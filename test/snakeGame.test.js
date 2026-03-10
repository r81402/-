import test from 'node:test';
import assert from 'node:assert/strict';
import {
  GRID_SIZE,
  createInitialState,
  setDirection,
  spawnFood,
  step
} from '../src/snakeGame.js';

const fixedRng = (value) => () => value;

test('snake moves one cell each step in current direction', () => {
  const state = createInitialState(fixedRng(0));
  const next = step(state, fixedRng(0));

  assert.equal(next.snake[0].x, state.snake[0].x + 1);
  assert.equal(next.snake[0].y, state.snake[0].y);
  assert.equal(next.score, 0);
});

test('snake grows and score increments when eating food', () => {
  const state = createInitialState(fixedRng(0));
  const targetFood = {
    x: state.snake[0].x + 1,
    y: state.snake[0].y
  };

  const next = step({ ...state, food: targetFood }, fixedRng(0.5));

  assert.equal(next.snake.length, state.snake.length + 1);
  assert.equal(next.score, 1);
  assert.notDeepEqual(next.food, targetFood);
});

test('wall collision triggers game over', () => {
  const state = {
    ...createInitialState(fixedRng(0)),
    snake: [{ x: GRID_SIZE - 1, y: 0 }],
    direction: { x: 1, y: 0 },
    pendingDirection: { x: 1, y: 0 }
  };

  const next = step(state, fixedRng(0));
  assert.equal(next.gameOver, true);
});

test('cannot reverse into opposite direction immediately', () => {
  const state = createInitialState(fixedRng(0));
  const reversed = setDirection(state, { x: -1, y: 0 });
  assert.deepEqual(reversed.pendingDirection, state.pendingDirection);
});

test('spawnFood chooses only open cells', () => {
  const snake = [{ x: 0, y: 0 }];
  const food = spawnFood(snake, fixedRng(0));
  assert.notDeepEqual(food, snake[0]);
});
