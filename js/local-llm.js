/**
 * Local LLM Engine - Interface for local language model inference
 * Generates prompts and decisions based on fused features
 * Can work with Ollama, LM Studio, or other local LLM backends
 */

class LocalLLMEngine {
    constructor(endpoint = 'http://localhost:11434') {
        this.endpoint = endpoint;
        this.modelName = 'llama2'; // Default model
        this.isAvailable = false;
        this.lastPrompt = '';
        this.lastResponse = '';
        this.inferenceTime = 0;
    }

    async initialize(modelName = 'llama2') {
        try {
            this.modelName = modelName;
            // Test connection to local LLM
            const response = await fetch(`${this.endpoint}/api/tags`, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' }
            });
            
            if (response.ok) {
                this.isAvailable = true;
                console.log('[LocalLLMEngine] Connected to local LLM at', this.endpoint);
            }
        } catch (error) {
            console.warn('[LocalLLMEngine] Local LLM not available, using mock mode:', error);
            this.isAvailable = false;
        }
    }

    generatePrompt(fusedFeatures, sessionContext = {}) {
        const {
            cognitiveLoad,
            stressLevel,
            fatigue,
            engagement,
            burnoutRisk,
            vision,
            audio
        } = fusedFeatures;

        const sessionDuration = sessionContext.duration || '10 minutes';
        const sessionActivities = sessionContext.activities || 'coding/working';

        const prompt = `You are MindGuardian AI, a wellness assistant monitoring cognitive health.

Current Session Context:
- Duration: ${sessionDuration}
- Activities: ${sessionActivities}
- Time: ${new Date().toLocaleTimeString()}

Real-time Biometric Analysis:
- Cognitive Load: ${Math.round(cognitiveLoad)}%
- Stress Level: ${Math.round(stressLevel)}%
- Fatigue: ${Math.round(fatigue)}%
- Engagement: ${Math.round(engagement)}%
- Burnout Risk: ${Math.round(burnoutRisk)}%

Vision Metrics:
- Facial Expression: ${vision.expression}
- Blink Rate: ${vision.blinkRate} bpm
- Head Stability: ${Math.round(vision.faceStability)}%
- Eye Closure: ${Math.round(vision.eyeClosure)}%
- Yawning: ${vision.yawning ? 'Yes' : 'No'}

Audio Metrics:
- Speaking: ${audio.speaking ? 'Yes' : 'No'}
- Voice Energy: ${Math.round(audio.voiceEnergy)}%
- Speech Rate: ${Math.round(audio.rate)} wpm
- Audio Quality: ${audio.quality}

Based on this analysis:
1. Provide a brief wellness assessment (1-2 sentences)
2. Identify the primary wellness concern (if any)
3. Suggest ONE specific intervention or recommendation
4. Estimate recovery time if action is taken

Format your response as JSON:
{
  "assessment": "...",
  "concern": "...",
  "recommendation": "...",
  "recoveryTime": "...",
  "confidence": 0-100
}`;

        this.lastPrompt = prompt;
        return prompt;
    }

    async generateDecision(fusedFeatures, sessionContext = {}) {
        const prompt = this.generatePrompt(fusedFeatures, sessionContext);

        if (this.isAvailable) {
            return await this.callRemoteLLM(prompt);
        } else {
            // Use mock/fallback decision engine
            return this.generateMockDecision(fusedFeatures);
        }
    }

    async callRemoteLLM(prompt) {
        try {
            const startTime = Date.now();
            const response = await fetch(`${this.endpoint}/api/generate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    model: this.modelName,
                    prompt: prompt,
                    stream: false,
                    temperature: 0.7,
                    top_p: 0.9,
                    top_k: 40
                })
            });

            const data = await response.json();
            this.inferenceTime = Date.now() - startTime;
            this.lastResponse = data.response;
            
            // Try to parse JSON response
            return this.parseDecisionResponse(data.response);
        } catch (error) {
            console.error('[LocalLLMEngine] Error calling remote LLM:', error);
            // Fallback to mock
            return this.generateMockDecision({});
        }
    }

    parseDecisionResponse(response) {
        try {
            // Extract JSON from response
            const jsonMatch = response.match(/\{[^{}]*\}/);
            if (jsonMatch) {
                return JSON.parse(jsonMatch[0]);
            }
        } catch (e) {
            console.error('Failed to parse LLM response:', e);
        }
        
        return this.generateMockDecision({});
    }

    generateMockDecision(fusedFeatures) {
        // Mock decision engine (when local LLM is not available)
        const burnoutRisk = fusedFeatures.burnoutRisk || 0;
        const stressLevel = fusedFeatures.stressLevel || 0;
        const fatigue = fusedFeatures.fatigue || 0;

        let assessment, concern, recommendation, recoveryTime;
        let confidence = 85;

        // Decision logic based on metrics
        if (burnoutRisk > 70) {
            assessment = 'Critical wellness alert detected. Immediate intervention needed.';
            concern = 'Severe burnout risk';
            recommendation = 'Take a 15-minute break. Step outside for fresh air and movement.';
            recoveryTime = '20 minutes';
            confidence = 90;
        } else if (burnoutRisk > 50) {
            assessment = 'Moderate stress indicators detected.';
            concern = 'High stress levels';
            recommendation = 'Consider a 5-minute breathing exercise or brief walk.';
            recoveryTime = '10 minutes';
            confidence = 85;
        } else if (fatigue > 60) {
            assessment = 'Fatigue signals detected.';
            concern = 'Reduced energy levels';
            recommendation = 'Take a 2-minute stretch break and have some water.';
            recoveryTime = '5 minutes';
            confidence = 80;
        } else if (stressLevel > 60) {
            assessment = 'Mild stress indicators present.';
            concern = 'Moderate stress';
            recommendation = 'Try a quick mindfulness exercise or change tasks.';
            recoveryTime = '8 minutes';
            confidence = 78;
        } else {
            assessment = 'Wellness levels are good.';
            concern = 'None';
            recommendation = 'Continue with current activities. Maintain good posture and take regular breaks.';
            recoveryTime = 'N/A';
            confidence = 88;
        }

        return {
            assessment,
            concern,
            recommendation,
            recoveryTime,
            confidence,
            timestamp: Date.now()
        };
    }

    getLastPrompt() {
        return this.lastPrompt;
    }

    getLastResponse() {
        return this.lastResponse;
    }

    getInferenceTime() {
        return this.inferenceTime;
    }
}
