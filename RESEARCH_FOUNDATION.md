# MindGuardian AI - Research Foundation & Theoretical Framework

## 1. RESEARCH OBJECTIVES

### Primary Research Question
> **Can we develop a privacy-preserving, locally-processed multimodal AI system that reliably estimates cognitive fatigue and burnout risk without transmitting sensitive behavioral data to remote servers?**

### Secondary Research Questions
1. How accurately can webcam and microphone signals estimate cognitive load without external reference standards?
2. What is the optimal fusion strategy for multimodal cognitive indicators?
3. How do locally-processed signals compare to cloud-based alternatives in terms of accuracy and latency?
4. What are the privacy-utility tradeoffs in edge-based cognitive monitoring?

---

## 2. LITERATURE FOUNDATION

### Key Related Work

#### Cognitive Fatigue Detection
- **Electroencephalography (EEG)-based approaches**: Gevins & Cutillo (2007) - "Brain imaging of sustained attention"
- **Eye-tracking metrics**: Zhu et al. (2015) - "Eye tracking under natural conditions"
- **Facial expression analysis**: Ekman & Friesen (1978) - "The Facial Action Coding System (FACS)"

#### Multimodal Fusion for Cognitive Assessment
- **Multimodal learning**: Baltrušaitis et al. (2018) - "Multimodal Machine Learning: A Survey"
- **Audio-visual fusion**: Zadeh et al. (2018) - "CMU-MOSEI: A Multimodal Dataset for Sentiment Analysis"

#### Privacy-Preserving ML
- **Federated Learning**: McMahan et al. (2017) - "Communication-Efficient Learning of Deep Networks"
- **Local inference**: Ryffel et al. (2018) - "A Generic Framework for Interesting Subspace Cluster Detection"
- **Differential Privacy**: Dwork & Roth (2014) - "The Algorithmic Foundations of Differential Privacy"

#### Computer Vision for Behavioral Analysis
- **MediaPipe**: Lugaresi et al. (2019) - "MediaPipe: A Framework for Building Multimodal Machine Learning Pipelines"
- **Facial Action Units**: Fasel & Luettin (2003) - "Automatic facial expression analysis: a survey"

---

## 3. THEORETICAL FRAMEWORK

### Multimodal Cognitive Load Model

```
Cognitive State Estimation:
   C = f(V, A, T) where:
   
   V = Vision-based indicators:
      - Eye metrics (blink rate, pupil dilation)
      - Facial expressions (action units)
      - Head pose and posture
      - Gaze patterns
   
   A = Audio-based indicators:
      - Voice prosody (pitch, speech rate)
      - Speech energy and quality
      - Silence/pause patterns
      - Vocal effort indicators
   
   T = Temporal dynamics:
      - Fatigue accumulation over time
      - Attention drift patterns
      - Recovery indicators
   
   f = Fusion function (weighted combination with learned weights)
```

### Risk Assessment Pipeline

```
Signal → Feature Extraction → Feature Fusion → Risk Scoring → Decision
  |            ↓                    ↓                ↓            ↓
  |       [Vision Engine]    [Multimodal          [Thresholding  [Intervention
  |       [Audio Engine]      Fusion Net]          & Ranking]     Generation]
  |
  └─→ Local Processing (Privacy-First)
```

### Cognitive States Being Modeled

| State | Indicators | Risk Level |
|-------|-----------|-----------|
| **Engaged** | High eye contact, stable head, normal speech rate | Low |
| **Focused** | Sustained attention, minimal blinks, stable posture | Low |
| **Fatigued** | Increased blink rate, head drooping, slower speech | Medium |
| **Strained** | Tense expressions, irregular blinks, high stress markers | High |
| **Exhausted** | Eye closure patterns, slumped posture, monotone speech | Critical |

---

## 4. METHODOLOGY

### 4.1 Data Collection Protocol

#### For Validation Studies
1. **Participant Recruitment**
   - Age range: 18-65
   - Healthy volunteers
   - No neurological disorders
   - Informed consent + IRB approval required

