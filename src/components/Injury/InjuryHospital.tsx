import { useState } from 'react';

interface InjuryInfo {
  icon: string;
  injuries: string[];
  description: string;
  hospitalKeywords: string[];
  firstAid: string;
  severityGuide: string;
}

const INJURY_DATA: Record<string, InjuryInfo> = {
  '발목': {
    icon: '🦶',
    injuries: ['발목 염좌 (접질림)', '아킬레스건 부상', '발목 골절'],
    description: '풋살에서 가장 흔한 부상입니다. 급격한 방향 전환이나 상대와의 접촉으로 발생합니다.',
    hospitalKeywords: ['정형외과', '스포츠의학과'],
    firstAid: 'RICE 처치 (Rest, Ice, Compression, Elevation) - 즉시 냉찜질하고 압박 붕대로 감싸세요.',
    severityGuide: '걸을 수 없을 정도면 응급실, 붓기와 통증이 있으면 정형외과 방문',
  },
  '무릎': {
    icon: '🦵',
    injuries: ['전방십자인대(ACL) 파열', '반월상연골 손상', '무릎 인대 염좌', '슬개골 탈구'],
    description: '급정지, 회전, 점프 착지 시 무릎에 큰 부하가 걸려 발생합니다.',
    hospitalKeywords: ['정형외과', '스포츠의학과', '무릎전문병원'],
    firstAid: '무릎을 구부리지 말고 고정하세요. 냉찜질 후 즉시 병원 방문을 권합니다.',
    severityGuide: "'뚝' 소리가 났거나 무릎이 불안정하면 즉시 정형외과 방문",
  },
  '허벅지': {
    icon: '🦿',
    injuries: ['햄스트링 파열/긴장', '대퇴사두근 좌상', '근육 경련'],
    description: '스프린트나 킥 동작에서 근육이 과도하게 늘어나 발생합니다.',
    hospitalKeywords: ['정형외과', '재활의학과', '스포츠의학과'],
    firstAid: '즉시 운동을 중단하고 냉찜질하세요. 스트레칭은 금물입니다.',
    severityGuide: '걸을 수 있으면 재활의학과, 극심한 통증이면 정형외과',
  },
  '어깨': {
    icon: '💪',
    injuries: ['어깨 탈구', '회전근개 손상', '쇄골 골절'],
    description: '골키퍼의 다이빙이나 넘어질 때 팔을 짚으면서 발생합니다.',
    hospitalKeywords: ['정형외과', '어깨전문병원'],
    firstAid: '탈구 시 억지로 맞추지 말고 응급실로 가세요.',
    severityGuide: '팔을 올릴 수 없으면 응급실, 통증만 있으면 정형외과',
  },
  '손목/손가락': {
    icon: '🤚',
    injuries: ['손목 염좌/골절', '손가락 골절', '손가락 탈구'],
    description: '넘어질 때 손을 짚거나, 골키퍼가 공을 막다가 발생합니다.',
    hospitalKeywords: ['정형외과', '수부외과'],
    firstAid: '부목으로 고정하고 냉찜질하세요.',
    severityGuide: '변형이 있으면 응급실, 부종과 통증만 있으면 정형외과',
  },
  '머리/얼굴': {
    icon: '🧠',
    injuries: ['뇌진탕', '코뼈 골절', '안면 타박상'],
    description: '머리끼리 충돌하거나 팔꿈치에 맞아 발생합니다.',
    hospitalKeywords: ['신경외과', '응급실', '이비인후과'],
    firstAid: '의식이 흐릿하거나 구토가 있으면 즉시 119에 연락하세요.',
    severityGuide: '의식 변화/구토이면 응급실, 코피가 멈추지 않으면 이비인후과',
  },
  '허리/등': {
    icon: '🔙',
    injuries: ['요추 염좌', '디스크 탈출', '근육 좌상'],
    description: '공을 차는 동작이나 몸싸움에서 허리에 무리가 가면 발생합니다.',
    hospitalKeywords: ['정형외과', '재활의학과', '척추전문병원'],
    firstAid: '무리하지 말고 편안한 자세로 안정하세요.',
    severityGuide: '다리 저림/힘빠짐이 있으면 즉시 정형외과',
  },
  '발/발가락': {
    icon: '👟',
    injuries: ['발가락 골절', '족저근막염', '발등 타박상'],
    description: '볼에 밟히거나 강한 슈팅 시 발에 충격이 가해져 발생합니다.',
    hospitalKeywords: ['정형외과', '족부전문병원'],
    firstAid: '신발을 벗고 냉찜질하세요. 체중을 싣지 마세요.',
    severityGuide: '걸을 수 없으면 정형외과, 경미한 통증은 며칠 관찰',
  },
};

