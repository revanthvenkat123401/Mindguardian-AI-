/**
 * Vision Engine - Real-time computer vision processing
 * Handles face detection, facial landmarks, expressions, eye tracking, head pose
 */

class VisionEngine {
    constructor() {
        this.faceMesh = null;
        this.camera = null;
        this.isRunning = false;
        this.frameCount = 0;
        this.fpsCounter = 0;
        this.lastFpsTime = Date.now();
        this.currentMetrics = {
            faceDetected: false,
            landmarks: [],
            expression: 'neutral',
            smileScore: 0,
            blinkRate: 0,
            eyeClosure: 0,
            eyeOpenness: 100,
            ear: 0,
            lookingAway: false,
            headPose: { pitch: 0, yaw: 0, roll: 0 },
            headPitch: 0,
            headYaw: 0,
            headRoll: 0,
            mar: 0,
            mouthOpening: 0,
            yawning: false,
            faceStability: 100,
            distance: 'normal',
            tracking: false,
            lighting: 'normal',
            resolution: '0x0',
            fps: 0
        };
        this.blinkFrameCount = 0;
        this.lastBlinkTime = Date.now();
        this.consecutiveClosedFrames = 0;
    }

    async initialize(videoElement, canvasElement) {
        try {
            // Initialize MediaPipe Face Mesh
            const FaceMesh = window.FaceMesh;
            this.faceMesh = new FaceMesh({
                locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/face_mesh/${file}`
            });

            this.faceMesh.setOptions({
                maxNumFaces: 1,
                refineLandmarks: true,
                minDetectionConfidence: 0.5,
                minTrackingConfidence: 0.5
            });

            this.faceMesh.onResults(this.onResults.bind(this));

            // Initialize camera
            const Camera = window.Camera;
            if (Camera) {
                this.camera = new Camera(videoElement, {
                    onFrame: async () => {
                        await this.faceMesh.send({ image: videoElement });
                    },
                    width: videoElement.videoWidth || 1280,
                    height: videoElement.videoHeight || 720
                });
                await this.camera.initialize();
            } else {
                console.warn('MediaPipe Camera not available, using fallback');
            }

            this.isRunning = true;
            console.log('[VisionEngine] Initialized successfully');
            return true;
        } catch (error) {
            console.error('[VisionEngine] Initialization failed:', error);
            return false;
        }
    }

    onResults(results) {
        if (!results.multiFaceLandmarks || results.multiFaceLandmarks.length === 0) {
            this.currentMetrics.faceDetected = false;
            return;
        }

        const landmarks = results.multiFaceLandmarks[0];
        this.currentMetrics.faceDetected = true;
        this.currentMetrics.landmarks = landmarks;
        this.currentMetrics.tracking = true;

        // Calculate facial metrics
        this.calculateExpressionMetrics(landmarks);
        this.calculateHeadPose(landmarks);
        this.calculateEyeMetrics(landmarks);
        this.calculateMouthMetrics(landmarks);
        this.calculateFaceStability(landmarks);

        this.frameCount++;
        this.updateFPS();
    }

    calculateExpressionMetrics(landmarks) {
        // Smile detection using mouth corner positions
        const mouthLeft = landmarks[61];  // Mouth left corner
        const mouthRight = landmarks[291]; // Mouth right corner
        const mouthTop = landmarks[13];    // Mouth top
        const mouthBottom = landmarks[14];  // Mouth bottom

        // Simple smile score based on mouth corner uplift
        const mouthCornerDiff = (mouthLeft.y + mouthRight.y) - (mouthTop.y + mouthBottom.y);
        this.currentMetrics.smileScore = Math.max(0, Math.min(100, 50 + mouthCornerDiff * 200));

        // Determine expression
        if (this.currentMetrics.smileScore > 70) {
            this.currentMetrics.expression = 'happy';
        } else if (this.currentMetrics.smileScore > 40) {
            this.currentMetrics.expression = 'neutral';
        } else {
            this.currentMetrics.expression = 'stressed';
        }
    }

    calculateHeadPose(landmarks) {
        // Simplified head pose estimation using facial landmarks
        const nose = landmarks[1];
        const forehead = landmarks[10];
        const chin = landmarks[152];
        const leftEar = landmarks[234];
        const rightEar = landmarks[454];

        // Pitch: vertical head angle
        const verticalDist = chin.y - forehead.y;
        const noseCenterX = (leftEar.x + rightEar.x) / 2;
        this.currentMetrics.headPitch = (nose.y - forehead.y) * 90;

        // Yaw: horizontal head angle
        const horizontalDiff = nose.x - noseCenterX;
        this.currentMetrics.headYaw = horizontalDiff * 90;

        // Roll: tilt angle
        const earDiff = leftEar.y - rightEar.y;
        this.currentMetrics.headRoll = earDiff * 90;
    }

    calculateEyeMetrics(landmarks) {
        // Eye Aspect Ratio (EAR) for blink detection
        const leftEye = this.getEyePoints(landmarks, 'left');
        const rightEye = this.getEyePoints(landmarks, 'right');

        const leftEAR = this.calculateEAR(leftEye);
        const rightEAR = this.calculateEAR(rightEye);
        this.currentMetrics.ear = (leftEAR + rightEAR) / 2;

        // Eye closure detection (EAR threshold ~0.2)
        const earThreshold = 0.2;
        if (this.currentMetrics.ear < earThreshold) {
            this.consecutiveClosedFrames++;
        } else {
            if (this.consecutiveClosedFrames > 2) {
                this.blinkFrameCount++;
                this.lastBlinkTime = Date.now();
            }
            this.consecutiveClosedFrames = 0;
        }

        this.currentMetrics.eyeClosure = Math.max(0, 100 - this.currentMetrics.ear * 500);
        this.currentMetrics.eyeOpenness = 100 - this.currentMetrics.eyeClosure;

        // Looking away detection - check if eye is outside normal range
        const eyeCenterX = (landmarks[133].x + landmarks[362].x) / 2;
        const faceCenterX = 0.5;
        this.currentMetrics.lookingAway = Math.abs(eyeCenterX - faceCenterX) > 0.15;
    }

    calculateMouthMetrics(landmarks) {
        // Mouth opening (MAR - Mouth Aspect Ratio)
        const topLip = landmarks[13];
        const bottomLip = landmarks[14];
        const leftCorner = landmarks[61];
        const rightCorner = landmarks[291];

        const mouthHeight = Math.abs(topLip.y - bottomLip.y);
        const mouthWidth = Math.abs(rightCorner.x - leftCorner.x);
        this.currentMetrics.mar = mouthHeight / (mouthWidth + 0.001);
        this.currentMetrics.mouthOpening = Math.min(100, this.currentMetrics.mar * 100);

        // Yawning detection (high MAR + duration)
        this.currentMetrics.yawning = this.currentMetrics.mar > 0.6;
    }

    calculateFaceStability(landmarks) {
        // Compare consecutive frame landmarks to assess stability
        // Higher stability = steadier face position
        if (!this.lastLandmarks) {
            this.lastLandmarks = landmarks;
            this.currentMetrics.faceStability = 100;
            return;
        }

        let totalDiff = 0;
        for (let i = 0; i < landmarks.length; i++) {
            totalDiff += Math.abs(landmarks[i].x - this.lastLandmarks[i].x) +
                        Math.abs(landmarks[i].y - this.lastLandmarks[i].y);
        }

        const avgDiff = totalDiff / landmarks.length;
        this.currentMetrics.faceStability = Math.max(0, 100 - avgDiff * 50);
        this.lastLandmarks = landmarks;
    }

    getEyePoints(landmarks, side) {
        if (side === 'left') {
            return {
                top: landmarks[159],
                bottom: landmarks[145],
                left: landmarks[133],
                right: landmarks[33]
            };
        } else {
            return {
                top: landmarks[386],
                bottom: landmarks[374],
                left: landmarks[362],
                right: landmarks[263]
            };
        }
    }

    calculateEAR(eyePoints) {
        const A = this.euclideanDistance(eyePoints.top, eyePoints.bottom);
        const B = this.euclideanDistance(eyePoints.left, eyePoints.right);
        return A / (2 * B + 0.001);
    }

    euclideanDistance(p1, p2) {
        return Math.sqrt(Math.pow(p1.x - p2.x, 2) + Math.pow(p1.y - p2.y, 2));
    }

    updateFPS() {
        this.fpsCounter++;
        const now = Date.now();
        if (now - this.lastFpsTime >= 1000) {
            this.currentMetrics.fps = this.fpsCounter;
            this.fpsCounter = 0;
            this.lastFpsTime = now;
        }
    }

    calculateBlinkRate() {
        const now = Date.now();
        const secondsElapsed = (now - this.lastBlinkTime) / 1000;
        if (secondsElapsed > 0) {
            return Math.round((this.blinkFrameCount / secondsElapsed) * 60);
        }
        return 0;
    }

    getMetrics() {
        return {
            ...this.currentMetrics,
            blinkRate: this.calculateBlinkRate()
        };
    }

    stop() {
        if (this.camera) {
            this.camera.stop();
        }
        this.isRunning = false;
        console.log('[VisionEngine] Stopped');
    }
}
