"""SQLAlchemy models for MindGuardian AI"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON, ForeignKey, Text, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()


class User(Base):
    """User model for authentication and profile management"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    avatar_url = Column(String(255), nullable=True)
    
    # Privacy settings
    data_retention_days = Column(Integer, default=90)
    auto_delete_enabled = Column(Boolean, default=True)
    allow_data_export = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    preferences = relationship("UserPreferences", back_populates="user", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User {self.username}>"


class UserPreferences(Base):
    """User preferences and settings"""
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    
    # Notification settings
    notifications_enabled = Column(Boolean, default=True)
    email_alerts = Column(Boolean, default=False)
    alert_threshold = Column(Integer, default=70)  # Burnout risk threshold
    
    # Display preferences
    theme = Column(String(20), default="light")  # light/dark
    language = Column(String(10), default="en")
    timezone = Column(String(50), default="UTC")
    
    # Privacy settings
    share_anonymous_data = Column(Boolean, default=False)
    
    # Session settings
    session_duration_minutes = Column(Integer, default=25)  # Pomodoro-like default
    auto_start_next_session = Column(Boolean, default=False)
    
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="preferences")
    
    def __repr__(self):
        return f"<UserPreferences user_id={self.user_id}>"


class SessionState(str, enum.Enum):
    """Session state enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class Session(Base):
    """Monitoring session model"""
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    
    # Session metadata
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    activity_type = Column(String(50), default="general")  # coding, studying, meeting, etc.
    
    # Session timing
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, default=0)
    
    # Session state
    state = Column(Enum(SessionState), default=SessionState.PENDING, index=True)
    is_active = Column(Boolean, default=True, index=True)
    
    # Aggregated metrics (calculated at session end)
    avg_cognitive_load = Column(Float, nullable=True)
    avg_stress_level = Column(Float, nullable=True)
    avg_fatigue = Column(Float, nullable=True)
    avg_engagement = Column(Float, nullable=True)
    max_burnout_risk = Column(Float, nullable=True)
    
    # Session summary
    total_frames = Column(Integer, default=0)
    data_quality = Column(Float, default=0.0)  # 0-100
    notes = Column(Text, nullable=True)
    
    # Privacy flags
    is_archived = Column(Boolean, default=False)
    marked_for_deletion = Column(Boolean, default=False)
    deletion_scheduled_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    metrics = relationship("SessionMetric", back_populates="session", cascade="all, delete-orphan")
    decisions = relationship("Decision", back_populates="session", cascade="all, delete-orphan")
    interventions = relationship("Intervention", back_populates="session", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Session {self.id}: {self.title}>"


class SessionMetric(Base):
    """Real-time metrics collected during a session"""
    __tablename__ = "session_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id", ondelete="CASCADE"), index=True)
    
    # Timestamp
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    frame_index = Column(Integer)  # Frame number in session
    
    # Vision metrics
    face_detected = Column(Boolean)
    expression = Column(String(20))  # happy, neutral, stressed
    smile_score = Column(Float)
    blink_rate = Column(Float)
    eye_closure = Column(Float)  # 0-100
    head_pitch = Column(Float)
    head_yaw = Column(Float)
    head_roll = Column(Float)
    yawning = Column(Boolean)
    face_stability = Column(Float)  # 0-100
    
    # Audio metrics
    speaking = Column(Boolean)
    voice_energy = Column(Float)  # 0-100
    pitch = Column(Float)
    speech_rate = Column(Float)
    noise_level = Column(Float)  # 0-100
    audio_quality = Column(String(20))  # good, fair, poor
    
    # Fused metrics
    cognitive_load = Column(Float)
    stress_level = Column(Float)
    fatigue = Column(Float)
    engagement = Column(Float)
    burnout_risk = Column(Float)
    
    # Raw data (JSON for flexibility)
    vision_data = Column(JSON, nullable=True)
    audio_data = Column(JSON, nullable=True)
    
    # Relationships
    session = relationship("Session", back_populates="metrics")
    
    def __repr__(self):
        return f"<SessionMetric session_id={self.session_id} frame={self.frame_index}>"


class Decision(Base):
    """AI decisions and recommendations generated during sessions"""
    __tablename__ = "decisions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id", ondelete="CASCADE"), index=True)
    
    # Decision metadata
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    decision_type = Column(String(50))  # recommendation, alert, intervention
    
    # Decision content
    assessment = Column(Text)
    concern = Column(String(200))
    recommendation = Column(Text)
    reasoning = Column(Text)  # Why this recommendation was made
    
    # Decision metrics
    state = Column(String(20))  # HEALTHY, ALERT, WARNING, CRITICAL
    priority = Column(String(20))  # LOW, MEDIUM, HIGH, URGENT
    burnout_risk = Column(Float)
    confidence = Column(Float)  # 0-100
    recovery_time = Column(String(50))
    
    # LLM details
    llm_prompt = Column(Text, nullable=True)
    llm_response = Column(Text, nullable=True)
    inference_time_ms = Column(Integer, nullable=True)
    
    # User response
    user_acknowledged = Column(Boolean, default=False)
    acknowledged_at = Column(DateTime, nullable=True)
    user_feedback = Column(Text, nullable=True)
    
    # Relationships
    session = relationship("Session", back_populates="decisions")
    
    def __repr__(self):
        return f"<Decision session_id={self.session_id} type={self.decision_type}>"


class Intervention(Base):
    """Interventions executed during sessions"""
    __tablename__ = "interventions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id", ondelete="CASCADE"), index=True)
    decision_id = Column(Integer, ForeignKey("decisions.id"), nullable=True)
    
    # Intervention details
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    action_type = Column(String(50))  # break, breathe, move, hydrate, etc.
    action_description = Column(Text)
    reason = Column(String(200))
    
    # Execution
    was_executed = Column(Boolean, default=False)
    executed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    
    # Outcome
    effectiveness_rating = Column(Integer, nullable=True)  # 1-5 star rating
    user_feedback = Column(Text, nullable=True)
    
    # Impact metrics (before/after)
    metrics_before = Column(JSON, nullable=True)
    metrics_after = Column(JSON, nullable=True)
    
    # Relationships
    session = relationship("Session", back_populates="interventions")
    
    def __repr__(self):
        return f"<Intervention session_id={self.session_id} action={self.action_type}>"


class Report(Base):
    """Generated reports and exports"""
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    
    # Report metadata
    title = Column(String(200))
    report_type = Column(String(50))  # daily, weekly, monthly, session_summary
    
    # Report scope
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    total_sessions = Column(Integer)
    total_duration_minutes = Column(Integer)
    
    # Report summary
    avg_burnout_risk = Column(Float)
    avg_stress_level = Column(Float)
    avg_fatigue = Column(Float)
    avg_engagement = Column(Float)
    
    # Trends
    burnout_trend = Column(String(20))  # improving, stable, declining
    total_interventions = Column(Integer)
    
    # File storage
    file_path = Column(String(500), nullable=True)
    file_format = Column(String(20))  # pdf, json, csv
    file_size = Column(Integer, nullable=True)  # bytes
    
    # Report status
    is_generated = Column(Boolean, default=False)
    generated_at = Column(DateTime, nullable=True)
    
    # Privacy
    is_archived = Column(Boolean, default=False)
    marked_for_deletion = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Report {self.id}: {self.title}>"
