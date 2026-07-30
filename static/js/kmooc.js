/**
 * kmooc.js - K-MOOC 강좌 추천 로직 (독립 실행 파일)
 */

// K-MOOC API 요청 및 HTML 렌더링 함수
async function loadKmoocRecommendations(categoryId) {
    const kmoocSection = document.getElementById('kmoocSection');
    const kmoocList = document.getElementById('kmoocList');

    if (!kmoocSection || !kmoocList) return;

    // 카테고리별 검색 키워드 자동 지정
    let keyword = '컴퓨터';
    if (categoryId === 'general') keyword = '교양';
    else if (categoryId === 'major_req' || categoryId === 'major_elec') keyword = '소프트웨어';

    // UI 로딩 상태 표시
    kmoocList.innerHTML = '<p class="text-xs text-slate-400 col-span-2 py-2">대체 추천 강좌 탐색 중...</p>';
    kmoocSection.classList.remove('hidden');

    try {
        const response = await fetch(`/api/kmooc-recommend?keyword=${encodeURIComponent(keyword)}`);
        const resData = await response.json();

        if (resData.status === 'success' && resData.data.length > 0) {
            kmoocList.innerHTML = '';
            resData.data.forEach(course => {
                const card = document.createElement('a');
                card.href = course.url;
                card.target = '_blank';
                card.className = 'block p-3 bg-indigo-50/50 hover:bg-indigo-100/70 border border-indigo-100 rounded-xl transition group';
                card.innerHTML = `
                    <div class="flex justify-between items-start gap-2">
                        <div>
                            <div class="font-bold text-xs text-indigo-950 group-hover:text-indigo-600 transition-colors line-clamp-1">
                                ${course.title}
                            </div>
                            <div class="text-[11px] text-slate-500 mt-0.5">${course.org_name}</div>
                        </div>
                        <span class="text-[10px] font-bold text-indigo-600 bg-white px-2 py-1 rounded shadow-sm whitespace-nowrap">
                            수강 <i class="fa-solid fa-arrow-up-right-from-square text-[9px]"></i>
                        </span>
                    </div>
                `;
                kmoocList.appendChild(card);
            });
        } else {
            kmoocList.innerHTML = '<p class="text-xs text-slate-400 col-span-2">추천 가능한 K-MOOC 강좌가 없습니다.</p>';
        }
    } catch (err) {
        console.error('K-MOOC 로딩 중 오류:', err);
        kmoocSection.classList.add('hidden');
    }
}

// 기존 main.js의 openCourseModal 함수가 실행된 후 K-MOOC 로직이 자동으로 이어서 실행되도록 바인딩
document.addEventListener('DOMContentLoaded', () => {
    if (typeof openCourseModal === 'function') {
        const originalOpenModal = openCourseModal;
        
        // 기존 openCourseModal 함수를 덮어씌워 확장
        window.openCourseModal = async function(categoryId) {
            // 1. 기존 모달 오픈 로직 실행
            await originalOpenModal(categoryId);
            // 2. K-MOOC 강좌 추천 로직 추가 실행
            loadKmoocRecommendations(categoryId);
        };
    }
});