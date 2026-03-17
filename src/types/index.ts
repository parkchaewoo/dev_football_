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

export interface UserProfile {
  uid: string;
  displayName: string;
  photoURL: string;
  email: string;
  createdAt: number;
  teams: string[];
}

export interface Team {
  id: string;
  name: string;
  description: string;
  leaderId: string;
  members: string[];
  inviteCode: string;
  createdAt: number;
}

export interface StrategyMeta {
  id: string;
  name: string;
  description: string;
  authorId: string;
  authorName: string;
  teamId: string;
  teamName: string;
  visibility: 'public' | 'private' | 'team';
  phases: Phase[];
  createdAt: number;
  updatedAt: number;
  likesCount: number;
}

export interface Comment {
  id: string;
  strategyId: string;
  authorId: string;
  authorName: string;
  authorPhoto: string;
  text: string;
  createdAt: number;
}

export interface BoardPost {
  id: string;
  title: string;
  content: string;
  authorId: string;
  authorName: string;
  teamId: string;
  isSecret: boolean;
  passwordHash: string;
  createdAt: number;
  updatedAt: number;
}
