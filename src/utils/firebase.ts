import { initializeApp } from 'firebase/app';
import type { FirebaseApp } from 'firebase/app';
import { getDatabase } from 'firebase/database';
import type { Database } from 'firebase/database';

// Firebase config - replace with your own project config
const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY || '',
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN || '',
  databaseURL: import.meta.env.VITE_FIREBASE_DATABASE_URL || '',
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID || '',
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET || '',
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID || '',
  appId: import.meta.env.VITE_FIREBASE_APP_ID || '',
};

let app: FirebaseApp | null = null;
let db: Database | null = null;

export function getFirebaseDB(): Database | null {
  if (!firebaseConfig.apiKey) return null;
  if (!app) {
    app = initializeApp(firebaseConfig);
    db = getDatabase(app);
  }
  return db;
}

export function isFirebaseConfigured(): boolean {
  return Boolean(firebaseConfig.apiKey);
}
