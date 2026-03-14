export interface Position3D {
  x: number;
  y: number; // height (aerial)
  z: number;
}

export interface Player {
  id: string;
  team: 'home' | 'away';
  number: number;
  position: Position3D;
}

export interface Frame {
  id: string;
  players: Player[];
  ballPosition: Position3D;
}

export interface Phase {
  id: string;
  name: string;
  description: string;
  frames: Frame[];
  order: number;
}

export interface Strategy {
  id: string;
  name: string;
  description: string;
  phases: Phase[];
  createdAt: number;
}

export interface ChatMessage {
  id: string;
  author: string;
  text: string;
  timestamp: number;
  strategyId?: string;
  phaseId?: string;
}
