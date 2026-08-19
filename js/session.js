document.addEventListener('DOMContentLoaded', () => {
    const startBtn = document.getElementById('startSessionBtn');
    const pauseBtn = document.getElementById('pauseSessionBtn');
    const resumeBtn = document.getElementById('resumeSessionBtn');
    const endBtn = document.getElementById('endSessionBtn');
    const retryBtn = document.getElementById('retryHardwareBtn');
    const cancelBtn = document.getElementById('cancelHardwareBtn');

    if(startBtn) {
        startBtn.addEventListener('click', () => {
            Pipeline.start();
        });
    }
    
    if(pauseBtn) {
        pauseBtn.addEventListener('click', () => {
            Pipeline.pause();
        });
    }

    if(resumeBtn) {
        resumeBtn.addEventListener('click', () => {
            Pipeline.resume();
        });
    }

    if(endBtn) {
        endBtn.addEventListener('click', () => {
            Pipeline.end();
        });
    }

    if (retryBtn) {
        retryBtn.addEventListener('click', () => {
            Pipeline.start();
        });
    }

    if (cancelBtn) {
        cancelBtn.addEventListener('click', () => {
            const errorState = document.getElementById('cameraErrorState');
            if (errorState) errorState.classList.add('hidden');
            Pipeline.end();
        });
    }

    const startNewBtn = document.getElementById('startNewSessionBtn');
    if(startNewBtn) {
        startNewBtn.addEventListener('click', () => {
            const modal = document.getElementById('sessionSummaryModal');
            if (modal) modal.classList.add('hidden');
            // The pipeline is already completely reset to Idle by the end() method
        });
    }
});
