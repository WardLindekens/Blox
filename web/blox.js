// WebSocket handling
const ws = new WebSocket(`${location.origin.replace(/^http/, "ws")}/ws`);


ws.onopen = () => {
    console.log("WebSocket connected!");
};
ws.onerror = (err) => {
    console.error("WebSocket error:", err);
};

// Canvas setup
const canvas = document.getElementById("game");
const ctx = canvas.getContext("2d");
const boardCols = 6;
const boardRows = 16;

let tileSize = 40;
let resizeTimeout;

resizeCanvas();

function resizeCanvas() {
    const wrapper = document.getElementById("gameWrapper");
    const windowWidth = wrapper.clientWidth;
    const windowHeight = wrapper.clientHeight;

    const tileSizeX = Math.floor(windowWidth / boardCols);
    const tileSizeY = Math.floor(windowHeight / boardRows);
    tileSize = Math.min(tileSizeX, tileSizeY);

    canvas.width = tileSize * boardCols;
    canvas.height = tileSize * boardRows;
}

window.addEventListener('resize', () => {
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(resizeCanvas, 310);
});

// Game state
let fastDropActive = false;
let gameOverShown = false;

// Event listeners for handling input
setupInputListeners();

// Functions for handling WebSocket communication
ws.onmessage = handleServerMessage;

// WebSocket communication functions
function handleServerMessage(event) {
    const message = JSON.parse(event.data);

    switch(message.message_type) {
        case "state_update":
            draw(message);
            updateScore(message.score);
            updateLevel(message.level);
            if (message.game_over && !gameOverShown) {
                gameOverShown = true;
                document.getElementById("gameOver").classList.remove("hidden");
                showHighscores(message.highscores)
            }
            if (!message.game_over) {
                gameOverShown = false;
                document.getElementById("gameOver").classList.add("hidden");
            }
            break;
        case "animation_event":
            handleAnimationEvent(message.animations);
            break;
        default:
            console.warn("Unknown message type:", message.message_type);
    }
}

// Input handling functions
function setupInputListeners() {
    document.addEventListener("keydown", handleKeydown);
    document.addEventListener("keyup", handleKeyup);
    document.getElementById("resetBtn").onclick = resetGame;
    document.getElementById("leftBtn").onclick = moveLeft;
    document.getElementById("rightBtn").onclick = moveRight;
    document.getElementById("downBtn").ontouchstart = startFastDrop;
    document.getElementById("downBtn").ontouchend = stopFastDrop;
}

function handleKeydown(e) {
    let action = null;
    if (e.key === "ArrowLeft") action = "move_left";
    else if (e.key === "ArrowRight") action = "move_right";
    else if (e.key === "ArrowDown" && !fastDropActive) {
        startFastDrop();
    }
    if (action) {
        ws.send(JSON.stringify({ action }));
    }
    if(e.key === "r") resetGame();
}

function handleKeyup(e) {
    if (e.key === "ArrowDown" && fastDropActive) {
        stopFastDrop();
    }
}

function resetGame() {
    ws.send(JSON.stringify({ action: "reset" }));    
}

function moveLeft() {
    ws.send(JSON.stringify({ action: "move_left" }));
}

function moveRight() {
    ws.send(JSON.stringify({ action: "move_right" }));
}

function startFastDrop() {
    fastDropActive = true;
    ws.send(JSON.stringify({ action: "fast_drop", active: true }));
}

function stopFastDrop() {
    fastDropActive = false;
    ws.send(JSON.stringify({ action: "fast_drop", active: false }));
}

// Swipe gestures
let touchStartX = 0;
let touchStartY = 0;

window.addEventListener("touchstart", e => {
    const touch = e.touches[0];
    touchStartX = touch.clientX;
    touchStartY = touch.clientY;
});

