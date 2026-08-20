"""Decision and intervention API routes"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from database import get_db
from models import Decision, Intervention, SessionModel
from schemas import DecisionResponse, InterventionResponse, InterventionFeedback
from auth import get_current_user
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/decisions", tags=["decisions"])


@router.get("", response_model=list[DecisionResponse])
async def list_decisions(
    current_user: dict = Depends(get_current_user),
    session_id: int = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    List decisions for user (optionally filtered by session)
    """
    query = db.query(Decision).join(
        SessionModel,
        SessionModel.id == Decision.session_id
    ).filter(SessionModel.user_id == current_user["user_id"])
    
    if session_id:
        query = query.filter(Decision.session_id == session_id)
    
    decisions = query.order_by(desc(Decision.timestamp)).offset(skip).limit(limit).all()
    return decisions


@router.get("/{decision_id}", response_model=DecisionResponse)
async def get_decision(
    decision_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get specific decision details
    """
    decision = db.query(Decision).join(
        SessionModel,
        SessionModel.id == Decision.session_id
    ).filter(
        (Decision.id == decision_id) &
        (SessionModel.user_id == current_user["user_id"])
    ).first()
    
    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )
    
    return decision


@router.post("/{decision_id}/acknowledge")
async def acknowledge_decision(
    decision_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark decision as acknowledged by user
    """
    decision = db.query(Decision).join(
        SessionModel,
        SessionModel.id == Decision.session_id
    ).filter(
        (Decision.id == decision_id) &
        (SessionModel.user_id == current_user["user_id"])
    ).first()
    
    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )
    
    decision.user_acknowledged = True
    decision.acknowledged_at = datetime.utcnow()
    db.commit()
    
    logger.info(f"Decision acknowledged: {decision_id}")
    return {"message": "Decision acknowledged"}


@router.post("/{decision_id}/feedback")
async def provide_decision_feedback(
    decision_id: int,
    feedback: InterventionFeedback,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Provide feedback on a decision
    """
    decision = db.query(Decision).join(
        SessionModel,
        SessionModel.id == Decision.session_id
    ).filter(
        (Decision.id == decision_id) &
        (SessionModel.user_id == current_user["user_id"])
    ).first()
    
    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Decision not found"
        )
    
    decision.user_feedback = feedback.user_feedback
    db.commit()
    
    logger.info(f"Feedback provided for decision: {decision_id}")
    return {"message": "Feedback recorded"}


# Interventions routes
@router.get("/interventions", response_model=list[InterventionResponse])
async def list_interventions(
    current_user: dict = Depends(get_current_user),
    session_id: int = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    List interventions for user (optionally filtered by session)
    """
    query = db.query(Intervention).join(
        SessionModel,
        SessionModel.id == Intervention.session_id
    ).filter(SessionModel.user_id == current_user["user_id"])
    
    if session_id:
        query = query.filter(Intervention.session_id == session_id)
    
    interventions = query.order_by(desc(Intervention.timestamp)).offset(skip).limit(limit).all()
    return interventions


@router.post("/{intervention_id}/execute")
async def execute_intervention(
    intervention_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark intervention as executed
    """
    intervention = db.query(Intervention).join(
        SessionModel,
        SessionModel.id == Intervention.session_id
    ).filter(
        (Intervention.id == intervention_id) &
        (SessionModel.user_id == current_user["user_id"])
    ).first()
    
    if not intervention:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Intervention not found"
        )
    
    intervention.was_executed = True
    intervention.executed_at = datetime.utcnow()
    db.commit()
    
    logger.info(f"Intervention executed: {intervention_id}")
    return {"message": "Intervention marked as executed"}


@router.post("/{intervention_id}/feedback")
async def provide_intervention_feedback(
    intervention_id: int,
    feedback: InterventionFeedback,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Provide feedback on intervention effectiveness
    """
    intervention = db.query(Intervention).join(
        SessionModel,
        SessionModel.id == Intervention.session_id
    ).filter(
        (Intervention.id == intervention_id) &
        (SessionModel.user_id == current_user["user_id"])
    ).first()
    
    if not intervention:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Intervention not found"
        )
    
    intervention.effectiveness_rating = feedback.effectiveness_rating
    intervention.user_feedback = feedback.user_feedback
    db.commit()
    
    logger.info(f"Feedback provided for intervention: {intervention_id}")
    return {"message": "Feedback recorded"}
