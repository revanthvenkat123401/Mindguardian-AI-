/**
 * Feature Fusion Engine - Combines multimodal signals
 * Fuses vision and audio features to create rich cognitive state representation
 */

class FeatureFusion {
    constructor() {
        this.visionEngine = null;
        this.audioEngine = null;
        this.fusedFeatures = {
            cognitiveLoad: 0,
            stressLevel: 0,
            fatigue: 0,
            engagement: 0,
            burnoutRisk: 0,
            sessionQuality: 0,
            timestamp: Date.now()
        };
        this.historyBuffer = [];
        this.maxHistory = 100;
    }

    initialize(visionEngine, audioEngine) {
        this.visionEngine = visionEngine;
        this.audioEngine = audioEngine;
        console.log('[FeatureFusion] Initialized');
    }

    fuse() {
        if (!this.visionEngine || !this.audioEngine) {
            return null;
        }

        const visionMetrics = this.visionEngine.getMetrics();
        const audioMetrics = this.audioEngine.getMetrics();

        // Calculate fused features
        this.fusedFeatures = {
            cognitiveLoad: this.calculateCognitiveLoad(visionMetrics, audioMetrics),
            stressLevel: this.calculateStressLevel(visionMetrics, audioMetrics),
            fatigue: this.calculateFatigue(visionMetrics, audioMetrics),
            engagement: this.calculateEngagement(visionMetrics, audioMetrics),
            burnoutRisk: this.calculateBurnoutRisk(visionMetrics, audioMetrics),
            sessionQuality: this.calculateSessionQuality(visionMetrics, audioMetrics),
            timestamp: Date.now(),
            // Raw multimodal features
            vision: visionMetrics,
            audio: audioMetrics
        };

        // Store in history
        this.historyBuffer.push(this.fusedFeatures);
        if (this.historyBuffer.length > this.maxHistory) {
            this.historyBuffer.shift();
        }

        return this.fusedFeatures;
    }

    calculateCognitiveLoad(vision, audio) {
        // Cognitive load indicators:
        // - High stress in facial expression
        // - Frequent blinks (over 20/min)
        // - Reduced head stability
        // - Changes in voice pitch

        let score = 0;
        
        // Expression-based (stress indicator)
        if (vision.expression === 'stressed') score += 30;
        else if (vision.expression === 'neutral') score += 15;
        
        // Blink rate (normal ~17/min, higher during strain)
        if (vision.blinkRate > 25) score += 25;
        else if (vision.blinkRate < 10) score += 20;
        
        // Head stability
        score += (100 - vision.faceStability) * 0.2;
        
        // Voice characteristics
        if (audio.speaking) {
            if (audio.pitch > 200 || audio.pitch < 100) score += 15;
        }
        
        return Math.min(100, score);
    }

    calculateStressLevel(vision, audio) {
        // Stress indicators:
        // - Facial tension (reduced smile score)
        // - Eye closure/tension (low EAR or high eye closure)
        // - Head movement (unstable pose)
        // - Voice tension (pitch changes, speech rate)

        let score = 0;
        
        // Facial tension
        if (vision.smileScore < 30) score += 30;
        if (vision.eyeClosure > 20) score += 15;
        
        // Head movement
        const headMovement = Math.abs(vision.headPitch) + Math.abs(vision.headYaw);
        if (headMovement > 30) score += 20;
        
        // Voice strain indicators
        if (audio.speaking) {
            if (audio.rate > 150) score += 20; // Fast speech
            if (audio.voiceEnergy > 70) score += 15; // High intensity
        }
        
        // Yawning (stress relief indicator)
        if (vision.yawning) score += 10;
        
        return Math.min(100, score);
    }

    calculateFatigue(vision, audio) {
        // Fatigue indicators:
        // - Eye closure/drooping (high eye closure duration)
        // - Slow blink rate
        // - Head drooping (pitch angle)
        // - Monotone voice
        // - Reduced engagement

        let score = 0;
        
        // Eye metrics
        if (vision.eyeClosure > 30) score += 35;
        if (vision.blinkRate < 12) score += 20;
        
        // Head position (drooping forward)
        if (vision.headPitch > 20) score += 25;
        
        // Voice monotony
        if (audio.speaking) {
            if (audio.pitch === 0 || Math.abs(audio.pitch - 120) < 20) score += 15;
        }
        
        // Looking away
        if (vision.lookingAway) score += 10;
        
        return Math.min(100, score);
    }

    calculateEngagement(vision, audio) {
        // Engagement indicators:
        // - Stable head/face position
        // - Active eye contact (not looking away)
        // - Speaking/voice activity
        // - Positive expression
        // - High face stability

        let score = 50; // Base score
        
        // Face stability (high = engaged)
        score += vision.faceStability * 0.3;
        
        // Positive expression
        if (vision.expression === 'happy') score += 20;
        
        // Eye contact
        if (!vision.lookingAway) score += 15;
        
        // Voice activity
        if (audio.speaking) score += 10;
        
        // Stable head
        const headMovement = Math.abs(vision.headPitch) + Math.abs(vision.headYaw);
        if (headMovement < 15) score += 10;
        
        return Math.min(100, Math.max(0, score));
    }

    calculateBurnoutRisk(vision, audio) {
        // Burnout risk combines multiple factors:
        // - High stress levels
        // - High cognitive load
        // - Moderate to high fatigue
        // - Low engagement over time

        const stress = this.calculateStressLevel(vision, audio);
        const cogLoad = this.calculateCognitiveLoad(vision, audio);
        const fatigue = this.calculateFatigue(vision, audio);
        const engagement = this.calculateEngagement(vision, audio);
        
        // Weighted combination
        const riskScore = (stress * 0.35) + (cogLoad * 0.25) + (fatigue * 0.25) + ((100 - engagement) * 0.15);
        
        return Math.min(100, Math.max(0, riskScore));
    }

    calculateSessionQuality(vision, audio) {
        // Session quality based on data reliability
        let qualityScore = 100;
        
        // Face detection quality
        if (!vision.faceDetected) qualityScore -= 50;
        if (!vision.tracking) qualityScore -= 20;
        
        // Audio quality
        if (audio.quality === 'poor') qualityScore -= 20;
        else if (audio.quality === 'fair') qualityScore -= 10;
        
        // Face stability
        qualityScore -= (100 - vision.faceStability) * 0.3;
        
        return Math.max(0, qualityScore);
    }

    getRiskCategory(riskScore) {
        if (riskScore < 30) return 'Low';
        if (riskScore < 60) return 'Medium';
        return 'High';
    }

    getFusedFeatures() {
        return this.fusedFeatures;
    }

    getHistory() {
        return this.historyBuffer;
    }

    getAverageMetrics(windowSize = 10) {
        const window = this.historyBuffer.slice(-windowSize);
        if (window.length === 0) return null;

        const avg = {
            cognitiveLoad: 0,
            stressLevel: 0,
            fatigue: 0,
            engagement: 0,
            burnoutRisk: 0
        };

        window.forEach(frame => {
            avg.cognitiveLoad += frame.cognitiveLoad;
            avg.stressLevel += frame.stressLevel;
            avg.fatigue += frame.fatigue;
            avg.engagement += frame.engagement;
            avg.burnoutRisk += frame.burnoutRisk;
        });

        Object.keys(avg).forEach(key => {
            avg[key] = Math.round(avg[key] / window.length);
        });

        return avg;
    }
}
