import {
  doc, collection, addDoc, getDoc, getDocs, updateDoc, deleteDoc,
  query, where, orderBy, limit, increment
} from 'firebase/firestore';
import { getFirebaseFirestore } from '../utils/firebase';
import { getCached, invalidateCache } from '../utils/firestoreCache';
import type { StrategyMeta, Phase } from '../types';

export async function saveStrategyToFirestore(
  strategy: {
    name: string;
    description: string;
    phases: Phase[];
  },
  authorId: string,
  authorName: string,
  teamId: string,
  teamName: string,
  visibility: 'public' | 'private' | 'team',
  existingId?: string
): Promise<string> {
  const fs = getFirebaseFirestore()!;
  const data = {
    name: strategy.name,
    description: strategy.description,
    authorId,
    authorName,
    teamId,
    teamName,
    visibility,
    phases: JSON.parse(JSON.stringify(strategy.phases)),
    updatedAt: Date.now(),
    ...(existingId ? {} : { createdAt: Date.now(), likesCount: 0 }),
  };

  if (existingId) {
    await updateDoc(doc(fs, 'strategies', existingId), data);
    invalidateCache('strategies:');
    return existingId;
  }
  const ref = await addDoc(collection(fs, 'strategies'), data);
  invalidateCache('strategies:');
  return ref.id;
}

export async function getTeamStrategies(teamId: string): Promise<StrategyMeta[]> {
  return getCached(`strategies:team:${teamId}`, async () => {
    const fs = getFirebaseFirestore()!;
    const q = query(
      collection(fs, 'strategies'),
      where('teamId', '==', teamId),
      orderBy('updatedAt', 'desc')
    );
    const snap = await getDocs(q);
    return snap.docs.map((d) => ({ id: d.id, ...d.data() }) as StrategyMeta);
  }, 3 * 60 * 1000);
}

export async function getPublicStrategies(): Promise<StrategyMeta[]> {
  return getCached('strategies:public', async () => {
    const fs = getFirebaseFirestore()!;
    const q = query(
      collection(fs, 'strategies'),
      where('visibility', '==', 'public'),
      orderBy('updatedAt', 'desc'),
      limit(30)
    );
    const snap = await getDocs(q);
    return snap.docs.map((d) => ({ id: d.id, ...d.data() }) as StrategyMeta);
  }, 5 * 60 * 1000);
}

export async function getStrategy(id: string): Promise<StrategyMeta | null> {
  const fs = getFirebaseFirestore()!;
  const snap = await getDoc(doc(fs, 'strategies', id));
  if (!snap.exists()) return null;
  return { id: snap.id, ...snap.data() } as StrategyMeta;
}

export async function deleteStrategyFromFirestore(id: string): Promise<void> {
  const fs = getFirebaseFirestore()!;
  await deleteDoc(doc(fs, 'strategies', id));
  invalidateCache('strategies:');
}

export async function incrementLikes(strategyId: string, delta: number): Promise<void> {
  const fs = getFirebaseFirestore()!;
  await updateDoc(doc(fs, 'strategies', strategyId), {
    likesCount: increment(delta),
  });
}
