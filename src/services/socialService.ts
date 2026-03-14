import {
  doc, collection, addDoc, getDocs, getDoc, deleteDoc, setDoc,
  query, where, orderBy
} from 'firebase/firestore';
import { getFirebaseFirestore } from '../utils/firebase';
import { incrementLikes } from './strategyService';
import type { Comment } from '../types';

export async function addComment(
  strategyId: string,
  authorId: string,
  authorName: string,
  authorPhoto: string,
  text: string
): Promise<Comment> {
  const fs = getFirebaseFirestore()!;
  const comment: Omit<Comment, 'id'> = {
    strategyId,
    authorId,
    authorName,
    authorPhoto,
    text,
    createdAt: Date.now(),
  };
  const ref = await addDoc(collection(fs, 'comments'), comment);
  return { id: ref.id, ...comment };
}

export async function getComments(strategyId: string): Promise<Comment[]> {
  const fs = getFirebaseFirestore()!;
  const q = query(
    collection(fs, 'comments'),
    where('strategyId', '==', strategyId),
    orderBy('createdAt', 'asc')
  );
  const snap = await getDocs(q);
  return snap.docs.map((d) => ({ id: d.id, ...d.data() }) as Comment);
}

export async function deleteComment(commentId: string): Promise<void> {
  const fs = getFirebaseFirestore()!;
  await deleteDoc(doc(fs, 'comments', commentId));
}

export async function toggleLike(
  strategyId: string,
  userId: string
): Promise<boolean> {
  const fs = getFirebaseFirestore()!;
  const likeId = `${strategyId}__${userId}`;
  const ref = doc(fs, 'likes', likeId);
  const snap = await getDoc(ref);

  if (snap.exists()) {
    await deleteDoc(ref);
    await incrementLikes(strategyId, -1);
    return false;
  } else {
    await setDoc(ref, {
      strategyId,
      userId,
      createdAt: Date.now(),
    });
    await incrementLikes(strategyId, 1);
    return true;
  }
}

export async function hasLiked(
  strategyId: string,
  userId: string
): Promise<boolean> {
  const fs = getFirebaseFirestore()!;
  const likeId = `${strategyId}__${userId}`;
  const snap = await getDoc(doc(fs, 'likes', likeId));
  return snap.exists();
}
