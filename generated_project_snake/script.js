const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

canvas.width = 400;
canvas.height = 400;

let snake = [{ x: 150, y: 150 }, { x: 140, y: 150 }, { x: 130, y: 150 }];
let direction = 'RIGHT';
let food = { x: 200, y: 200 };
let speed = 1;
let gameInterval;

function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw snake
    ctx.fillStyle = 'green';
    snake.forEach(segment => {
        ctx.fillRect(segment.x, segment.y, 10, 10);
    });

    // Draw food
    ctx.fillStyle = 'red';
    ctx.fillRect(food.x, food.y, 10, 10);
}

function update() {
    let head = { x: snake[0].x, y: snake[0].y };

    switch (direction) {
        case 'UP':
            head.y -= 10;
            break;
        case 'DOWN':
            head.y += 10;
            break;
        case 'LEFT':
            head.x -= 10;
            break;
        case 'RIGHT':
            head.x += 10;
            break;
    }

    snake.unshift(head);

    if (head.x === food.x && head.y === food.y) {
        food = { x: Math.floor(Math.random() * 40) * 10, y: Math.floor(Math.random() * 40) * 10 };
    } else {
        snake.pop();
    }

    // Game over conditions
    if (head.x < 0 || head.x >= canvas.width || head.y < 0 || head.y >= canvas.height || checkCollision(head)) {
        clearInterval(gameInterval);
        alert('Game Over!');
    }
}

function checkCollision(head) {
    for (let i = 1; i < snake.length; i++) {
        if (head.x === snake[i].x && head.y === snake[i].y) {
            return true;
        }
    }
    return false;
}

document.addEventListener('keydown', (e) => {
    switch (e.key) {
        case 'ArrowUp':
            if (direction !== 'DOWN') direction = 'UP';
            break;
        case 'ArrowDown':
            if (direction !== 'UP') direction = 'DOWN';
            break;
        case 'ArrowLeft':
            if (direction !== 'RIGHT') direction = 'LEFT';
            break;
        case 'ArrowRight':
            if (direction !== 'LEFT') direction = 'RIGHT';
            break;
    }
});

document.getElementById('speedSlider').addEventListener('input', (e) => {
    speed = e.target.value;
    clearInterval(gameInterval);
    gameInterval = setInterval(() => {
        update();
        draw();
    }, 100 / speed);
});

gameInterval = setInterval(() => {
    update();
    draw();
}, 100 / speed);