// localStorage.js

function saveHighScore(score) {
    let highScore = localStorage.getItem('highScore');
    if (highScore === null || score > highScore) {
        localStorage.setItem('highScore', score);
    }
}

function loadHighScore() {
    return localStorage.getItem('highScore') || 0;
}
