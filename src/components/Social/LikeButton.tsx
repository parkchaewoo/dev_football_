import { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { toggleLike, hasLiked } from '../../services/socialService';

interface LikeButtonProps {
  strategyId: string;
  initialCount: number;
}

export default function LikeButton({ strategyId, initialCount }: LikeButtonProps) {
  const { user } = useAuth();
  const [liked, setLiked] = useState(false);
  const [count, setCount] = useState(initialCount);

  useEffect(() => {
    if (!user) return;
    hasLiked(strategyId, user.uid).then(setLiked);
  }, [strategyId, user]);

  const handleToggle = async () => {
    if (!user) return;
    const nowLiked = await toggleLike(strategyId, user.uid);
    setLiked(nowLiked);
    setCount((c) => c + (nowLiked ? 1 : -1));
  };

  return (
    <button
      onClick={handleToggle}
      className={`flex items-center gap-1 px-3 py-1 rounded-lg text-sm transition-colors ${
        liked ? 'bg-red-600/20 text-red-400' : 'bg-gray-700 text-gray-400 hover:text-red-400'
      }`}
    >
      {liked ? '♥' : '♡'} {count}
    </button>
  );
}
