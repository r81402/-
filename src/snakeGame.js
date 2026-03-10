export const GRID_SIZE = 20;

const DIRECTIONS = {
  ArrowUp: { x: 0, y: -1 },
  ArrowDown: { x: 0, y: 1 },
  ArrowLeft: { x: -1, y: 0 },
  ArrowRight: { x: 1, y: 0 },
  w: { x: 0, y: -1 },
  s: { x: 0, y: 1 },
  a: { x: -1, y: 0 },
  d: { x: 1, y: 0 },
  W: { x: 0, y: -1 },
  S: { x: 0, y: 1 },
  A: { x: -1, y: 0 },
  D: { x: 1, y: 0 }
};

function pointsEqual(a, b) {
  return a.x === b.x && a.y === b.y;
}

function isOppositeDirection(current, next) {
  return current.x + next.x === 0 && current.y + next.y === 0;
}

export function keyToDirection(key) {
  return DIRECTIONS[key] ?? null;
}

export function createInitialState(rng = Math.random) {
  const center = Math.floor(GRID_SIZE / 2);
  const snake = [
    { x: center, y: center },
    { x: center - 1, y: center },
    { x: center - 2, y: center }
  ];

  return {
    snake,
    direction: { x: 1, y: 0 },
    pendingDirection: { x: 1, y: 0 },
    food: spawnFood(snake, rng),
    score: 0,
    gameOver: false,
    paused: false
  };
}

export function setDirection(state, nextDirection) {
  if (!nextDirection || state.gameOver) {
    return state;
  }

  if (isOppositeDirection(state.direction, nextDirection)) {
    return state;
  }

  return {
    ...state,
    pendingDirection: nextDirection
  };
}

export function spawnFood(snake, rng = Math.random) {
  const occupied = new Set(snake.map((segment) => `${segment.x},${segment.y}`));
  const openCells = [];

  for (let y = 0; y < GRID_SIZE; y += 1) {
    for (let x = 0; x < GRID_SIZE; x += 1) {
      const key = `${x},${y}`;
      if (!occupied.has(key)) {
        openCells.push({ x, y });
      }
    }
  }

  if (openCells.length === 0) {
    return null;
  }

  const idx = Math.floor(rng() * openCells.length);
  return openCells[idx];
}

export function step(state, rng = Math.random) {
  if (state.gameOver || state.paused) {
    return state;
  }

  const direction = state.pendingDirection;
  const head = state.snake[0];
  const nextHead = {
    x: head.x + direction.x,
    y: head.y + direction.y
  };

  const hitsWall =
    nextHead.x < 0 ||
    nextHead.x >= GRID_SIZE ||
    nextHead.y < 0 ||
    nextHead.y >= GRID_SIZE;

  if (hitsWall) {
    return {
      ...state,
      direction,
      gameOver: true
    };
  }

  const willGrow = pointsEqual(nextHead, state.food);
  const bodyToCheck = willGrow ? state.snake : state.snake.slice(0, -1);
  const hitsSelf = bodyToCheck.some((segment) => pointsEqual(segment, nextHead));

  if (hitsSelf) {
    return {
      ...state,
      direction,
      gameOver: true
    };
  }

  const movedSnake = [nextHead, ...state.snake];
  if (!willGrow) {
    movedSnake.pop();
  }

  const nextFood = willGrow ? spawnFood(movedSnake, rng) : state.food;

  return {
    ...state,
    snake: movedSnake,
    direction,
    food: nextFood,
    score: state.score + (willGrow ? 1 : 0),
    gameOver: nextFood === null
  };
}

export function togglePause(state) {
  if (state.gameOver) {
    return state;
  }

  return {
    ...state,
    paused: !state.paused
  };
}