2. **Study Design**
   - Randomized controlled trials (RCT)
   - Counterbalanced task order
   - Multiple task types (cognitive load levels)

3. **Ground Truth Collection**
   - Self-reported fatigue (Karolinska Sleepiness Scale)
   - Performance metrics (error rates, reaction time)
   - Optional: Physiological baseline (heart rate, if available)

#### Session Structure
```
Baseline (5 min) → Task Phase 1 (15 min) → Rest (5 min) → 
Task Phase 2 (25 min) → Assessment → Follow-up
```

### 4.2 Feature Engineering

#### Vision Pipeline Features
```python
vision_features = {
    "eye_metrics": ["blink_rate", "blink_duration", "pupil_size"],
    "facial_au": ["au1", "au4", "au7", "au12", "au15", "au25", "au26"],
    "head_pose": ["pitch_stability", "yaw_range", "roll_variance"],
    "expression": ["smile_score", "frown_score", "tension_score"],
    "attention": ["gaze_direction", "fixation_duration", "saccade_rate"]
}
```

#### Audio Pipeline Features
```python
audio_features = {
    "prosody": ["pitch_mean", "pitch_variance", "pitch_range"],
    "speech_rate": ["syllables_per_second", "pause_ratio"],
    "energy": ["rms_energy", "spectral_centroid", "mfcc_coefficients"],
    "voice_quality": ["jitter", "shimmer", "noise_ratio"]
}
```

#### Fusion Strategy
- **Early fusion**: Concatenate features before ML model
- **Late fusion**: Combine predictions from separate models
- **Hybrid fusion**: Selective fusion with learned attention weights

### 4.3 Validation Metrics

#### Classification Performance (for risk categories)
```
Metrics = [
    Accuracy, Precision, Recall, F1-Score,
    ROC-AUC, PR-AUC, Cohen's Kappa
]
```

#### Regression Performance (for continuous scores)
```
Metrics = [
    MAE (Mean Absolute Error),
    RMSE (Root Mean Squared Error),
    R² Score (Coefficient of Determination),
    Spearman Correlation with Ground Truth
]
```

#### Temporal Consistency
```
Metrics = [
    Autocorrelation within sessions,
    Stability over repeated measurements,
    Test-retest reliability (ICC)
]
```

---

## 5. MODEL ARCHITECTURE SPECIFICATION

### 5.1 Current Status
- Architecture designed but not fully implemented
- Placeholder for local SLM integration
- Feature fusion approach not yet specified

### 5.2 Proposed Implementation

#### Option A: Rule-Based + Statistical
- **Pros**: Interpretable, no data needed, fast
- **Cons**: Limited accuracy, hand-crafted rules
- **Use case**: MVP/prototyping

#### Option B: Traditional ML
- **Algorithms**: Random Forest, XGBoost, SVM
- **Pros**: Good accuracy, relatively fast, interpretable
- **Cons**: Manual feature engineering needed
- **Use case**: Production baseline

#### Option C: Deep Learning (Local)
- **Architecture**: Lightweight CNN for vision, LSTM for temporal
- **Pros**: Automatic feature learning, multimodal fusion
- **Cons**: Needs more data, less interpretable
- **Use case**: Advanced implementation

#### Option D: Small Language Models (SLM)
- **Models**: Ollama-compatible (Mistral, Phi, etc.)
- **Pros**: Reasoning capability, flexible
- **Cons**: Latency, higher compute
- **Use case**: Final decision rationale generation

**Recommendation for MVP**: Use Option B with Option A fallback

---

## 6. PRIVACY & SECURITY SPECIFICATION

### 6.1 Privacy Guarantees

#### Data Minimization
- ✅ Only process necessary signals (vision + audio)
- ✅ Extract features locally, discard raw signals
- ✅ Never transmit raw video/audio frames

#### Local Processing
- ✅ All ML inference happens on user's device
- ✅ Optional backend only stores aggregated metrics, not raw signals
- ✅ User can opt for fully offline mode

