import { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { addComment, getComments, deleteComment } from '../../services/socialService';
import type { Comment } from '../../types';

interface CommentSectionProps {
  strategyId: string;
}

export default function CommentSection({ strategyId }: CommentSectionProps) {
  const { user, profile } = useAuth();
  const [comments, setComments] = useState<Comment[]>([]);
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getComments(strategyId).then((c) => {
      setComments(c);
      setLoading(false);
    });
  }, [strategyId]);

  const handleSubmit = async () => {
    if (!text.trim() || !user || !profile) return;
    const comment = await addComment(
      strategyId,
      user.uid,
      profile.displayName,
      profile.photoURL,
      text.trim()
    );
    setComments((prev) => [...prev, comment]);
    setText('');
  };

  const handleDelete = async (id: string) => {
    await deleteComment(id);
    setComments((prev) => prev.filter((c) => c.id !== id));
  };

  return (
    <div className="flex flex-col gap-2">
      <h3 className="text-sm font-medium text-gray-300">
        댓글 {comments.length > 0 && `(${comments.length})`}
      </h3>

      {loading ? (
        <p className="text-gray-500 text-xs">로딩 중...</p>
      ) : (
        <div className="flex flex-col gap-1 max-h-48 overflow-y-auto">
          {comments.map((c) => (
            <div key={c.id} className="flex items-start gap-2 p-2 bg-gray-700/50 rounded text-xs">
              <div className="flex-1">
                <span className="text-blue-400 font-medium">{c.authorName}</span>
                <span className="text-gray-300 ml-2">{c.text}</span>
                <span className="text-gray-600 ml-2">
                  {new Date(c.createdAt).toLocaleDateString('ko-KR')}
                </span>
              </div>
              {user?.uid === c.authorId && (
                <button
                  onClick={() => handleDelete(c.id)}
                  className="text-gray-500 hover:text-red-400 shrink-0"
                >
                  ×
                </button>
              )}
            </div>
          ))}
        </div>
      )}

      <div className="flex gap-2">
        <input
          className="flex-1 px-2 py-1 bg-gray-700 text-white text-sm rounded border border-gray-600 outline-none focus:border-blue-500"
          placeholder="댓글을 입력하세요..."
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
        />
        <button
          onClick={handleSubmit}
          disabled={!text.trim()}
          className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-40"
        >
          등록
        </button>
      </div>
    </div>
  );
}
