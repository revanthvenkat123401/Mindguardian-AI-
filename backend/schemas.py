"""Pydantic schemas for request/response validation"""
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum


# ============ User Schemas ============

class UserBase(BaseModel):
    """Base user schema"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """Schema for user creation"""
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """Schema for user updates"""
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None


class UserResponse(UserBase):
    """Schema for user response"""
    id: int
    avatar_url: Optional[str]
    data_retention_days: int
    created_at: datetime
    last_login: Optional[datetime]
    
    class Config:
        from_attributes = True


# ============ Session Schemas ============

class SessionCreate(BaseModel):
    """Schema for creating a session"""
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    activity_type: str = Field(default="general")


class SessionUpdate(BaseModel):
    """Schema for updating a session"""
    title: Optional[str] = None
    description: Optional[str] = None
    notes: Optional[str] = None


class SessionResponse(BaseModel):
    """Schema for session response"""
    id: int
    title: str
    description: Optional[str]
    activity_type: str
    state: str
    duration_seconds: int
    avg_cognitive_load: Optional[float]
    avg_stress_level: Optional[float]
    avg_fatigue: Optional[float]
    avg_engagement: Optional[float]
    max_burnout_risk: Optional[float]
    data_quality: float
    started_at: datetime
    ended_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============ Metrics Schemas ============

class MetricsBase(BaseModel):
    """Base metrics schema"""
    face_detected: bool
    expression: Optional[str]
    smile_score: Optional[float]
    blink_rate: Optional[float]
    eye_closure: Optional[float]
    head_pitch: Optional[float]
    head_yaw: Optional[float]
    head_roll: Optional[float]
    yawning: Optional[bool]
    speaking: Optional[bool]
    voice_energy: Optional[float]
    pitch: Optional[float]
    speech_rate: Optional[float]
    noise_level: Optional[float]
    cognitive_load: float
    stress_level: float
    fatigue: float
    engagement: float
    burnout_risk: float


class MetricsIngest(MetricsBase):
    """Schema for ingesting metrics from frontend"""
    session_id: int
    frame_index: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class MetricsResponse(MetricsBase):
    """Schema for metrics response"""
    id: int
    session_id: int
    frame_index: int
    timestamp: datetime
    
    class Config:
        from_attributes = True


# ============ Decision Schemas ============

class DecisionResponse(BaseModel):
    """Schema for decision response"""
    id: int
    session_id: int
    timestamp: datetime
    decision_type: str
    assessment: str
    concern: str
    recommendation: str
    state: str
    priority: str
    burnout_risk: float
    confidence: float
    recovery_time: str
    user_acknowledged: bool
    
    class Config:
        from_attributes = True


# ============ Intervention Schemas ============

class InterventionResponse(BaseModel):
    """Schema for intervention response"""
    id: int
    session_id: int
    timestamp: datetime
    action_type: str
    action_description: str
    reason: str
    was_executed: bool
    executed_at: Optional[datetime]
    effectiveness_rating: Optional[int]
    
    class Config:
        from_attributes = True


class InterventionFeedback(BaseModel):
    """Schema for intervention feedback"""
    effectiveness_rating: int = Field(..., ge=1, le=5)
    user_feedback: Optional[str] = None


# ============ Report Schemas ============

class ReportRequest(BaseModel):
    """Schema for report generation request"""
    report_type: str  # daily, weekly, monthly
    start_date: datetime
    end_date: datetime
    file_format: str = "pdf"  # pdf, json, csv


class ReportResponse(BaseModel):
    """Schema for report response"""
    id: int
    title: str
    report_type: str
    start_date: datetime
    end_date: datetime
    total_sessions: int
    avg_burnout_risk: float
    avg_stress_level: float
    burnout_trend: str
    total_interventions: int
    is_generated: bool
    generated_at: Optional[datetime]
    file_format: str
    
    class Config:
        from_attributes = True


# ============ Authentication Schemas ============

class LoginRequest(BaseModel):
    """Schema for login request"""
    username: str
    password: str


class TokenResponse(BaseModel):
    """Schema for token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


# ============ Analytics Schemas ============

class DashboardStats(BaseModel):
    """Schema for dashboard statistics"""
    total_sessions: int
    total_duration_hours: float
    avg_burnout_risk: float
    current_trend: str  # improving, stable, declining
    active_sessions_today: int
    total_interventions: int
    avg_effectiveness: float
    last_session: Optional[datetime]


class WellnessTrend(BaseModel):
    """Schema for wellness trends"""
    date: datetime
    burnout_risk: float
    stress_level: float
    fatigue: float
    engagement: float
    session_count: int


# ============ Privacy Schemas ============

class PrivacySettings(BaseModel):
    """Schema for privacy settings"""
    data_retention_days: int = Field(..., ge=1, le=365)
    auto_delete_enabled: bool = True
    allow_data_export: bool = True


class DataExportRequest(BaseModel):
    """Schema for data export request"""
    export_format: str = "json"  # json, csv, pdf
    include_sessions: bool = True
    include_metrics: bool = True
    include_decisions: bool = True
    include_interventions: bool = True
