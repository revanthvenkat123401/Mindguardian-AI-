"""Session management API routes"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from database import get_db
from models import Session as SessionModel, SessionMetric, Decision, SessionState
from schemas import SessionCreate, SessionResponse, SessionUpdate, MetricsIngest, MetricsResponse
from auth import get_current_user
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/sessions", tags=["sessions"])


@router.post("/start", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def start_session(
    session_data: SessionCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Start a new monitoring session
    """
    try:
        new_session = SessionModel(
            user_id=current_user["user_id"],
            title=session_data.title,
            description=session_data.description,
            activity_type=session_data.activity_type,
            state=SessionState.RUNNING,
            started_at=datetime.utcnow()
        )
        db.add(new_session)
        db.commit()
        db.refresh(new_session)
        
        logger.info(f"Session started: {new_session.id} for user {current_user['user_id']}")
        return new_session
    
    except Exception as e:
        db.rollback()
        logger.error(f"Session start error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start session"
        )


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get session details
    """
    session = db.query(SessionModel).filter(
        (SessionModel.id == session_id) &
        (SessionModel.user_id == current_user["user_id"])
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    return session


@router.get("", response_model=list[SessionResponse])
async def list_sessions(
    current_user: dict = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    state: str = Query(None),
    db: Session = Depends(get_db)
):
    """
    List user sessions with pagination and filtering
    """
    query = db.query(SessionModel).filter(
        SessionModel.user_id == current_user["user_id"]
    )
    
    # Filter by state if provided
    if state:
        query = query.filter(SessionModel.state == state)
    
    sessions = query.order_by(desc(SessionModel.started_at)).offset(skip).limit(limit).all()
    return sessions


@router.post("/{session_id}/metrics", response_model=MetricsResponse, status_code=status.HTTP_201_CREATED)
async def ingest_metrics(
    session_id: int,
    metrics: MetricsIngest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Ingest real-time metrics from frontend
    
    Called frequently (multiple times per second) during active sessions
    """
    # Verify session belongs to user
    session = db.query(SessionModel).filter(
        (SessionModel.id == session_id) &
        (SessionModel.user_id == current_user["user_id"])
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    if session.state != SessionState.RUNNING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session is not active"
        )
    
    try:
        metric = SessionMetric(
            session_id=session_id,
            frame_index=metrics.frame_index,
            timestamp=metrics.timestamp,
            face_detected=metrics.face_detected,
            expression=metrics.expression,
            smile_score=metrics.smile_score,
            blink_rate=metrics.blink_rate,
            eye_closure=metrics.eye_closure,
            head_pitch=metrics.head_pitch,
            head_yaw=metrics.head_yaw,
            head_roll=metrics.head_roll,
            yawning=metrics.yawning,
            speaking=metrics.speaking,
            voice_energy=metrics.voice_energy,
            pitch=metrics.pitch,
            speech_rate=metrics.speech_rate,
            noise_level=metrics.noise_level,
            cognitive_load=metrics.cognitive_load,
            stress_level=metrics.stress_level,
            fatigue=metrics.fatigue,
            engagement=metrics.engagement,
            burnout_risk=metrics.burnout_risk
        )
        db.add(metric)
        db.commit()
        db.refresh(metric)
        
        return metric
    
    except Exception as e:
        db.rollback()
        logger.error(f"Metrics ingestion error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to ingest metrics"
        )


@router.post("/{session_id}/end", response_model=SessionResponse)
async def end_session(
    session_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    End a session and calculate aggregated metrics
    """
    session = db.query(SessionModel).filter(
        (SessionModel.id == session_id) &
        (SessionModel.user_id == current_user["user_id"])
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    try:
        # Calculate aggregated metrics
        metrics = db.query(SessionMetric).filter(
            SessionMetric.session_id == session_id
        ).all()
        
        if metrics:
            session.total_frames = len(metrics)
            session.avg_cognitive_load = sum(m.cognitive_load for m in metrics) / len(metrics)
            session.avg_stress_level = sum(m.stress_level for m in metrics) / len(metrics)
            session.avg_fatigue = sum(m.fatigue for m in metrics) / len(metrics)
            session.avg_engagement = sum(m.engagement for m in metrics) / len(metrics)
            session.max_burnout_risk = max(m.burnout_risk for m in metrics)
            
            # Calculate data quality
            face_detected_count = sum(1 for m in metrics if m.face_detected)
            session.data_quality = (face_detected_count / len(metrics)) * 100
        
        # Update session state
        session.ended_at = datetime.utcnow()
        session.state = SessionState.COMPLETED
        session.duration_seconds = int(
            (session.ended_at - session.started_at).total_seconds()
        )
        
        db.commit()
        db.refresh(session)
        
        logger.info(f"Session ended: {session_id}")
        return session
    
    except Exception as e:
        db.rollback()
        logger.error(f"Session end error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to end session"
        )


@router.get("/{session_id}/metrics", response_model=list[MetricsResponse])
async def get_session_metrics(
    session_id: int,
    current_user: dict = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Get all metrics for a session
    """
    # Verify session
    session = db.query(SessionModel).filter(
        (SessionModel.id == session_id) &
        (SessionModel.user_id == current_user["user_id"])
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    metrics = db.query(SessionMetric).filter(
        SessionMetric.session_id == session_id
    ).order_by(SessionMetric.frame_index).offset(skip).limit(limit).all()
    
    return metrics
