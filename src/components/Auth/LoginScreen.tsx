import { useAuth } from '../../contexts/AuthContext';
import { isFirebaseConfigured } from '../../utils/firebase';
import FirebaseSetupGuide from '../Guide/FirebaseSetupGuide';

export default function LoginScreen() {
  const { signInWithGoogle, loading } = useAuth();

  if (!isFirebaseConfigured()) {
    return <FirebaseSetupGuide />;
  }

  if (loading) {
    return (
      <div className="w-full h-screen flex items-center justify-center bg-gray-900 text-white">
        <div className="text-xl">로딩 중...</div>
      </div>
    );
  }

  return (
    <div className="w-full h-screen flex items-center justify-center bg-gray-900">
      <div className="bg-gray-800 rounded-2xl p-8 w-full max-w-sm text-center shadow-2xl">
        <div className="text-6xl mb-4">&#9917;</div>
        <h1 className="text-2xl font-bold text-white mb-2">풋살 전술 보드</h1>
        <p className="text-gray-400 text-sm mb-8">
          팀원들과 전술을 만들고 공유하세요
        </p>

        <button
          onClick={signInWithGoogle}
          className="w-full flex items-center justify-center gap-3 px-4 py-3 bg-white text-gray-800 rounded-xl font-medium hover:bg-gray-100 transition-colors"
        >
          <svg width="20" height="20" viewBox="0 0 48 48">
            <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/>
            <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/>
            <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/>
            <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/>
          </svg>
          Google로 로그인
        </button>

        <p className="text-gray-500 text-xs mt-6">
          비밀번호 없이 간편하게 시작하세요
        </p>
      </div>
    </div>
  );
}
