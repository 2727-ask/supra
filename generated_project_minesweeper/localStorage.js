// localStorage.js

function saveGameState() {
    const gameState = {
        board: board,
        revealedCells: revealedCells,
        gameOver: gameOver
    };
    localStorage.setItem('minesweeperState', JSON.stringify(gameState));
}

function loadGameState() {
    const savedState = localStorage.getItem('minesweeperState');
    if (savedState) {
        const gameState = JSON.parse(savedState);
        board = gameState.board;
        revealedCells = gameState.revealedCells;
        gameOver = gameState.gameOver;

        // Re-render the board based on the loaded state
        const container = document.getElementById('minesweeper-container');
        container.innerHTML = ''; // Clear existing cells
        createBoard();
    }
}

// Call loadGameState when the game starts to restore any saved state
window.onload = () => {
    loadGameState();
};