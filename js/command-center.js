console.log('Command Center Logic Loaded');

document.addEventListener('DOMContentLoaded', () => {
    // Basic initialization for command center can go here.

    // Load sessions from localStorage
    const sessions = JSON.parse(localStorage.getItem('mindguardian_sessions') || '[]');
    
    const ccTotalSessions = document.getElementById('ccTotalSessions');
    const ccAvgWellness = document.getElementById('ccAvgWellness');
    const ccLastRec = document.getElementById('ccLastRec');

    if (ccTotalSessions) {
        ccTotalSessions.textContent = sessions.length;
    }

    if (sessions.length > 0) {
        const lastSession = sessions[sessions.length - 1];
        
        if (ccAvgWellness) {
            ccAvgWellness.textContent = lastSession.wellness;
            
            // Adjust color based on wellness threshold if needed
            const wellnessVal = parseInt(lastSession.wellness);
            if (wellnessVal < 40) {
                ccAvgWellness.className = 'stat-value text-danger';
            } else if (wellnessVal < 75) {
                ccAvgWellness.className = 'stat-value text-warning';
            } else {
                ccAvgWellness.className = 'stat-value text-success';
            }
        }

        if (ccLastRec) {
            ccLastRec.textContent = lastSession.recommendation;
        }
    }
});