export default function InjuryHospital({ onClose }: { onClose: () => void }) {
  const [selectedPart, setSelectedPart] = useState<string | null>(null);
  const [location, setLocation] = useState('');

  const data = selectedPart ? INJURY_DATA[selectedPart] : null;

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-800 rounded-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-700 sticky top-0 bg-gray-800 z-10">
          <h2 className="text-xl font-bold">🏥 부상 위치 병원 추천</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-white text-xl">×</button>
        </div>

        <div className="p-4">
          {/* Ad placeholder */}
          <div className="bg-gradient-to-r from-blue-900/50 to-blue-800/50 rounded-lg p-3 mb-4 text-center text-gray-400 text-sm">
            📢 광고 영역 — 스포츠 용품, 보호대, 테이핑 등
          </div>

          {/* Body part selector */}
          <h3 className="font-semibold mb-3">부상 부위 선택</h3>
          <div className="grid grid-cols-4 gap-2 mb-4">
            {Object.entries(INJURY_DATA).map(([name, info]) => (
              <button
                key={name}
                onClick={() => setSelectedPart(name)}
                className={`p-2 rounded-lg text-sm text-center transition ${
                  selectedPart === name
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-700 hover:bg-gray-600'
                }`}
              >
                {info.icon} {name}
              </button>
            ))}
          </div>

          {/* Injury details */}
          {data && (
            <>
              <div className="border-t border-gray-700 pt-4">
                <h3 className="text-lg font-semibold mb-2">{data.icon} {selectedPart} 부상 정보</h3>
                <p className="text-gray-300 mb-3">{data.description}</p>

                <h4 className="font-medium mb-1">흔한 부상 종류:</h4>
                <ul className="list-disc list-inside text-gray-300 mb-3">
                  {data.injuries.map((injury) => (
                    <li key={injury}>{injury}</li>
                  ))}
                </ul>

                <div className="bg-yellow-900/30 border border-yellow-700/50 rounded-lg p-3 mb-3">
                  <strong>응급 처치:</strong> {data.firstAid}
                </div>

                <div className="bg-blue-900/30 border border-blue-700/50 rounded-lg p-3 mb-4">
                  <strong>병원 선택 가이드:</strong> {data.severityGuide}
                </div>
              </div>

              {/* Hospital search */}
              <div className="border-t border-gray-700 pt-4">
                <h3 className="font-semibold mb-3">🗺️ 주변 병원 찾기</h3>
                <input
                  type="text"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  placeholder="현재 위치 (예: 강남, 잠실, 수원)"
                  className="w-full p-2 rounded bg-gray-700 border border-gray-600 mb-3 text-white"
                />

                <div className="space-y-2 mb-4">
                  {data.hospitalKeywords.map((keyword) => {
                    const searchQuery = location ? `${location} ${keyword}` : keyword;
                    const url = `https://map.naver.com/v5/search/${encodeURIComponent(searchQuery)}`;
                    return (
                      <div key={keyword} className="flex items-center justify-between bg-gray-700 rounded-lg p-2">
                        <span>🏥 {keyword}</span>
                        <a
                          href={url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="px-3 py-1 bg-green-600 rounded text-sm hover:bg-green-700"
                        >
                          네이버 지도에서 검색
                        </a>
                      </div>
                    );
                  })}
                </div>

                {location && (
                  <a
                    href={`https://map.naver.com/v5/search/${encodeURIComponent(`${location} 응급실`)}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="block w-full p-3 bg-red-600 rounded-lg text-center font-bold hover:bg-red-700"
                  >
                    🚨 응급실 검색 (네이버 지도)
                  </a>
                )}
              </div>
            </>
          )}

          {/* Ad placeholder bottom */}
          <div className="bg-gradient-to-r from-red-900/30 to-red-800/30 rounded-lg p-3 mt-4 text-center text-gray-400 text-sm">
            📢 광고 영역 — 스포츠 보험, 부상 예방 프로그램 등
          </div>
        </div>
      </div>
    </div>
  );
}
