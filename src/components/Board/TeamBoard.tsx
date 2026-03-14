import { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import {
  createPost, getTeamPosts, deletePost,
  canReadSecret, canManagePost,
} from '../../services/boardService';
import type { BoardPost, Team } from '../../types';

interface TeamBoardProps {
  team: Team;
  onClose: () => void;
}

export default function TeamBoard({ team, onClose }: TeamBoardProps) {
  const { profile } = useAuth();
  const [posts, setPosts] = useState<BoardPost[]>([]);
  const [view, setView] = useState<'list' | 'write' | 'detail'>('list');
  const [selectedPost, setSelectedPost] = useState<BoardPost | null>(null);
  const [loading, setLoading] = useState(true);

  // Write form state
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [isSecret, setIsSecret] = useState(false);
  const [password, setPassword] = useState('');

  const userId = profile?.uid || '';
  const teamData = { leaderId: team.leaderId, admins: (team as Record<string, unknown>).admins as string[] | undefined };

  useEffect(() => {
    loadPosts();
  }, [team.id]);

  async function loadPosts() {
    setLoading(true);
    try {
      const data = await getTeamPosts(team.id);
      setPosts(data);
    } catch {
      // ignore
    }
    setLoading(false);
  }

  async function handleSubmit() {
    if (!title.trim() || !content.trim()) return;
    await createPost(title.trim(), content.trim(), userId, profile!.displayName, team.id, isSecret, password);
    setTitle('');
    setContent('');
    setIsSecret(false);
    setPassword('');
    setView('list');
    loadPosts();
  }

  async function handleDelete(postId: string) {
    await deletePost(postId);
    setView('list');
    setSelectedPost(null);
    loadPosts();
  }

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-800 rounded-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-700 sticky top-0 bg-gray-800 z-10">
          <h2 className="text-xl font-bold">📋 {team.name} 게시판</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-white text-xl">×</button>
        </div>

        <div className="p-4">
          {/* LIST VIEW */}
          {view === 'list' && (
            <>
              <div className="flex justify-end mb-3">
                <button
                  onClick={() => setView('write')}
                  className="px-4 py-2 bg-blue-600 rounded-lg hover:bg-blue-700 text-sm font-medium"
                >
                  ✏️ 글쓰기
                </button>
              </div>

              {loading ? (
                <p className="text-center text-gray-400 py-8">로딩 중...</p>
              ) : posts.length === 0 ? (
                <p className="text-center text-gray-400 py-8">아직 게시글이 없습니다.</p>
              ) : (
                <div className="space-y-1">
                  {posts.map((post) => {
                    const canRead = canReadSecret(post, userId, teamData);
                    return (
                      <button
                        key={post.id}
                        onClick={() => {
                          if (canRead || !post.isSecret) {
                            setSelectedPost(post);
                            setView('detail');
                          }
                        }}
                        className="w-full text-left p-3 bg-gray-700 rounded-lg hover:bg-gray-600 transition"
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            {post.isSecret && <span className="text-yellow-400">🔒</span>}
                            <span className="font-medium">
                              {post.isSecret && !canRead ? '비밀글입니다' : post.title}
                            </span>
                          </div>
                          <span className="text-xs text-gray-400">
                            {new Date(post.createdAt).toLocaleDateString('ko-KR')}
                          </span>
                        </div>
                        <div className="text-sm text-gray-400 mt-1">{post.authorName}</div>
                      </button>
                    );
                  })}
                </div>
              )}
            </>
          )}

          {/* WRITE VIEW */}
          {view === 'write' && (
            <>
              <button
                onClick={() => setView('list')}
                className="text-gray-400 hover:text-white text-sm mb-3"
              >
                ← 목록으로
              </button>

              <div className="space-y-3">
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="제목"
                  className="w-full p-2 rounded bg-gray-700 border border-gray-600 text-white"
                />
                <textarea
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  placeholder="내용"
                  rows={8}
                  className="w-full p-2 rounded bg-gray-700 border border-gray-600 text-white resize-none"
                />
                <label className="flex items-center gap-2 text-sm">
                  <input
                    type="checkbox"
                    checked={isSecret}
                    onChange={(e) => setIsSecret(e.target.checked)}
                  />
                  🔒 비밀글 (운영진에게 요청/건의)
                </label>
                {isSecret && (
                  <>
                    <p className="text-xs text-gray-400">
                      비밀글은 작성자 본인과 팀 운영진만 열람할 수 있습니다.
                    </p>
                    <input
                      type="password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="비밀번호 (선택)"
                      className="w-full p-2 rounded bg-gray-700 border border-gray-600 text-white"
                    />
                  </>
                )}
                <button
                  onClick={handleSubmit}
                  className="w-full py-2 bg-blue-600 rounded-lg hover:bg-blue-700 font-medium"
                >
                  작성 완료
                </button>
              </div>
            </>
          )}

          {/* DETAIL VIEW */}
          {view === 'detail' && selectedPost && (
            <>
              <button
                onClick={() => { setView('list'); setSelectedPost(null); }}
                className="text-gray-400 hover:text-white text-sm mb-3"
              >
                ← 목록으로
              </button>

              <div>
                <h3 className="text-lg font-bold mb-1">
                  {selectedPost.isSecret && '🔒 '}
                  {selectedPost.title}
                </h3>
                <p className="text-sm text-gray-400 mb-4">
                  {selectedPost.authorName} · {new Date(selectedPost.createdAt).toLocaleString('ko-KR')}
                </p>

                {selectedPost.isSecret && canReadSecret(selectedPost, userId, teamData) && selectedPost.authorId !== userId && (
                  <div className="bg-blue-900/30 border border-blue-700/50 rounded-lg p-2 mb-3 text-sm">
                    운영진 권한으로 열람 중입니다.
                  </div>
                )}

                <div className="bg-gray-700 rounded-lg p-4 whitespace-pre-wrap">
                  {selectedPost.content}
                </div>

                {canManagePost(selectedPost, userId, teamData) && (
                  <div className="flex gap-2 mt-4">
                    <button
                      onClick={() => handleDelete(selectedPost.id)}
                      className="px-4 py-2 bg-red-600 rounded-lg hover:bg-red-700 text-sm"
                    >
                      🗑️ 삭제
                    </button>
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
