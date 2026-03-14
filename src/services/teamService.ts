import {
  doc, collection, addDoc, getDoc, getDocs, updateDoc, deleteDoc,
  query, where, arrayUnion, arrayRemove
} from 'firebase/firestore';
import { getFirebaseFirestore } from '../utils/firebase';
import type { Team } from '../types';

function generateInviteCode(): string {
  return Math.random().toString(36).slice(2, 8).toUpperCase();
}

export async function createTeam(
  name: string,
  description: string,
  userId: string
): Promise<Team> {
  const fs = getFirebaseFirestore()!;
  const team: Omit<Team, 'id'> = {
    name,
    description,
    leaderId: userId,
    members: [userId],
    inviteCode: generateInviteCode(),
    createdAt: Date.now(),
  };
  const ref = await addDoc(collection(fs, 'teams'), team);
  await updateDoc(doc(fs, 'users', userId), {
    teams: arrayUnion(ref.id),
  });
  return { id: ref.id, ...team };
}

export async function joinTeamByCode(
  inviteCode: string,
  userId: string
): Promise<Team | null> {
  const fs = getFirebaseFirestore()!;
  const q = query(collection(fs, 'teams'), where('inviteCode', '==', inviteCode));
  const snap = await getDocs(q);
  if (snap.empty) return null;

  const teamDoc = snap.docs[0];
  const team = { id: teamDoc.id, ...teamDoc.data() } as Team;

  if (team.members.includes(userId)) return team;

  await updateDoc(doc(fs, 'teams', team.id), {
    members: arrayUnion(userId),
  });
  await updateDoc(doc(fs, 'users', userId), {
    teams: arrayUnion(team.id),
  });

  return { ...team, members: [...team.members, userId] };
}

export async function getMyTeams(userId: string): Promise<Team[]> {
  const fs = getFirebaseFirestore()!;
  const q = query(collection(fs, 'teams'), where('members', 'array-contains', userId));
  const snap = await getDocs(q);
  return snap.docs.map((d) => ({ id: d.id, ...d.data() }) as Team);
}

export async function getTeam(teamId: string): Promise<Team | null> {
  const fs = getFirebaseFirestore()!;
  const snap = await getDoc(doc(fs, 'teams', teamId));
  if (!snap.exists()) return null;
  return { id: snap.id, ...snap.data() } as Team;
}

export async function leaveTeam(teamId: string, userId: string): Promise<void> {
  const fs = getFirebaseFirestore()!;
  await updateDoc(doc(fs, 'teams', teamId), {
    members: arrayRemove(userId),
  });
  await updateDoc(doc(fs, 'users', userId), {
    teams: arrayRemove(teamId),
  });
}

export async function deleteTeam(teamId: string): Promise<void> {
  const fs = getFirebaseFirestore()!;
  const teamSnap = await getDoc(doc(fs, 'teams', teamId));
  if (!teamSnap.exists()) return;
  const team = teamSnap.data() as Team;
  for (const uid of team.members) {
    await updateDoc(doc(fs, 'users', uid), {
      teams: arrayRemove(teamId),
    });
  }
  await deleteDoc(doc(fs, 'teams', teamId));
}
