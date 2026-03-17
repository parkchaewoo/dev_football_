import { useState } from 'react';

const ENV_TEMPLATE = `VITE_FIREBASE_API_KEY=여기에_입력
VITE_FIREBASE_AUTH_DOMAIN=여기에_입력
VITE_FIREBASE_DATABASE_URL=여기에_입력
VITE_FIREBASE_PROJECT_ID=여기에_입력
VITE_FIREBASE_STORAGE_BUCKET=여기에_입력
VITE_FIREBASE_MESSAGING_SENDER_ID=여기에_입력
VITE_FIREBASE_APP_ID=여기에_입력`;

const steps = [
  {
    title: '1. Firebase 프로젝트 생성',
    content: [
      'console.firebase.google.com 접속',
      '"프로젝트 추가" 클릭',
      '프로젝트 이름 입력 (예: futsal-tactics)',
      'Google 애널리틱스는 끄셔도 됩니다 (무료 유지)',
      '"프로젝트 만들기" 클릭',
    ],
  },
  {
    title: '2. 웹 앱 등록',
    content: [
      '프로젝트 대시보드에서 "</>" (웹) 아이콘 클릭',
      '앱 닉네임 입력 (예: futsal-web)',
      '"앱 등록" 클릭',
      'firebaseConfig 객체가 표시됩니다 — 이 값들을 .env 파일에 복사',
    ],
  },
  {
    title: '3. Authentication 설정',
    content: [
      '왼쪽 메뉴 → "빌드" → "Authentication"',
      '"시작하기" 클릭',
      '"로그인 방법" 탭 → "Google" → "사용 설정" → 저장',
    ],
  },
  {
    title: '4. Firestore Database 설정',
    content: [
      '왼쪽 메뉴 → "빌드" → "Firestore Database"',
      '"데이터베이스 만들기" 클릭',
      '위치: asia-northeast3 (서울) 선택',
      '"테스트 모드에서 시작" 선택 → "만들기"',
    ],
  },
  {
    title: '5. Realtime Database 설정',
    content: [
      '왼쪽 메뉴 → "빌드" → "Realtime Database"',
      '"데이터베이스 만들기" 클릭',
      '위치: 싱가포르(asia-southeast1) 선택',
      '"테스트 모드에서 시작" → "사용 설정"',
    ],
  },
  {
    title: '6. .env 파일 생성',
    content: [
      '프로젝트 루트에 .env 파일 생성',
      '아래 템플릿을 복사하여 Firebase 콘솔의 값으로 교체',
      '앱을 재시작하면 완료!',
    ],
  },
];

export default function FirebaseSetupGuide() {
  const [copied, setCopied] = useState(false);
  const [openStep, setOpenStep] = useState(0);

  const handleCopy = () => {
    navigator.clipboard.writeText(ENV_TEMPLATE);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="w-full h-screen flex items-center justify-center bg-gray-900 overflow-y-auto py-8">
      <div className="bg-gray-800 rounded-2xl p-6 w-full max-w-lg shadow-2xl mx-4">
        <div className="text-center mb-6">
          <div className="text-5xl mb-3">&#9917;</div>
          <h1 className="text-xl font-bold text-white mb-1">풋살 전술 보드</h1>
          <p className="text-gray-400 text-sm">
            Firebase 설정이 필요합니다 (완전 무료)
          </p>
        </div>

        <div className="bg-green-900/30 border border-green-700/50 rounded-lg p-3 mb-4 text-sm">
          <p className="text-green-400 font-medium mb-1">Spark (무료) 플랜</p>
          <p className="text-green-300/70 text-xs">
            신용카드 등록 불필요 / 추가 과금 없음 / 한도 초과 시 서비스만 일시 중단
          </p>
        </div>

        <div className="flex flex-col gap-2">
          {steps.map((step, i) => (
            <div key={i} className="border border-gray-700 rounded-lg overflow-hidden">
              <button
                onClick={() => setOpenStep(openStep === i ? -1 : i)}
                className="w-full flex items-center justify-between px-3 py-2 text-sm font-medium text-left hover:bg-gray-700/50 transition-colors"
              >
                <span className={openStep === i ? 'text-blue-400' : 'text-gray-300'}>
                  {step.title}
                </span>
                <span className="text-gray-500 text-xs">
                  {openStep === i ? '▲' : '▼'}
                </span>
              </button>
              {openStep === i && (
                <div className="px-3 pb-3">
                  <ol className="flex flex-col gap-1.5">
                    {step.content.map((line, j) => (
                      <li key={j} className="text-gray-400 text-xs flex gap-2">
                        <span className="text-gray-600 shrink-0">{j + 1}.</span>
                        {line}
                      </li>
                    ))}
                  </ol>
                  {i === steps.length - 1 && (
                    <div className="mt-3">
                      <div className="bg-gray-900 rounded p-2 text-xs font-mono text-gray-300 whitespace-pre">
                        {ENV_TEMPLATE}
                      </div>
                      <button
                        onClick={handleCopy}
                        className="mt-2 px-3 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700"
                      >
                        {copied ? '복사됨!' : '.env 템플릿 복사'}
                      </button>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>

        <p className="text-gray-600 text-xs mt-4 text-center">
          설정 완료 후 앱을 새로고침하세요
        </p>
      </div>
    </div>
  );
}
