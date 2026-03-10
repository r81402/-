import {
  GRID_SIZE,
  createInitialState,
  keyToDirection,
  setDirection,
  step,
  togglePause
} from './snakeGame.js';

const board = document.querySelector('[data-board]');
const scoreValue = document.querySelector('[data-score]');
const statusValue = document.querySelector('[data-status]');
const restartBtn = document.querySelector('[data-restart]');
const pauseBtn = document.querySelector('[data-pause]');
const controlButtons = document.querySelectorAll('[data-dir]');

const TICK_MS = 140;
let state = createInitialState();

function render() {
  board.style.setProperty('--grid-size', String(GRID_SIZE));
  board.innerHTML = '';

  state.snake.forEach((segment, index) => {
    const cell = document.createElement('div');
    cell.className = index === 0 ? 'snake-head' : 'snake-segment';
    cell.style.gridColumnStart = segment.x + 1;
    cell.style.gridRowStart = segment.y + 1;
    board.appendChild(cell);
  });

  if (state.food) {
    const food = document.createElement('div');
    food.className = 'food';
    food.style.gridColumnStart = state.food.x + 1;
    food.style.gridRowStart = state.food.y + 1;
    board.appendChild(food);
  }

  scoreValue.textContent = String(state.score);

  if (state.gameOver) {
    statusValue.textContent = 'Game over';
  } else if (state.paused) {
    statusValue.textContent = 'Paused';
  } else {
    statusValue.textContent = 'Running';
  }

  pauseBtn.textContent = state.paused ? 'Resume' : 'Pause';
}

function handleDirectionInput(key) {
  if (key === ' ') {
    state = togglePause(state);
    render();
    return;
  }

  const direction = keyToDirection(key);
  if (!direction) {
    return;
  }

  state = setDirection(state, direction);
}

document.addEventListener('keydown', (event) => {
  handleDirectionInput(event.key);
});

controlButtons.forEach((button) => {
  button.addEventListener('click', () => {
    const dir = button.dataset.dir;
    handleDirectionInput(dir);
  });
});

restartBtn.addEventListener('click', () => {
  state = createInitialState();
  render();
});

pauseBtn.addEventListener('click', () => {
  state = togglePause(state);
  render();
});

setInterval(() => {
  const prev = state;
  state = step(state);
  if (state !== prev) {
    render();
  }
}, TICK_MS);

render();