window.addEventListener("touchend", e => {
    const touch = e.changedTouches[0];
    const dx = touch.clientX - touchStartX;
    const dy = touch.clientY - touchStartY;
    const absDx = Math.abs(dx);
    const absDy = Math.abs(dy);
    const threshold = 30;
    if (absDx > absDy && absDx > threshold) {
        ws.send(JSON.stringify({ action: dx > 0 ? "move_right" : "move_left" }));
    } else if (absDy > absDx && dy > threshold) {
        ws.send(JSON.stringify({ action: "fast_drop", active: true }));
        setTimeout(() => {
            ws.send(JSON.stringify({ action: "fast_drop", active: false }));
        }, 50);
    }
});

// Toggle Controls Button Logic
document.getElementById("toggleControlsBtn").onclick = () => {
    document.body.classList.toggle('show-controls');
    setTimeout(() => {
        resizeCanvas();
    }, 310);    
};

// Functions for drawing the game
function draw(state) {
    clearCanvas();
    drawGrid();
    drawBoard(state.board);
    drawBlock(state.block.x, state.block.y, state.block.color);
}

function clearCanvas() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
}

function drawGrid() {
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.3)';
    ctx.lineWidth = 1;
    for (let x = 0; x <= canvas.width; x += tileSize) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, canvas.height);
        ctx.stroke();
    }
    for (let y = 0; y <= canvas.height; y += tileSize) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(canvas.width, y);
        ctx.stroke();
    }
}

function drawBoard(board) {
    for (let y = 0; y < board.length; y++) {
        for (let x = 0; x < board[0].length; x++) {
            if (board[y][x] !== 0) {
                drawBlock(x, y, board[y][x]);
            }
        }
    }
}

function drawRow(row, colors){
    for( let x = 0; x < colors.length; x++){
        drawBlock(x, row, colors[x]);
    }
}

function drawBlock(x, y, color) {
    ctx.fillStyle = ["", "red", "green", "blue", "cyan", "magenta", "yellow"][color] || "gray";
    ctx.fillRect(x * tileSize, y * tileSize, tileSize - 2, tileSize - 2);
}

// Animation functions
function handleAnimationEvent(events){
    events.forEach(animation => {
        switch(animation.effect){
            case "flicker_row":
                flickerRow(animation.rows);
                break;
            default:
                console.log("animation not implemented yet")
        }
    });
}

function flickerRow(rows){
    let flickerInterval = 0;
    const flickerTimes = 6;
    const flickerDuration = 80;
    const flicker = setInterval(() => {        
        for( let x = 0; x < rows.length; x++){
            let color = (flickerInterval%2 === 0) ? "black": rows[x];
            drawBlock(x, boardRows - 1, color);
        }
        (flickerInterval%2 === 0) ? drawRow(boardRows - 1, [6,6,6,6,6,6]) : drawRow(boardRows - 1, rows);
        flickerInterval++;
        if(flickerInterval >= flickerTimes){
            clearInterval(flicker);
            drawRow(boardRows -1, rows);
        }
    }, flickerDuration);
}

// Functions for updating the game state
function updateScore(score) {
    const scoreDiv = document.getElementById("scoreDisplay");
    scoreDiv.textContent = `Score: ${score}`;
}

function updateLevel(level) {
    const scoreDiv = document.getElementById("levelDisplay");
    scoreDiv.textContent = `Level: ${level}`;
}

function showHighscores(scores) {
    const display = document.getElementById("highscoreDisplay");
    const list = document.getElementById("highscoreList");
    list.innerHTML = ""; // Clear previous list

    scores.forEach((entry, index) => {
        const row = document.createElement("div");
        row.style.display = "flex";
        row.style.justifyContent = "space-between";
        row.style.marginBottom = "10px";

        const rank = document.createElement("span");
        rank.textContent = `${index + 1}.`;
        rank.style.flex = "1";
        rank.style.textAlign = "right";

        const name = document.createElement("span");
        name.textContent = `${entry.name}`;
        name.style.flex = "1";
        name.style.textAlign = "center";

        const score = document.createElement("span");
        score.textContent = entry.score;
        score.style.flex = "1";
        score.style.textAlign = "right";

        row.appendChild(rank);
        row.appendChild(name);
        row.appendChild(score);
        list.appendChild(row);
    });
    display.style.display = "block";

}

function hideHighscores() {
    document.getElementById("highscoreDisplay").style.display = "none";
    location.reload();
}