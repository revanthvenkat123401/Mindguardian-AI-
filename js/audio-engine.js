/**
 * Audio Engine - Real-time audio processing
 * Handles voice activity detection, pitch extraction, speech rate, noise analysis
 */

class AudioEngine {
    constructor() {
        this.audioContext = null;
        this.analyser = null;
        this.microphone = null;
        this.scriptProcessor = null;
        this.isRunning = false;
        this.currentMetrics = {
            speaking: false,
            voiceEnergy: 0,
            pitch: 0,
            noiseLevel: 0,
            rate: 0,
            silenceDuration: 0,
            peakAmplitude: 0,
            avgAmplitude: 0,
            quality: 'good',
            confidence: 0
        };
        this.frequencyData = null;
        this.timeData = null;
        this.silenceStart = Date.now();
        this.voiceActivityFrames = 0;
        this.lastFrameWasSpeech = false;
    }

    async initialize() {
        try {
            // Initialize Web Audio API
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            this.analyser = this.audioContext.createAnalyser();
            this.analyser.fftSize = 2048;
            this.analyser.smoothingTimeConstant = 0.8;

            // Get microphone access
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            this.microphone = this.audioContext.createMediaStreamSource(stream);
            
            // Create script processor for real-time processing
            this.scriptProcessor = this.audioContext.createScriptProcessor(4096, 1, 1);
            this.scriptProcessor.onaudioprocess = this.processAudio.bind(this);

            // Connect nodes
            this.microphone.connect(this.analyser);
            this.analyser.connect(this.scriptProcessor);
            this.scriptProcessor.connect(this.audioContext.destination);

            // Initialize data arrays
            this.frequencyData = new Uint8Array(this.analyser.frequencyBinCount);
            this.timeData = new Uint8Array(this.analyser.fftSize);

            this.isRunning = true;
            console.log('[AudioEngine] Initialized successfully');
            return true;
        } catch (error) {
            console.error('[AudioEngine] Initialization failed:', error);
            return false;
        }
    }

    processAudio(event) {
        const inputData = event.inputBuffer.getChannelData(0);
        
        // Calculate audio metrics
        this.calculateAmplitude(inputData);
        this.analyser.getByteFrequencyData(this.frequencyData);
        this.analyser.getByteTimeDomainData(this.timeData);
        
        this.detectVoiceActivity(inputData);
        this.estimatePitch(inputData);
        this.analyzeNoise();
        this.calculateSpeechRate();
    }

    calculateAmplitude(inputData) {
        let sum = 0;
        let max = 0;
        
        for (let i = 0; i < inputData.length; i++) {
            const value = Math.abs(inputData[i]);
            sum += value * value;
            max = Math.max(max, value);
        }

        this.currentMetrics.peakAmplitude = max;
        const rms = Math.sqrt(sum / inputData.length);
        this.currentMetrics.avgAmplitude = rms;
        this.currentMetrics.voiceEnergy = Math.min(100, rms * 500);
    }

    detectVoiceActivity(inputData) {
        // Simple VAD using amplitude threshold
        const threshold = 0.05;
        let activeCount = 0;

        for (let i = 0; i < inputData.length; i++) {
            if (Math.abs(inputData[i]) > threshold) {
                activeCount++;
            }
        }

        const activityRatio = activeCount / inputData.length;
        this.currentMetrics.speaking = activityRatio > 0.3;
        this.currentMetrics.confidence = Math.min(100, activityRatio * 200);

        if (this.currentMetrics.speaking) {
            this.silenceStart = Date.now();
            this.voiceActivityFrames++;
            this.lastFrameWasSpeech = true;
        } else {
            this.currentMetrics.silenceDuration = (Date.now() - this.silenceStart) / 1000;
            if (this.lastFrameWasSpeech) {
                this.lastFrameWasSpeech = false;
            }
        }
    }

    estimatePitch(inputData) {
        // Simple pitch detection using autocorrelation
        const autoCorrelation = this.autoCorrelate(inputData);
        this.currentMetrics.pitch = autoCorrelation;
    }

    autoCorrelate(inputData) {
        // Simplified autocorrelation for pitch detection
        const minPitch = 50;
        const maxPitch = 400;
        const minPeriod = Math.floor(this.audioContext.sampleRate / maxPitch);
        const maxPeriod = Math.floor(this.audioContext.sampleRate / minPitch);

        let bestOffset = -1;
        let bestCorrelation = 0;

        for (let offset = minPeriod; offset <= maxPeriod; offset++) {
            let correlation = 0;
            for (let i = 0; i < maxPeriod; i++) {
                correlation += Math.abs(
                    inputData[i] - inputData[i + offset]
                );
            }
            if (correlation < bestCorrelation) {
                bestCorrelation = correlation;
                bestOffset = offset;
            }
        }

        if (bestCorrelation < inputData.length && bestOffset > 0) {
            return this.audioContext.sampleRate / bestOffset;
        }
        return 0;
    }

    analyzeNoise() {
        // Analyze frequency spectrum for noise
        let noiseSum = 0;
        const lowFreqBins = Math.floor(this.frequencyData.length * 0.2);

        for (let i = 0; i < lowFreqBins; i++) {
            noiseSum += this.frequencyData[i];
        }

        this.currentMetrics.noiseLevel = Math.min(100, (noiseSum / lowFreqBins) / 2.55);
    }

    calculateSpeechRate() {
        // Estimate speech rate based on voice activity changes
        if (this.voiceActivityFrames > 0) {
            this.currentMetrics.rate = Math.min(200, this.voiceActivityFrames / 5);
        }
    }

    getQuality() {
        // Determine audio quality based on noise and clarity
        if (this.currentMetrics.noiseLevel > 60) {
            this.currentMetrics.quality = 'poor';
        } else if (this.currentMetrics.noiseLevel > 40) {
            this.currentMetrics.quality = 'fair';
        } else {
            this.currentMetrics.quality = 'good';
        }
    }

    getMetrics() {
        this.getQuality();
        return { ...this.currentMetrics };
    }

    getWaveformData() {
        return this.timeData;
    }

    stop() {
        if (this.scriptProcessor) {
            this.scriptProcessor.disconnect();
        }
        if (this.microphone) {
            this.microphone.disconnect();
        }
        if (this.audioContext) {
            this.audioContext.close();
        }
        this.isRunning = false;
        console.log('[AudioEngine] Stopped');
    }
}
