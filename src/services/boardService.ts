import {
  doc, collection, addDoc, getDocs, getDoc, deleteDoc, updateDoc,
  query, where, orderBy, limit
} from 'firebase/firestore';
import { getFirebaseFirestore } from '../utils/firebase';
import { getCached, invalidateCache } from '../utils/firestoreCache';
import type { BoardPost } from '../types';

function hashPassword(password: string): string {
  // Simple hash for client-side — matches Python's SHA256
  // In production, use a proper crypto library
  let hash = 0;
  for (let i = 0; i < password.length; i++) {
    const char = password.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash;
  }
  return Math.abs(hash).toString(16);
}

export async function createPost(
  title: string,
  content: string,
  authorId: string,
  authorName: string,
  teamId: string,
  isSecret: boolean = false,
  password: string = ''
): Promise<BoardPost> {
  const fs = getFirebaseFirestore()!;
  const postData: Omit<BoardPost, 'id'> = {
    title,
    content,
    authorId,
    authorName,
    teamId,
    isSecret,
    passwordHash: isSecret && password ? hashPassword(password) : '',
    createdAt: Date.now(),
    updatedAt: Date.now(),
  };
  const ref = await addDoc(collection(fs, 'board_posts'), postData);
  invalidateCache(`posts:${teamId}`);
  return { id: ref.id, ...postData };
}

export async function getTeamPosts(teamId: string): Promise<BoardPost[]> {
  return getCached(`posts:${teamId}`, async () => {
    const fs = getFirebaseFirestore()!;
    const q = query(
      collection(fs, 'board_posts'),
      where('teamId', '==', teamId),
      orderBy('createdAt', 'desc'),
      limit(50)
    );
    const snap = await getDocs(q);
    return snap.docs.map((d) => ({ id: d.id, ...d.data() }) as BoardPost);
  }, 3 * 60 * 1000);
}

export async function getPost(postId: string): Promise<BoardPost | null> {
  const fs = getFirebaseFirestore()!;
  const snap = await getDoc(doc(fs, 'board_posts', postId));
  if (!snap.exists()) return null;
  return { id: snap.id, ...snap.data() } as BoardPost;
}

export async function updatePost(
  postId: string,
  title: string,
  content: string,
  isSecret: boolean = false,
  password: string = ''
): Promise<void> {
  const fs = getFirebaseFirestore()!;
  const updateData: Record<string, unknown> = {
    title,
    content,
    isSecret,
    updatedAt: Date.now(),
  };
  if (isSecret && password) {
    updateData.passwordHash = hashPassword(password);
  } else if (!isSecret) {
    updateData.passwordHash = '';
  }
  await updateDoc(doc(fs, 'board_posts', postId), updateData);
  invalidateCache('posts:');
}

export async function deletePost(postId: string): Promise<void> {
  const fs = getFirebaseFirestore()!;
  await deleteDoc(doc(fs, 'board_posts', postId));
  invalidateCache('posts:');
}

export function canReadSecret(
  post: BoardPost,
  userId: string,
  team: { leaderId: string; admins?: string[] } | null
): boolean {
  if (!post.isSecret) return true;
  if (post.authorId === userId) return true;
  if (team) {
    if (team.leaderId === userId) return true;
    if (team.admins?.includes(userId)) return true;
  }
  return false;
}

export function canManagePost(
  post: BoardPost,
  userId: string,
  team: { leaderId: string; admins?: string[] } | null
): boolean {
  if (post.authorId === userId) return true;
  if (team) {
    if (team.leaderId === userId) return true;
    if (team.admins?.includes(userId)) return true;
  }
  return false;
}
