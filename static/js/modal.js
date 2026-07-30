/**
 * 카테고리별 이수/미이수 상세 모달을 띄우는 함수
 * @param {string} categoryId - 'total', 'major_req', 'major_elec', 'general'
 */
async function openCourseModal(categoryId) {
    const modal = document.getElementById('courseModal');
    const modalTitle = document.getElementById('modalTitle');
    const completedList = document.getElementById('modalCompletedList');
    const remainingList = document.getElementById('modalRemainingList');
    const remainingSection = document.getElementById('modalRemainingSection');

    // 1. 기존 데이터 초기화 (이전 팝업 내용 잔재 제거)
    modalTitle.innerHTML = '<i class="fa-solid fa-spinner animate-spin text-indigo-600"></i> 불러오는 중...';
    completedList.innerHTML = '<p class="text-slate-400 text-sm">로딩 중...</p>';
    remainingList.innerHTML = '';
    remainingSection.classList.add('hidden');

    // 모달 먼저 열기
    modal.classList.remove('hidden');

    try {
        // 2. 캐시 방지를 위해 타임스탬프 쿼리 스트링 추가 요청
        const response = await fetch(`/api/credit-detail/${categoryId}?_t=${new Date().getTime()}`);
        const result = await response.json();

        if (result.status !== 'success') {
            alert(result.message || '상세 내역을 가져오는데 실패했습니다.');
            closeCourseModal();
            return;
        }

        const data = result.data;

        // 3. 타이틀 변경
        modalTitle.innerHTML = `<i class="fa-solid fa-list-check text-indigo-600"></i> ${data.title}`;

        // 4. 이수 과목 렌더링
        completedList.innerHTML = '';
        if (data.completed && data.completed.length > 0) {
            data.completed.forEach(course => {
                const item = document.createElement('div');
                item.className = 'bg-white p-3 rounded-lg border border-slate-200 shadow-sm flex justify-between items-center';
                item.innerHTML = `
                    <div>
                        <div class="font-bold text-slate-800 text-sm">${course.name}</div>
                        <div class="text-xs text-slate-400">${course.category || '이수 완료'}</div>
                    </div>
                    <span class="bg-emerald-100 text-emerald-800 text-xs font-bold px-2.5 py-1 rounded-full">
                        ${course.credit}학점
                    </span>
                `;
                completedList.appendChild(item);
            });
        } else {
            completedList.innerHTML = '<p class="text-slate-400 text-sm col-span-2 text-center py-4">이수한 과목이 없습니다.</p>';
        }

        // 5. 미이수 과목 렌더링 (미이수 항목이 존재하는 카테고리만)
        remainingList.innerHTML = '';
        if (data.remaining && data.remaining.length > 0) {
            remainingSection.classList.remove('hidden');
            data.remaining.forEach(course => {
                const item = document.createElement('div');
                item.className = 'bg-white p-3 rounded-lg border border-rose-200 shadow-sm flex justify-between items-center';
                item.innerHTML = `
                    <div>
                        <div class="font-bold text-slate-800 text-sm">${course.name}</div>
                        <div class="text-xs text-rose-500 font-medium">${course.category || '미이수'}</div>
                    </div>
                    <span class="bg-rose-100 text-rose-800 text-xs font-bold px-2.5 py-1 rounded-full">
                        ${course.credit}학점
                    </span>
                `;
                remainingList.appendChild(item);
            });
        } else {
            remainingSection.classList.add('hidden');
        }

    } catch (error) {
        console.error('Modal Fetch Error:', error);
        alert('데이터를 불러오는 도중 오류가 발생했습니다.');
        closeCourseModal();
    }
}

// 모달 닫기 함수
function closeCourseModal() {
    const modal = document.getElementById('courseModal');
    if (modal) {
        modal.classList.add('hidden');
    }
}