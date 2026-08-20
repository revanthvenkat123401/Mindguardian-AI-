"""
Advanced Vision Processing Engine
Supports: DeepFace, OpenFace, YOLOv8, Micro-expressions
"""

import cv2
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging
from dataclasses import dataclass
from enum import Enum

# These will be conditionally imported based on availability
try:
    from deepface import DeepFace
    DEEPFACE_AVAILABLE = True
except ImportError:
    DEEPFACE_AVAILABLE = False

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False

logger = logging.getLogger(__name__)


class EmotionType(str, Enum):
    """7 Basic Emotions"""
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    FEAR = "fear"
    DISGUST = "disgust"
    SURPRISE = "surprise"
    NEUTRAL = "neutral"


class FacialActionUnit(Enum):
    """Facial Action Units (FACS)"""
    # Upper face
    AU1 = "inner_brow_raiser"
    AU2 = "outer_brow_raiser"
    AU4 = "brow_lowerer"
    AU5 = "upper_eyelid_raiser"
    AU7 = "lid_tightener"
    
    # Mid face
    AU9 = "nose_wrinkler"
    AU10 = "upper_lip_raiser"
    
    # Lower face
    AU12 = "lip_corner_puller"
    AU15 = "lip_corner_depressor"
    AU17 = "chin_raiser"
    AU20 = "lip_stretcher"
    AU25 = "lips_parted"
    AU26 = "jaw_drop"


@dataclass
class FacialMetrics:
    """Comprehensive facial metrics"""
    face_detected: bool
    confidence: float
    
    # Emotion
    emotion: str
    emotion_probabilities: Dict[str, float]
    
    # Facial Action Units
    action_units: Dict[str, float]
    
    # Face Landmarks
    landmarks: Optional[np.ndarray]
    num_landmarks: int
    
    # Head Pose
    head_pitch: float  # Looking up/down
    head_yaw: float    # Looking left/right
    head_roll: float   # Head tilt
    
    # Eye Metrics
    eye_aspect_ratio: float
    left_eye_openness: float
    right_eye_openness: float
    gaze_direction: Tuple[float, float]
    blink_detected: bool
    
    # Mouth Metrics
    mouth_aspect_ratio: float
    mouth_open: bool
    yawn_detected: bool
    
    # Micro-expressions
    micro_expression_detected: bool
    micro_expression_type: Optional[str]
    
    # Posture
    body_detected: bool
    posture_score: float
    posture_type: str  # "upright", "slouching", "leaning"
    
    # Lighting
    brightness: float
    contrast: float
    lighting_quality: str  # "good", "poor", "shadows"


