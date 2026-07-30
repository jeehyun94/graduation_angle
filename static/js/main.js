/**
 * main.js - 졸업 가능성 진단 및 UI 제어
 */

// 1. 졸업 가능성 진단 요청 함수
async function runDiagnosis() {
    const studentIdElem = document.getElementById('studentId');
    const studentId = studentIdElem ? studentIdElem.value.trim() : '';
    const semester = document.getElementById('semester') ? document.getElementById('semester').value : '1';

    if (!studentId) {
        alert("학번 정보를 찾을 수 없습니다.");
        return;
    }

    const loadingElem = document.getElementById('loading');
    const resultSection = document.getElementById('resultSection');

    if (loadingElem) loadingElem.classList.remove('hidden');
    if (resultSection) resultSection.classList.add('hidden');

    try {
        // diagnose.py의 /api/diagnose 라우트로 POST 요청
        const response = await fetch('/api/diagnose', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                student_id: studentId,
                semester: parseInt(semester)
            })
        });

        const resData = await response.json();

        if (!response.ok || resData.status === "error") {
            showErrorCard(resData.message || '진단 정보를 불러올 수 없습니다.');
            return;
        }

        // 백엔드에서 반환된 data 객체
        const diagnosisData = resData.data;
        renderResults(diagnosisData);

    } catch (err) {
        console.error("진단 호출 중 에러 발생:", err);
        showErrorCard('진단 로직 처리 중 시스템 오류가 발생했습니다.');
    } finally {
        if (loadingElem) loadingElem.classList.add('hidden');
    }
}

// 2. 에러 발생 시 카드 UI 처리 함수
function showErrorCard(errorMessage) {
    const resultSection = document.getElementById('resultSection');
    const statusCard = document.getElementById('statusCard');
    const statusTitle = document.getElementById('statusTitle');
    const statusDesc = document.getElementById('statusDesc');

    if (!resultSection || !statusCard) return;

    document.getElementById('warningContainer')?.classList.add('hidden');
    const progressGrid = document.getElementById('progressGrid');
    const missingCoursesList = document.getElementById('missingCoursesList');
    if (progressGrid) progressGrid.innerHTML = '';
    if (missingCoursesList) missingCoursesList.innerHTML = '';

    statusCard.className = "p-6 rounded-xl shadow-md border border-amber-200 bg-amber-50 text-center";
    if (statusTitle) {
        statusTitle.className = "text-2xl font-bold text-amber-700 mb-2";
        statusTitle.innerText = "ℹ️ 진단 정보를 불러올 수 없습니다";
    }
    if (statusDesc) statusDesc.innerText = errorMessage;

    resultSection.classList.remove('hidden');
}

// 3. 진단 결과 UI 렌더링 함수
function renderResults(data) {
    const resultSection = document.getElementById('resultSection');
    const statusCard = document.getElementById('statusCard');
    const statusTitle = document.getElementById('statusTitle');
    const statusDesc = document.getElementById('statusDesc');

    // 1) 종합 판정 카드
    if (data.is_graduable) {
        statusCard.className = "p-6 rounded-xl shadow-md border border-emerald-200 bg-emerald-50 text-center";
        statusTitle.className = "text-3xl font-extrabold text-emerald-700 mb-2";
        statusTitle.innerText = "🎉 졸업 가능";
        statusDesc.innerText = "모든 졸업 요건(학점 및 필수 과목)을 충족하였습니다.";
    } else {
        statusCard.className = "p-6 rounded-xl shadow-md border border-rose-200 bg-rose-50 text-center";
        statusTitle.className = "text-3xl font-extrabold text-rose-700 mb-2";
        statusTitle.innerText = "⚠️ 졸업 불가 (요건 미달)";
        statusDesc.innerText = "학점 부족 또는 미이수한 필수 과목이 존재합니다. 아래 세부 내용을 확인하세요.";
    }

    // 2) 경고 메시지 렌더링
    const warningContainer = document.getElementById('warningContainer');
    const warningList = document.getElementById('warningList');
    if (warningList) warningList.innerHTML = '';

    if (data.warnings && data.warnings.length > 0) {
        data.warnings.forEach(w => {
            const item = document.createElement('p');
            item.className = "text-sm font-semibold text-amber-900";
            item.innerText = w.message || w;
            if (warningList) warningList.appendChild(item);
        });
        if (warningContainer) warningContainer.classList.remove('hidden');
    } else {
        if (warningContainer) warningContainer.classList.add('hidden');
    }

    // 3) 영역별 이수 학점 Progress Bar 렌더링
    const progressGrid = document.getElementById('progressGrid');
    if (progressGrid) {
        progressGrid.innerHTML = '';
        const summary = data.summary || {};
        
        const categories = [
            { id: 'total', label: '총 학점', earned: summary.total_earned, limit: summary.total_req },
            { id: 'major_req', label: '전공 필수 / 학부 기초', earned: summary.req_earned, limit: summary.req_limit },
            { id: 'major_elec', label: '전공 선택', earned: summary.ele_earned, limit: summary.ele_limit },
            { id: 'general', label: '교양 학점', earned: summary.gen_earned, limit: summary.gen_limit }
        ];

        categories.forEach(cat => {
            const earned = cat.earned || 0;
            const limit = cat.limit || 1;
            const percent = Math.min(Math.round((earned / limit) * 100), 100) || 0;
            const isSuccess = earned >= limit;
            const barColor = isSuccess ? 'bg-indigo-600' : 'bg-amber-500';

            const cardHtml = `
                <div onclick="openCourseModal('${cat.id}')" 
                     class="bg-slate-50 p-4 rounded-lg border border-slate-200 hover:border-indigo-400 hover:shadow-md transition cursor-pointer group">
                    <div class="flex justify-between items-center mb-2">
                        <span class="font-bold text-slate-700 group-hover:text-indigo-600 transition-colors">
                            ${cat.label} <i class="fa-solid fa-chevron-right text-xs opacity-0 group-hover:opacity-100 transition-opacity ml-1"></i>
                        </span>
                        <span class="text-sm font-semibold ${isSuccess ? 'text-indigo-600' : 'text-amber-600'}">
                            ${earned} / ${limit} 학점 (${percent}%)
                        </span>
                    </div>
                    <div class="w-full bg-slate-200 rounded-full h-3">
                        <div class="${barColor} h-3 rounded-full transition-all duration-500" style="width: ${percent}%"></div>
                    </div>
                </div>
            `;
            progressGrid.innerHTML += cardHtml;
        });
    }

    // 4) 미이수 필수 과목 뱃지 렌더링
    const missingCoursesList = document.getElementById('missingCoursesList');
    if (missingCoursesList) {
        missingCoursesList.innerHTML = '';
        if (data.missing_required_courses && data.missing_required_courses.length > 0) {
            data.missing_required_courses.forEach(courseName => {
                const badge = document.createElement('span');
                badge.className = "bg-rose-100 text-rose-700 font-semibold px-3 py-1 rounded-full text-sm border border-rose-200";
                badge.innerText = `❌ ${courseName}`;
                missingCoursesList.appendChild(badge);
            });
        } else {
            missingCoursesList.innerHTML = '<span class="text-emerald-600 font-bold text-sm">✅ 모든 필수 과목을 이수하였습니다!</span>';
        }
    }

    if (resultSection) resultSection.classList.remove('hidden');
}

