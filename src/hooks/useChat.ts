import { useState, useEffect, useCallback } from 'react';
import { ref, push, onValue, query, orderByChild, limitToLast } from 'firebase/database';
import type { ChatMessage } from '../types';
import { getFirebaseDB, isFirebaseConfigured } from '../utils/firebase';
import { generateId } from '../utils/storage';

const LOCAL_CHAT_KEY = 'futsal-chat';

export function useChat(strategyId?: string) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [nickname, setNickname] = useState(() => {
    return localStorage.getItem('futsal-nickname') || '';
  });

  const firebaseEnabled = isFirebaseConfigured();

  // Load messages
  useEffect(() => {
    if (firebaseEnabled) {
      const db = getFirebaseDB();
      if (!db) return;
      const chatRef = ref(db, 'chat');
      const chatQuery = query(chatRef, orderByChild('timestamp'), limitToLast(50));
      const unsubscribe = onValue(chatQuery, (snapshot) => {
        const data = snapshot.val();
        if (data) {
          const msgs = Object.values(data) as ChatMessage[];
          setMessages(msgs.sort((a, b) => a.timestamp - b.timestamp));
        }
      });
      return () => unsubscribe();
    } else {
      // Local mode
      const data = localStorage.getItem(LOCAL_CHAT_KEY);
      if (data) {
        try {
          setMessages(JSON.parse(data));
        } catch { /* ignore */ }
      }
    }
  }, [firebaseEnabled]);

  const saveNickname = useCallback((name: string) => {
    setNickname(name);
    localStorage.setItem('futsal-nickname', name);
  }, []);

  const sendMessage = useCallback(
    (text: string, phaseId?: string) => {
      if (!nickname || !text.trim()) return;

      const message: ChatMessage = {
        id: generateId(),
        author: nickname,
        text: text.trim(),
        timestamp: Date.now(),
        strategyId,
        phaseId,
      };

      if (firebaseEnabled) {
        const db = getFirebaseDB();
        if (db) {
          const chatRef = ref(db, 'chat');
          push(chatRef, message);
        }
      } else {
        // Local mode
        setMessages((prev) => {
          const updated = [...prev, message];
          localStorage.setItem(LOCAL_CHAT_KEY, JSON.stringify(updated));
          return updated;
        });
      }
    },
    [nickname, strategyId, firebaseEnabled]
  );

  return {
    messages,
    nickname,
    saveNickname,
    sendMessage,
    firebaseEnabled,
  };
}