#### User Control
- ✅ Users can delete data at any time
- ✅ Configurable data retention policies
- ✅ Full data export in standard formats (JSON, CSV)
- ✅ Clear audit logs of access

### 6.2 Security Specifications

#### Encryption
```
At-rest: AES-256 for PostgreSQL (optional)
In-transit: HTTPS/TLS 1.3 minimum
Database: Encrypted sensitive fields
```

#### Authentication
```
JWT with RS256 (asymmetric signing)
Token expiration: 30 minutes
Refresh tokens: 7 days
Rate limiting: 5 failed attempts → 15 min lockout
```

#### Access Control
```
Role-Based Access Control (RBAC):
  - User (read own data)
  - Researcher (read anonymized data, with consent)
  - Admin (full access, audit trails)
```

---

## 7. EVALUATION PLAN

### Phase 1: Internal Validation (Week 1-4)
- [ ] Component testing (vision engine, audio engine)
- [ ] Integration testing (feature fusion)
- [ ] Edge case testing (low light, silence, etc.)

### Phase 2: Pilot Study (Week 5-12)
- [ ] Recruit 10-15 participants
- [ ] Conduct controlled task sessions
- [ ] Validate model predictions against ground truth
- [ ] Measure latency and compute usage

### Phase 3: Expanded Study (Week 13-20)
- [ ] 50-100 participants
- [ ] Diverse task types
- [ ] Multi-day tracking
- [ ] Cross-validation analysis

### Phase 4: Real-World Validation (Week 21+)
- [ ] Open deployment (beta)
- [ ] Monitor model performance
- [ ] Collect user feedback
- [ ] Publish preliminary findings

---

## 8. EXPECTED OUTCOMES & LIMITATIONS

### Expected Contributions
1. Demonstration that cognitive fatigue detection works without cloud processing
2. Quantification of privacy-utility tradeoff in edge AI
3. Open-source framework for researchers to build on
4. Reference implementation for privacy-first multimodal monitoring

### Known Limitations
- ✅ **Scope**: Estimates relative fatigue, not clinical diagnosis
- ✅ **Validation**: Needs independent validation studies
- ✅ **Baseline**: Requires user calibration for best results
- ✅ **Environment**: Sensitive to lighting, noise conditions
- ✅ **Wearables**: Currently webcam/microphone only

---

## 9. REFERENCES

### Foundational Papers
```bibtex
@article{baltrušaitis2018,
  title={Multimodal Machine Learning: A Survey and Taxonomy},
  author={Baltrušaitis, Tadas and Ahuja, Chirag and Morency, Louis-Philippe},
  journal={IEEE transactions on pattern analysis and machine intelligence},
  year={2018}
}

@article{ekman1978,
  title={The Facial Action Coding System},
  author={Ekman, Paul and Friesen, Wallace V},
  journal={Consulting Psychologists Press},
  year={1978}
}

@article{dwork2014,
  title={The Algorithmic Foundations of Differential Privacy},
  author={Dwork, Cynthia and Roth, Aaron},
  journal={Foundations and Trends in Theoretical Computer Science},
  year={2014}
}
```

---

## 10. FUNDING & REPRODUCIBILITY

### Grant Alignment
- **NSF**: Privacy-preserving ML, HCI
- **NIH**: Workplace wellness, cognitive health
- **DARPA**: Edge AI, privacy tech

### Reproducibility Checklist
- [ ] Code: Open-source on GitHub with proper documentation
- [ ] Data: Synthetic dataset for testing (anonymized real data for research)
- [ ] Models: Published model weights and architecture specs
- [ ] Results: Detailed results tables with error bars
- [ ] Methods: Complete methodology section in paper
- [ ] Env: Docker containers for reproducible setup

---

**Next Steps:**
1. Conduct literature review update
2. Define validation study protocol
3. Implement feature engineering pipeline
4. Set up ML experiment tracking (MLflow)
5. Write research manuscript skeleton