// 4. 과목 상세 내역 팝업 모달 오픈 함수
async function openCourseModal(categoryId) {
    try {
        const response = await fetch(`/api/credit-detail/${categoryId}`);
        const resData = await response.json();

        if (!response.ok || resData.status !== "success") {
            alert(resData.message || "과목 정보를 불러올 수 없습니다.");
            return;
        }

        const data = resData.data;

        // 1) 모달 타이틀
        const modalTitle = document.getElementById('modalTitle');
        if (modalTitle) modalTitle.innerHTML = `<i class="fa-solid fa-list-check text-indigo-600"></i> ${data.title}`;

        // 2) 미이수 / 추가 필요 과목
        const remSection = document.getElementById('modalRemainingSection');
        const remList = document.getElementById('modalRemainingList');
        if (remList) remList.innerHTML = '';

        if (data.remaining && data.remaining.length > 0) {
            data.remaining.forEach(c => {
                const item = document.createElement('div');
                item.className = "bg-white p-2.5 rounded-lg border border-rose-200 text-xs flex justify-between items-center";
                item.innerHTML = `
                    <span class="font-bold text-rose-800">❌ ${c.name}</span>
                    <span class="text-rose-500 bg-rose-100 px-2 py-0.5 rounded font-semibold">${c.credit}학점</span>
                `;
                if (remList) remList.appendChild(item);
            });
            if (remSection) remSection.classList.remove('hidden');
        } else {
            if (remSection) remSection.classList.add('hidden');
        }

        // 3) 이수 완료 과목
        const compList = document.getElementById('modalCompletedList');
        if (compList) compList.innerHTML = '';

        if (data.completed && data.completed.length > 0) {
            data.completed.forEach(c => {
                const item = document.createElement('div');
                item.className = "bg-white p-2.5 rounded-lg border border-slate-200 text-xs flex justify-between items-center";
                item.innerHTML = `
                    <span class="font-medium text-slate-700">✅ ${c.name}</span>
                    <span class="text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded font-semibold">${c.credit}학점</span>
                `;
                if (compList) compList.appendChild(item);
            });
        } else {
            if (compList) compList.innerHTML = '<p class="text-xs text-slate-400 col-span-2">이수한 과목이 없습니다.</p>';
        }

        // 모달 표시
        const courseModal = document.getElementById('courseModal');
        if (courseModal) courseModal.classList.remove('hidden');

    } catch (err) {
        console.error("모달 오픈 중 오류:", err);
        alert("과목 상세 정보를 가져오는 중 오류가 발생했습니다.");
    }
}

// 5. 팝업 모달 닫기 함수
function closeCourseModal() {
    const courseModal = document.getElementById('courseModal');
    if (courseModal) courseModal.classList.add('hidden');
}

// 6. DOM 로드 완료 시 자동 진단 실행
document.addEventListener("DOMContentLoaded", function() {
    console.log("🚀 main.js 연결 완료!");
    runDiagnosis();
});