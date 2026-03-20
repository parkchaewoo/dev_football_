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

// Highlight Generator Types
export interface HighlightClip {
  id: string;
  startTime: number;
  endTime: number;
  label: string;
  type: 'auto-audio' | 'auto-motion' | 'manual';
  confidence: number; // 0~1
  thumbnail?: string; // data URL
}

export interface HighlightSettings {
  audioThreshold: number;     // 0~1, volume spike sensitivity
  motionThreshold: number;    // 0~1, scene change sensitivity
  clipPaddingBefore: number;  // seconds before detected moment
  clipPaddingAfter: number;   // seconds after detected moment
  minClipDuration: number;    // minimum clip length in seconds
  mergeGap: number;           // merge clips closer than this (seconds)
}

export interface AnalysisProgress {
  phase: 'idle' | 'analyzing-audio' | 'analyzing-video' | 'merging' | 'done';
  percent: number;
}