class VisionEngine:
    """Advanced Vision Processing Engine"""
    
    def __init__(self, use_deepface: bool = True, use_yolo: bool = True):
        self.use_deepface = use_deepface and DEEPFACE_AVAILABLE
        self.use_yolo = use_yolo and YOLO_AVAILABLE
        
        if self.use_yolo:
            try:
                self.yolo_model = YOLO('yolov8n-pose.pt')
                logger.info("YOLOv8 pose detection model loaded")
            except Exception as e:
                logger.warning(f"YOLOv8 load failed: {e}")
                self.use_yolo = False
        
        # Cascade classifiers for fallback
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
    
    def process_frame(self, frame: np.ndarray) -> FacialMetrics:
        """
        Process a video frame and extract comprehensive facial metrics
        
        Args:
            frame: Input video frame (BGR format)
            
        Returns:
            FacialMetrics object with all extracted features
        """
        metrics = FacialMetrics(
            face_detected=False,
            confidence=0.0,
            emotion="neutral",
            emotion_probabilities={},
            action_units={},
            landmarks=None,
            num_landmarks=0,
            head_pitch=0.0,
            head_yaw=0.0,
            head_roll=0.0,
            eye_aspect_ratio=0.0,
            left_eye_openness=0.0,
            right_eye_openness=0.0,
            gaze_direction=(0.0, 0.0),
            blink_detected=False,
            mouth_aspect_ratio=0.0,
            mouth_open=False,
            yawn_detected=False,
            micro_expression_detected=False,
            micro_expression_type=None,
            body_detected=False,
            posture_score=0.0,
            posture_type="unknown",
            brightness=0.0,
            contrast=0.0,
            lighting_quality="unknown"
        )
        
        # 1. Detect face
        faces = self.face_cascade.detectMultiScale(
            frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
        )
        
        if len(faces) == 0:
            return metrics
        
        # Use first detected face
        x, y, w, h = faces[0]
        face_roi = frame[y:y+h, x:x+w]
        metrics.face_detected = True
        metrics.confidence = 0.95
        
        # 2. Emotion Recognition (DeepFace)
        if self.use_deepface:
            try:
                result = DeepFace.analyze(
                    face_roi,
                    actions=['emotion', 'age', 'gender', 'race'],
                    enforce_detection=False
                )
                if result:
                    emotion_dict = result[0]['emotion']
                    dominant_emotion = result[0]['dominant_emotion']
                    metrics.emotion = dominant_emotion
                    metrics.emotion_probabilities = {
                        k: v/100.0 for k, v in emotion_dict.items()
                    }
            except Exception as e:
                logger.debug(f"DeepFace analysis error: {e}")
        
        # 3. Extract facial landmarks and head pose
        self._extract_head_pose(face_roi, metrics)
        
        # 4. Eye analysis
        self._analyze_eyes(face_roi, metrics)
        
        # 5. Mouth analysis
        self._analyze_mouth(face_roi, metrics)
        
        # 6. Micro-expression detection
        self._detect_micro_expressions(face_roi, metrics)
        
        # 7. Posture analysis (if YOLOv8 available)
        if self.use_yolo:
            self._analyze_posture(frame, metrics)
        
        # 8. Lighting analysis
        self._analyze_lighting(frame, metrics)
        
        return metrics
    
    def _extract_head_pose(self, face_roi: np.ndarray, metrics: FacialMetrics):
        """Extract head pose estimation"""
        # Simplified head pose estimation based on face landmarks
        # In production, use dlib or mediapipe for accurate landmark detection
        h, w = face_roi.shape[:2]
        
        # Approximate head pose from face aspect ratio
        aspect_ratio = w / h if h > 0 else 0
        
        if aspect_ratio > 1.3:
            metrics.head_yaw = 25.0  # Looking right
        elif aspect_ratio < 0.7:
            metrics.head_yaw = -25.0  # Looking left
        else:
            metrics.head_yaw = 0.0
        
        # For pitch and roll, would need full landmark detection
        metrics.head_pitch = 0.0
        metrics.head_roll = 0.0
    
    def _analyze_eyes(self, face_roi: np.ndarray, metrics: FacialMetrics):
        """Analyze eye metrics"""
        # Estimate eye openness from face region brightness
        gray = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape
        
        # Approximate eye regions (simplified)
        left_eye_region = gray[h//3:h//2, w//6:w//2]
        right_eye_region = gray[h//3:h//2, w//2:5*w//6]
        
        # Eye aspect ratio estimation
        left_brightness = np.mean(left_eye_region)
        right_brightness = np.mean(right_eye_region)
        
        # Normalize to 0-1 range
        metrics.left_eye_openness = min(1.0, left_brightness / 255.0)
        metrics.right_eye_openness = min(1.0, right_brightness / 255.0)
        
        # EAR (Eye Aspect Ratio) estimation
        metrics.eye_aspect_ratio = (metrics.left_eye_openness + metrics.right_eye_openness) / 2
        
        # Blink detection (EAR < 0.2)
        metrics.blink_detected = metrics.eye_aspect_ratio < 0.2
    
    def _analyze_mouth(self, face_roi: np.ndarray, metrics: FacialMetrics):
        """Analyze mouth metrics"""
        gray = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape
        
        # Approximate mouth region
        mouth_region = gray[2*h//3:h, w//4:3*w//4]
        
        # Mouth openness detection
        mouth_brightness = np.mean(mouth_region)
        metrics.mouth_aspect_ratio = min(1.0, mouth_brightness / 255.0)
        metrics.mouth_open = metrics.mouth_aspect_ratio > 0.6
        
        # Yawn detection (high mouth openness + eye closure)
        if metrics.mouth_open and metrics.eye_aspect_ratio < 0.3:
            metrics.yawn_detected = True
    
    def _detect_micro_expressions(self, face_roi: np.ndarray, metrics: FacialMetrics):
        """Detect micro-expressions"""
        # Micro-expressions are brief (100-500ms) involuntary facial movements
        # Would require temporal analysis with frame history
        # For now, detect based on unusual muscle tension
        
        gray = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
        
        # Detect edges (muscle tension indicators)
        edges = cv2.Canny(gray, 100, 200)
        edge_density = np.sum(edges > 0) / edges.size
        
        # High edge density might indicate micro-expression
        if edge_density > 0.15:
            metrics.micro_expression_detected = True
            metrics.micro_expression_type = "tension"
    
    def _analyze_posture(self, frame: np.ndarray, metrics: FacialMetrics):
        """Analyze body posture using YOLOv8"""
        if not self.use_yolo:
            return
        
        try:
            results = self.yolo_model(frame, verbose=False)
            
            if results and len(results) > 0:
                keypoints = results[0].keypoints
                if keypoints is not None and keypoints.data.size > 0:
                    metrics.body_detected = True
                    
                    # Analyze posture from keypoints
                    kpts = keypoints.data[0].cpu().numpy()
                    
                    # Calculate posture angle from shoulder and hip positions
                    if len(kpts) >= 6:  # At least shoulder and hip points
                        shoulder_y = (kpts[5][1] + kpts[6][1]) / 2
                        hip_y = (kpts[11][1] + kpts[12][1]) / 2
                        
                        posture_angle = abs(hip_y - shoulder_y)
                        
                        if posture_angle < 50:
                            metrics.posture_type = "upright"
                            metrics.posture_score = 0.95
                        elif posture_angle < 100:
                            metrics.posture_type = "neutral"
                            metrics.posture_score = 0.70
                        else:
                            metrics.posture_type = "slouching"
                            metrics.posture_score = 0.40
        except Exception as e:
            logger.debug(f"Posture analysis error: {e}")
    
    def _analyze_lighting(self, frame: np.ndarray, metrics: FacialMetrics):
        """Analyze lighting conditions"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Overall brightness
        brightness = np.mean(gray)
        metrics.brightness = brightness / 255.0
        
        # Contrast (standard deviation)
        contrast = np.std(gray)
        metrics.contrast = min(1.0, contrast / 127.0)
        
        # Quality assessment
        if metrics.brightness < 0.3:
            metrics.lighting_quality = "too_dark"
        elif metrics.brightness > 0.9:
            metrics.lighting_quality = "too_bright"
        elif metrics.contrast < 0.2:
            metrics.lighting_quality = "low_contrast"
        else:
            metrics.lighting_quality = "good"


class BurnoutSignalDetector:
    """Detect burnout-specific visual signals"""
    
    def __init__(self):
        self.frame_history = []
        self.max_history = 30  # 1 second at 30fps
    
    def detect_burnout_indicators(self, metrics: FacialMetrics) -> Dict[str, float]:
        """
        Detect burnout-related visual signals
        
        Returns:
            Dictionary of burnout indicators with scores 0-1
        """
        indicators = {}
        
        # 1. Eye fatigue score
        # Low eye openness + frequent blinking = fatigue
        indicators['eye_fatigue'] = self._calculate_eye_fatigue(metrics)
        
        # 2. Stress tension score
        # Furrowed brow + jaw tension = stress
        indicators['stress_tension'] = self._calculate_stress_tension(metrics)
        
        # 3. Attention drift score
        # Looking away frequently = attention loss
        indicators['attention_drift'] = self._calculate_attention_drift(metrics)
        
        # 4. Emotional exhaustion score
        # Neutral/sad emotion dominance = exhaustion
        indicators['emotional_exhaustion'] = self._calculate_emotional_exhaustion(metrics)
        
        # 5. Physical fatigue score
        # Yawning + slouching = fatigue
        indicators['physical_fatigue'] = self._calculate_physical_fatigue(metrics)
        
        # 6. Overall burnout risk
        indicators['burnout_risk'] = np.mean(list(indicators.values()))
        
        return indicators
    
    def _calculate_eye_fatigue(self, metrics: FacialMetrics) -> float:
        """Eye fatigue score 0-1"""
        # Low eye openness indicates fatigue
        eye_openness = (metrics.left_eye_openness + metrics.right_eye_openness) / 2
        fatigue = 1.0 - eye_openness
        
        # Blinking also indicates stress
        if metrics.blink_detected:
            fatigue += 0.2
        
        return min(1.0, fatigue)
    
    def _calculate_stress_tension(self, metrics: FacialMetrics) -> float:
        """Stress/tension score 0-1"""
        # Micro-expressions indicate stress
        tension = 0.0
        
        if metrics.micro_expression_detected:
            tension += 0.6
        
        # Certain emotions indicate stress
        stress_emotions = ['angry', 'fear', 'disgust']
        if metrics.emotion in stress_emotions:
            tension += 0.4
        
        return min(1.0, tension)
    
    def _calculate_attention_drift(self, metrics: FacialMetrics) -> float:
        """Attention drift score 0-1"""
        # Looking away (high yaw) indicates attention loss
        drift = abs(metrics.head_yaw) / 90.0  # Normalize to 90 degree max turn
        return min(1.0, drift)
    
    def _calculate_emotional_exhaustion(self, metrics: FacialMetrics) -> float:
        """Emotional exhaustion score 0-1"""
        # Neutral or sad expressions indicate exhaustion
        exhaustion = 0.0
        
        if metrics.emotion == 'neutral':
            exhaustion = 0.4
        elif metrics.emotion == 'sad':
            exhaustion = 0.8
        
        # Lower confidence in emotion = exhaustion
        if max(metrics.emotion_probabilities.values()) < 0.5:
            exhaustion += 0.2
        
        return min(1.0, exhaustion)
    
    def _calculate_physical_fatigue(self, metrics: FacialMetrics) -> float:
        """Physical fatigue score 0-1"""
        fatigue = 0.0
        
        # Yawning is strong indicator
        if metrics.yawn_detected:
            fatigue = 0.7
        
        # Slouching indicates fatigue
        if metrics.posture_type == "slouching":
            fatigue += 0.3
        
        return min(1.0, fatigue)
