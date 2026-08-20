"""Analytics and reporting API routes"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from database import get_db
from models import SessionModel, SessionMetric, Report, Decision, Intervention
from schemas import DashboardStats, WellnessTrend, ReportRequest, ReportResponse
from auth import get_current_user
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])


@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get dashboard statistics for user
    """
    user_id = current_user["user_id"]
    
    # Total sessions
    total_sessions = db.query(func.count(SessionModel.id)).filter(
        SessionModel.user_id == user_id
    ).scalar() or 0
    
    # Total duration
    total_duration = db.query(func.sum(SessionModel.duration_seconds)).filter(
        SessionModel.user_id == user_id
    ).scalar() or 0
    
    # Average burnout risk
    avg_burnout = db.query(func.avg(SessionModel.max_burnout_risk)).filter(
        SessionModel.user_id == user_id
    ).scalar() or 0
    
    # Active sessions today
    today = datetime.utcnow().date()
    active_today = db.query(func.count(SessionModel.id)).filter(
        (SessionModel.user_id == user_id) &
        (func.date(SessionModel.started_at) == today)
    ).scalar() or 0
    
    # Total interventions
    total_interventions = db.query(func.count(Intervention.id)).join(
        SessionModel
    ).filter(SessionModel.user_id == user_id).scalar() or 0
    
    # Average effectiveness
    avg_effectiveness = db.query(func.avg(Intervention.effectiveness_rating)).join(
        SessionModel
    ).filter(
        (SessionModel.user_id == user_id) &
        (Intervention.effectiveness_rating.isnot(None))
    ).scalar() or 0
    
    # Last session
    last_session = db.query(SessionModel).filter(
        SessionModel.user_id == user_id
    ).order_by(desc(SessionModel.started_at)).first()
    
    # Determine trend (improving, stable, declining)
    last_week = datetime.utcnow() - timedelta(days=7)
    this_week = db.query(func.avg(SessionModel.max_burnout_risk)).filter(
        (SessionModel.user_id == user_id) &
        (SessionModel.started_at >= last_week)
    ).scalar() or 0
    
    two_weeks_ago = datetime.utcnow() - timedelta(days=14)
    last_week_data = db.query(func.avg(SessionModel.max_burnout_risk)).filter(
        (SessionModel.user_id == user_id) &
        (SessionModel.started_at >= two_weeks_ago) &
        (SessionModel.started_at < last_week)
    ).scalar() or 0
    
    if this_week < last_week_data - 5:
        trend = "improving"
    elif this_week > last_week_data + 5:
        trend = "declining"
    else:
        trend = "stable"
    
    return DashboardStats(
        total_sessions=total_sessions,
        total_duration_hours=round(total_duration / 3600, 2),
        avg_burnout_risk=round(avg_burnout, 2),
        current_trend=trend,
        active_sessions_today=active_today,
        total_interventions=total_interventions,
        avg_effectiveness=round(avg_effectiveness, 2),
        last_session=last_session.started_at if last_session else None
    )


@router.get("/wellness-trends", response_model=list[WellnessTrend])
async def get_wellness_trends(
    current_user: dict = Depends(get_current_user),
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db)
):
    """
    Get wellness trends for last N days
    """
    user_id = current_user["user_id"]
    start_date = datetime.utcnow() - timedelta(days=days)
    
    sessions = db.query(SessionModel).filter(
        (SessionModel.user_id == user_id) &
        (SessionModel.started_at >= start_date)
    ).all()
    
    # Group by date and aggregate
    trends_by_date = {}
    
    for session in sessions:
        date = session.started_at.date()
        if date not in trends_by_date:
            trends_by_date[date] = {
                "burnout_risks": [],
                "stress_levels": [],
                "fatigues": [],
                "engagements": [],
                "session_count": 0
            }
        
        trends_by_date[date]["burnout_risks"].append(session.max_burnout_risk or 0)
        trends_by_date[date]["stress_levels"].append(session.avg_stress_level or 0)
        trends_by_date[date]["fatigues"].append(session.avg_fatigue or 0)
        trends_by_date[date]["engagements"].append(session.avg_engagement or 0)
        trends_by_date[date]["session_count"] += 1
    
    # Create trend objects
    trends = []
    for date in sorted(trends_by_date.keys()):
        data = trends_by_date[date]
        trends.append(WellnessTrend(
            date=datetime.combine(date, datetime.min.time()),
            burnout_risk=round(sum(data["burnout_risks"]) / len(data["burnout_risks"]), 2),
            stress_level=round(sum(data["stress_levels"]) / len(data["stress_levels"]), 2),
            fatigue=round(sum(data["fatigues"]) / len(data["fatigues"]), 2),
            engagement=round(sum(data["engagements"]) / len(data["engagements"]), 2),
            session_count=data["session_count"]
        ))
    
    return trends


@router.post("/reports", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def generate_report(
    report_request: ReportRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate wellness report for date range
    """
    try:
        # Get sessions in range
        sessions = db.query(SessionModel).filter(
            (SessionModel.user_id == current_user["user_id"]) &
            (SessionModel.started_at >= report_request.start_date) &
            (SessionModel.started_at <= report_request.end_date)
        ).all()
        
        if not sessions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No sessions found in date range"
            )
        
        # Calculate aggregates
        total_duration = sum(s.duration_seconds or 0 for s in sessions)
        avg_burnout = sum(s.max_burnout_risk or 0 for s in sessions) / len(sessions)
        avg_stress = sum(s.avg_stress_level or 0 for s in sessions) / len(sessions)
        
        # Determine trend
        if len(sessions) >= 2:
            first_half_avg = sum(s.max_burnout_risk or 0 for s in sessions[:len(sessions)//2]) / (len(sessions)//2)
            second_half_avg = sum(s.max_burnout_risk or 0 for s in sessions[len(sessions)//2:]) / (len(sessions) - len(sessions)//2)
            
            if second_half_avg < first_half_avg - 5:
                trend = "improving"
            elif second_half_avg > first_half_avg + 5:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "stable"
        
        # Get interventions in range
        interventions = db.query(Intervention).join(SessionModel).filter(
            (SessionModel.user_id == current_user["user_id"]) &
            (Intervention.timestamp >= report_request.start_date) &
            (Intervention.timestamp <= report_request.end_date)
        ).all()
        
        # Create report
        report = Report(
            user_id=current_user["user_id"],
            title=f"{report_request.report_type.capitalize()} Report",
            report_type=report_request.report_type,
            start_date=report_request.start_date,
            end_date=report_request.end_date,
            total_sessions=len(sessions),
            total_duration_minutes=int(total_duration / 60),
            avg_burnout_risk=round(avg_burnout, 2),
            avg_stress_level=round(avg_stress, 2),
            burnout_trend=trend,
            total_interventions=len(interventions),
            file_format=report_request.file_format,
            is_generated=True,
            generated_at=datetime.utcnow()
        )
        
        db.add(report)
        db.commit()
        db.refresh(report)
        
        logger.info(f"Report generated: {report.id} for user {current_user['user_id']}")
        return report
    
    except Exception as e:
        db.rollback()
        logger.error(f"Report generation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate report"
        )


@router.get("/reports", response_model=list[ReportResponse])
async def list_reports(
    current_user: dict = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    List generated reports for user
    """
    reports = db.query(Report).filter(
        Report.user_id == current_user["user_id"]
    ).order_by(desc(Report.generated_at)).offset(skip).limit(limit).all()
    
    return reports
