document.addEventListener('DOMContentLoaded', () => {
    // Calculate progress bar position
    const teamScores = document.querySelectorAll('.team-score');
    const progressFill = document.querySelector('.progress-fill');
    
    function updateProgressBar() {
        const team1Score = parseInt(teamScores[0].dataset.score);
        const team2Score = parseInt(teamScores[1].dataset.score);
        const total = team1Score + team2Score;
        const team1Percentage = (team1Score / total) * 100;
        
        progressFill.style.width = `${team1Percentage}%`;
    }

    // Initial update
    updateProgressBar();
    
    // Update when scores change (you can call this function when scores update)
    window.updateScores = (team1, team2) => {
        teamScores[0].dataset.score = team1;
        teamScores[1].dataset.score = team2;
        teamScores[0].textContent = team1;
        teamScores[1].textContent = team2;
        updateProgressBar();
    }
});