const boardSize = 10;
const mineCount = 10;

let board = [];
let revealedCells = 0;
let gameOver = false;

function initBoard() {
    for (let i = 0; i < boardSize * boardSize; i++) {
        board.push({ isMine: false, revealed: false, flagged: false });
    }
    placeMines();
}

function placeMines() {
    let minesPlaced = 0;
    while (minesPlaced < mineCount) {
        const randomIndex = Math.floor(Math.random() * board.length);
        if (!board[randomIndex].isMine) {
            board[randomIndex].isMine = true;
            minesPlaced++;
        }
    }
}

function revealCell(index) {
    if (gameOver || board[index].revealed || board[index].flagged) return;

    const cell = document.getElementById(`cell-${index}`);
    if (board[index].isMine) {
        gameOver = true;
        cell.classList.add('mine');
        alert('Game Over! You hit a mine.');
        revealAllMines();
    } else {
        board[index].revealed = true;
        revealedCells++;
        cell.classList.add('revealed');

        const adjacentMines = countAdjacentMines(index);
        if (adjacentMines > 0) {
            cell.textContent = adjacentMines;
        } else {
            revealAdjacentCells(index);
        }

        if (revealedCells === board.length - mineCount) {
            gameOver = true;
            alert('Congratulations! You won!');
        }
    }
}

function countAdjacentMines(index) {
    const row = Math.floor(index / boardSize);
    const col = index % boardSize;
    let count = 0;

    for (let i = -1; i <= 1; i++) {
        for (let j = -1; j <= 1; j++) {
            if (i === 0 && j === 0) continue;
            const newRow = row + i;
            const newCol = col + j;
            if (newRow >= 0 && newRow < boardSize && newCol >= 0 && newCol < boardSize) {
                const newIndex = newRow * boardSize + newCol;
                if (board[newIndex].isMine) count++;
            }
        }
    }

    return count;
}

function revealAdjacentCells(index) {
    const row = Math.floor(index / boardSize);
    const col = index % boardSize;

    for (let i = -1; i <= 1; i++) {
        for (let j = -1; j <= 1; j++) {
            if (i === 0 && j === 0) continue;
            const newRow = row + i;
            const newCol = col + j;
            if (newRow >= 0 && newRow < boardSize && newCol >= 0 && newCol < boardSize) {
                const newIndex = newRow * boardSize + newCol;
                revealCell(newIndex);
            }
        }
    }
}

function flagCell(index) {
    if (gameOver || board[index].revealed) return;

    const cell = document.getElementById(`cell-${index}`);
    if (!board[index].flagged) {
        board[index].flagged = true;
        cell.classList.add('flagged');
    } else {
        board[index].flagged = false;
        cell.classList.remove('flagged');
    }
}

function revealAllMines() {
    for (let i = 0; i < board.length; i++) {
        if (board[i].isMine) {
            const cell = document.getElementById(`cell-${i}`);
            cell.classList.add('mine');
        }
    }
}

function createBoard() {
    const container = document.getElementById('minesweeper-container');
    for (let i = 0; i < board.length; i++) {
        const cell = document.createElement('div');
        cell.className = 'cell';
        cell.id = `cell-${i}`;
        cell.addEventListener('click', () => revealCell(i));
        cell.addEventListener('contextmenu', (e) => {
            e.preventDefault();
            flagCell(i);
        });
        container.appendChild(cell);
    }
}

function initGame() {
    initBoard();
    createBoard();
}

initGame();