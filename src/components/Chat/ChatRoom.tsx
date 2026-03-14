import { useState, useRef, useEffect } from 'react';
import { useChat } from '../../hooks/useChat';
import ChatMessageItem from './ChatMessage';

interface ChatRoomProps {
  strategyId?: string;
}

export default function ChatRoom({ strategyId }: ChatRoomProps) {
  const { messages, nickname, saveNickname, sendMessage, firebaseEnabled } = useChat(strategyId);
  const [input, setInput] = useState('');
  const [nicknameInput, setNicknameInput] = useState(nickname);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  if (!nickname) {
    return (
      <div className="flex flex-col items-center justify-center h-full p-4 bg-gray-900">
        <h3 className="text-lg font-bold text-white mb-4">닉네임 입력</h3>
        <input
          className="px-3 py-2 bg-gray-800 text-white rounded border border-gray-700 w-full max-w-xs mb-3"
          placeholder="닉네임을 입력하세요"
          value={nicknameInput}
          onChange={(e) => setNicknameInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && nicknameInput.trim() && saveNickname(nicknameInput.trim())}
        />
        <button
          onClick={() => nicknameInput.trim() && saveNickname(nicknameInput.trim())}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          시작하기
        </button>
        {!firebaseEnabled && (
          <p className="text-xs text-gray-500 mt-3 text-center">
            로컬 모드로 실행 중입니다.<br />
            Firebase를 설정하면 실시간 채팅이 가능합니다.
          </p>
        )}
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full bg-gray-900">
      <div className="p-2 border-b border-gray-700 flex items-center justify-between">
        <span className="text-sm text-gray-300">
          채팅 {firebaseEnabled ? '(실시간)' : '(로컬)'}
        </span>
        <span className="text-xs text-gray-500">{nickname}</span>
      </div>

      <div className="flex-1 overflow-y-auto p-3">
        {messages.length === 0 && (
          <p className="text-center text-gray-600 text-sm mt-8">
            전략에 대해 토론해보세요!
          </p>
        )}
        {messages.map((msg) => (
          <ChatMessageItem
            key={msg.id}
            message={msg}
            isOwn={msg.author === nickname}
          />
        ))}
        <div ref={messagesEndRef} />
      </div>

      <div className="p-2 border-t border-gray-700">
        <div className="flex gap-2">
          <input
            className="flex-1 px-3 py-1.5 bg-gray-800 text-white text-sm rounded border border-gray-700 outline-none focus:border-blue-500"
            placeholder="메시지를 입력하세요..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && input.trim()) {
                sendMessage(input);
                setInput('');
              }
            }}
          />
          <button
            onClick={() => {
              if (input.trim()) {
                sendMessage(input);
                setInput('');
              }
            }}
            className="px-3 py-1.5 bg-blue-600 text-white text-sm rounded hover:bg-blue-700"
          >
            전송
          </button>
        </div>
      </div>
    </div>
  );
}
