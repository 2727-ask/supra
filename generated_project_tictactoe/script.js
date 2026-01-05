document.addEventListener('DOMContentLoaded', () => {
    const cells = document.querySelectorAll('.cell');
    const playerTurnDisplay = document.getElementById('player-turn');
    const resetButton = document.getElementById('reset-button');
    let currentPlayer = 'X';
    let gameBoard = ['', '', '', '', '', '', '', '', ''];
    let gameActive = true;

    function handleCellClick(event) {
        const cellIndex = event.target.getAttribute('data-index');

        if (gameBoard[cellIndex] !== '' || !gameActive) return;

        placeMark(event.target, currentPlayer);
        updateGameBoard(cellIndex, currentPlayer);

        if (checkWin()) {
            endGame(`Player ${currentPlayer} wins!`);
            gameActive = false;
        } else if (isDraw()) {
            endGame('It\'s a draw!');
            gameActive = false;
        } else {
            switchPlayer();
        }
    }

    function placeMark(cell, currentMarker) {
        cell.textContent = currentMarker;
    }

    function updateGameBoard(index, marker) {
        gameBoard[index] = marker;
    }

    function checkWin() {
        const winConditions = [
            [0, 1, 2],
            [3, 4, 5],
            [6, 7, 8],
            [0, 3, 6],
            [1, 4, 7],
            [2, 5, 8],
            [0, 4, 8],
            [2, 4, 6]
        ];

        return winConditions.some(condition => {
            return condition.every(index => gameBoard[index] === currentPlayer);
        });
    }

    function isDraw() {
        return gameBoard.every(cell => cell !== '');
    }

    function switchPlayer() {
        currentPlayer = (currentPlayer === 'X') ? 'O' : 'X';
        playerTurnDisplay.textContent = `Player ${currentPlayer}'s turn`;
    }

    function endGame(message) {
        playerTurnDisplay.textContent = message;
        cells.forEach(cell => cell.removeEventListener('click', handleCellClick));
    }

    resetButton.addEventListener('click', () => {
        gameBoard = ['', '', '', '', '', '', '', '', ''];
        currentPlayer = 'X';
        gameActive = true;
        playerTurnDisplay.textContent = `Player ${currentPlayer}'s turn`;
        cells.forEach(cell => {
            cell.textContent = '';
            cell.addEventListener('click', handleCellClick);
        });
    });

    cells.forEach(cell => {
        cell.addEventListener('click', handleCellClick);
    });
});