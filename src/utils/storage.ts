import type { Strategy } from '../types';

const STORAGE_KEY = 'futsal-strategies';

export function saveStrategy(strategy: Strategy): void {
  const strategies = loadStrategies();
  const idx = strategies.findIndex((s) => s.id === strategy.id);
  if (idx >= 0) {
    strategies[idx] = strategy;
  } else {
    strategies.push(strategy);
  }
  localStorage.setItem(STORAGE_KEY, JSON.stringify(strategies));
}

export function loadStrategies(): Strategy[] {
  const data = localStorage.getItem(STORAGE_KEY);
  if (!data) return [];
  try {
    return JSON.parse(data);
  } catch {
    return [];
  }
}

export function deleteStrategy(id: string): void {
  const strategies = loadStrategies().filter((s) => s.id !== id);
  localStorage.setItem(STORAGE_KEY, JSON.stringify(strategies));
}

export function generateId(): string {
  return Date.now().toString(36) + Math.random().toString(36).slice(2, 8);
}
