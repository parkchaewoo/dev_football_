import type { ChatMessage as ChatMessageType } from '../../types';

interface ChatMessageProps {
  message: ChatMessageType;
  isOwn: boolean;
}

export default function ChatMessageItem({ message, isOwn }: ChatMessageProps) {
  const time = new Date(message.timestamp).toLocaleTimeString('ko-KR', {
    hour: '2-digit',
    minute: '2-digit',
  });

  return (
    <div className={`flex flex-col ${isOwn ? 'items-end' : 'items-start'} mb-2`}>
      <span className="text-[10px] text-gray-500 mb-0.5">
        {message.author} · {time}
      </span>
      <div
        className={`px-3 py-1.5 rounded-lg text-sm max-w-[80%] break-words ${
          isOwn
            ? 'bg-blue-600 text-white'
            : 'bg-gray-700 text-gray-200'
        }`}
      >
        {message.text}
      </div>
    </div>
  );
}
