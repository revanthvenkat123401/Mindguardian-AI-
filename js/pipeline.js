/**
 * AI Pipeline Orchestrator - Coordinates all pipeline components
 * Manages vision, audio, fusion, LLM, and decision engines
 */

class MindGuardianPipeline {
    constructor() {
        this.visionEngine = new VisionEngine();
        this.audioEngine = new AudioEngine();
        this.featureFusion = new FeatureFusion();
        this.llmEngine = new LocalLLMEngine();
        this.decisionEngine = new DecisionEngine(this.llmEngine);
        
        this.isRunning = false;
        this.processingInterval = null;
        this.decisionInterval = null;
        this.processingFrequency = 100; // ms between fusion updates
        this.decisionFrequency = 3000; // ms between decision updates
        
        this.pipelineHistory = [];
        this.sessionMetrics = null;
        this.eventCallbacks = {};
    }

    async initialize(videoElement, canvasElement) {
        try {
            console.log('[Pipeline] Initializing MindGuardian AI Pipeline...');
            
            // Initialize vision engine
            const visionReady = await this.visionEngine.initialize(videoElement, canvasElement);
            if (!visionReady) throw new Error('Vision engine failed');
            
            // Initialize audio engine
            const audioReady = await this.audioEngine.initialize();
            if (!audioReady) throw new Error('Audio engine failed');
            
            // Initialize fusion
            this.featureFusion.initialize(this.visionEngine, this.audioEngine);
            
            // Initialize LLM
            await this.llmEngine.initialize('llama2');
            
            console.log('[Pipeline] All components initialized successfully');
            this.emit('pipeline:ready');
            return true;
        } catch (error) {
            console.error('[Pipeline] Initialization failed:', error);
            this.emit('pipeline:error', error);
            return false;
        }
    }

    start() {
        if (this.isRunning) return;
        
        this.isRunning = true;
        this.sessionMetrics = {
            startTime: Date.now(),
            decisions: [],
            frames: 0
        };
        
        console.log('[Pipeline] Starting continuous processing...');
        
        // Process fusion updates frequently
        this.processingInterval = setInterval(() => this.processFrame(), this.processingFrequency);
        
        // Generate decisions periodically
        this.decisionInterval = setInterval(() => this.generateDecision(), this.decisionFrequency);
        
        this.emit('pipeline:started');
    }

    processFrame() {
        if (!this.isRunning || !this.featureFusion.visionEngine) return;
        
        // Fuse current frame
        const fused = this.featureFusion.fuse();
        if (fused) {
            this.sessionMetrics.frames++;
            this.emit('fusion:update', fused);
        }
    }

    async generateDecision() {
        if (!this.isRunning) return;
        
        const fused = this.featureFusion.getFusedFeatures();
        if (!fused) return;
        
        try {
            const decision = await this.decisionEngine.makeDecision(fused, {
                duration: this.getSessionDuration(),
                activities: 'Session monitoring'
            });
            
            this.sessionMetrics.decisions.push(decision);
            this.emit('decision:generated', decision);
            
            // Execute if priority warrants it
            if (['URGENT', 'HIGH'].includes(decision.priority)) {
                this.decisionEngine.executeIntervention(decision);
                this.emit('intervention:executed', decision);
            }
        } catch (error) {
            console.error('[Pipeline] Decision generation error:', error);
        }
    }

    stop() {
        if (!this.isRunning) return;
        
        clearInterval(this.processingInterval);
        clearInterval(this.decisionInterval);
        
        this.visionEngine.stop();
        this.audioEngine.stop();
        
        this.isRunning = false;
        console.log('[Pipeline] Pipeline stopped');
        this.emit('pipeline:stopped');
        
        return this.getSessionSummary();
    }

    getSessionDuration() {
        if (!this.sessionMetrics) return '0s';
        const ms = Date.now() - this.sessionMetrics.startTime;
        const seconds = Math.floor(ms / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);
        
        if (hours > 0) return `${hours}h ${minutes % 60}m`;
        if (minutes > 0) return `${minutes}m ${seconds % 60}s`;
        return `${seconds}s`;
    }

    getSessionSummary() {
        if (!this.sessionMetrics) return null;
        
        const history = this.featureFusion.getHistory();
        const avgMetrics = this.featureFusion.getAverageMetrics();
        const interventions = this.decisionEngine.getInterventionHistory();
        
        return {
            duration: this.getSessionDuration(),
            startTime: this.sessionMetrics.startTime,
            endTime: Date.now(),
            totalFrames: this.sessionMetrics.frames,
            averageMetrics: avgMetrics,
            decisions: this.sessionMetrics.decisions,
            interventions: interventions,
            finalState: this.decisionEngine.getCurrentDecision()?.state || 'UNKNOWN'
        };
    }

    getFusedFeatures() {
        return this.featureFusion.getFusedFeatures();
    }

    getCurrentDecision() {
        return this.decisionEngine.getCurrentDecision();
    }

    getPipelineStatus() {
        return {
            running: this.isRunning,
            visionReady: this.visionEngine.isRunning,
            audioReady: this.audioEngine.isRunning,
            visionMetrics: this.visionEngine.getMetrics(),
            audioMetrics: this.audioEngine.getMetrics(),
            fusedMetrics: this.featureFusion.getFusedFeatures(),
            currentDecision: this.decisionEngine.getCurrentDecision()
        };
    }

    // Event system
    on(event, callback) {
        if (!this.eventCallbacks[event]) {
            this.eventCallbacks[event] = [];
        }
        this.eventCallbacks[event].push(callback);
    }

    emit(event, data) {
        if (!this.eventCallbacks[event]) return;
        this.eventCallbacks[event].forEach(callback => callback(data));
    }
}

// Global pipeline instance
let pipeline = null;

function initializePipeline(videoElement, canvasElement) {
    if (!pipeline) {
        pipeline = new MindGuardianPipeline();
    }
    return pipeline.initialize(videoElement, canvasElement);
}

function startPipeline() {
    if (pipeline) {
        pipeline.start();
    }
}

function stopPipeline() {
    if (pipeline) {
        return pipeline.stop();
    }
}

function getPipeline() {
    return pipeline;
}
