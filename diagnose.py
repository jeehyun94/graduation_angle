import json
from flask import Blueprint, render_template, request, redirect, url_for, session, Response, jsonify
from models import db, Student, Course, StudentCourse, GraduationRequirement

diagnose_bp = Blueprint('diagnose', __name__)

def diagnose_graduation(student_id, current_semester=1):
    # student_id를 문자열(String)로 확실히 처리
    student_id_str = str(student_id)
    
    student = Student.query.filter_by(student_id=student_id_str).first()
    if not student:
        return {"error": "학생 정보를 찾을 수 없습니다."}, 404

    # 1. 학생이 이수한 과목 목록 조회
    student_courses = StudentCourse.query.filter_by(student_id=student_id_str).all()
    completed_course_ids = [sc.course_id for sc in student_courses]
    
    taken_courses = Course.query.filter(Course.course_id.in_(completed_course_ids)).all() if completed_course_ids else []
    taken_course_names = [c.course_name.strip() for c in taken_courses if c.course_name]

    # 2. 졸업 기준 조회
    req = GraduationRequirement.query.filter_by(major=student.major).first()
    
    total_req_credit = req.total_credit if req else 130
    major_req_credit = req.major_required if req else 15
    major_ele_credit = req.major_elective if req else 45
    general_req_credit = req.general if req else 32

    # 3. 학점 계산
    earned_total = sum(c.credit for c in taken_courses if c.credit)
    earned_major_req = sum(c.credit for c in taken_courses if c.credit and c.category in ['필수/학부기초', '전공필수', '학부기초'])
    earned_major_ele = sum(c.credit for c in taken_courses if c.credit and c.category in ['전공 선택', '전공선택'])
    earned_general = sum(c.credit for c in taken_courses if c.credit and c.category and '교양' in c.category)

    # 4. 미이수 필수 과목 검사
    required_categories = ['필수/학부기초', '전공필수', '학부기초']
    all_required_courses = Course.query.filter(Course.category.in_(required_categories)).all()
    
    missing_required = [c for c in all_required_courses if c.course_id not in completed_course_ids]

    # 지정 필수 과목
    must_have_courses = ["운영체제", "컴퓨터 구조", "컴퓨터 네트워크"]
    missing_must_haves = [
        name for name in must_have_courses 
        if name not in taken_course_names
    ]

    # 5. 개설 학기 경고 메시지 (AttributeError 방지를 위한 getattr 안전 처리)
    warnings = []
    for miss_course in missing_required:
        semester_val = getattr(miss_course, 'semester', None) or getattr(miss_course, 'offered_semester', 0)
        if semester_val and semester_val != 0 and semester_val != current_semester:
            warnings.append({
                "course_name": miss_course.course_name,
                "offered_semester": f"{semester_val}학기",
                "message": f"🚨 [졸업 연기 위험] '{miss_course.course_name}' 과목은 {semester_val}학기에만 개설되는 필수/기초 과목입니다."
            })

    # 6. 미이수 목록 통합 및 최종 판단
    missing_course_names = list(set([c.course_name for c in missing_required if c.course_name] + missing_must_haves))

    is_graduable = (
        earned_total >= total_req_credit and
        earned_major_req >= major_req_credit and
        earned_major_ele >= major_ele_credit and
        earned_general >= general_req_credit and
        len(missing_course_names) == 0
    )

    return {
        "student_id": student.student_id,
        "is_graduable": is_graduable,
        "summary": {
            "total_credit": f"{earned_total} / {total_req_credit}",
            "major_required": f"{earned_major_req} / {major_req_credit}",
            "major_elective": f"{earned_major_ele} / {major_ele_credit}",
            "general": f"{earned_general} / {general_req_credit}",
            "total_earned": earned_total, "total_req": total_req_credit,
            "req_earned": earned_major_req, "req_limit": major_req_credit,
            "ele_earned": earned_major_ele, "ele_limit": major_ele_credit,
            "gen_earned": earned_general, "gen_limit": general_req_credit
        },
        "missing_required_courses": missing_course_names,
        "warnings": warnings
    }, 200

@diagnose_bp.route("/")
def home():
    if "user_id" not in session and "student_id" not in session:
        return redirect(url_for("auth.login"))
    
    student_id = session.get("student_id")
    username = session.get("username")
    
    # DB에서 student_id로 학생 정보(실명, 학과) 조회
    student = Student.query.filter_by(student_id=str(student_id)).first() if student_id else None
    
    # Student 테이블에 정보가 있을 경우 가져오고, 없으면 기본값 설정
    name = student.name if student else username
    major = student.major if student else "컴퓨터공학과"

    return render_template(
        "index.html", 
        student_id=student_id, 
        name=name, 
        major=major
    )

# 💡 카테고리별 이수/미이수 과목 정밀 분류 API
@diagnose_bp.route("/api/credit-detail/<category_id>", methods=["GET"])
def get_credit_detail(category_id):
    student_id = session.get("student_id")
    if not student_id:
        return jsonify({"status": "error", "message": "로그인이 필요합니다."}), 401

    student_id_str = str(student_id)
    student = Student.query.filter_by(student_id=student_id_str).first()
    if not student:
        return jsonify({"status": "error", "message": "학생 정보를 찾을 수 없습니다."}), 404

    # 학생이 수강한 과목 ID 목록
    student_courses = StudentCourse.query.filter_by(student_id=student_id_str).all()
    completed_ids = [sc.course_id for sc in student_courses]

    # 학생이 이수한 전체 과목 객체 리스트
    taken_courses = Course.query.filter(Course.course_id.in_(completed_ids)).all() if completed_ids else []

    title = ""
    completed_list = []
    remaining_list = []

    # 1. 총 학점 클릭 시: 이수한 모든 과목 (전공 + 교양 + 기타)
    if category_id == 'total':
        title = "전체 이수 과목 (총 학점)"
        completed_list = taken_courses
        # 미이수 항목에는 전체 필수 과목 중 안 들은 것 표시
        req_cats = ['필수/학부기초', '전공필수', '학부기초']
        remaining_list = Course.query.filter(
            Course.category.in_(req_cats),
            Course.course_id.not_in(completed_ids)
        ).all() if completed_ids else Course.query.filter(Course.category.in_(req_cats)).all()

    # 2. 전공 필수 / 학부 기초 클릭 시
    elif category_id in ['major_req', 'major_required']:
        title = "전공 필수 / 학부 기초"
        req_cats = ['필수/학부기초', '전공필수', '학부기초']
        completed_list = [c for c in taken_courses if c.category in req_cats]
        remaining_list = Course.query.filter(
            Course.category.in_(req_cats),
            Course.course_id.not_in(completed_ids)
        ).all() if completed_ids else Course.query.filter(Course.category.in_(req_cats)).all()

    # 3. 전공 선택 클릭 시
    elif category_id in ['major_elec', 'major_elective']:
        title = "전공 선택"
        elec_cats = ['전공 선택', '전공선택']
        completed_list = [c for c in taken_courses if c.category in elec_cats]
        # 개설된 전공 선택 과목 중 아직 안 들은 과목들
        remaining_list = Course.query.filter(
            Course.category.in_(elec_cats),
            Course.course_id.not_in(completed_ids)
        ).all() if completed_ids else Course.query.filter(Course.category.in_(elec_cats)).all()

    # 4. 교양 학점 클릭 시
    elif category_id in ['general']:
        title = "교양 과목"
        completed_list = [c for c in taken_courses if c.category and '교양' in c.category]
        remaining_list = [] # 교양은 자율 선택이므로 미이수 목록 생략 가능

    return jsonify({
        "status": "success",
        "data": {
            "title": title,
            "completed": [
                {
                    "code": c.course_id,
                    "name": c.course_name,
                    "category": c.category,
                    "credit": c.credit
                } for c in completed_list
            ],
            "remaining": [
                {
                    "code": c.course_id,
                    "name": c.course_name,
                    "category": c.category,
                    "credit": c.credit
                } for c in remaining_list
            ]
        }
    }), 200

# diagnose.py 아래 쪽에 추가

@diagnose_bp.route("/api/diagnose", methods=["POST", "GET"])
def api_diagnose():
    try:
        # Request에서 student_id 및 semester 데이터 가져오기
        if request.method == "POST":
            data = request.get_json() or {}
            student_id = data.get("student_id") or session.get("student_id")
            semester = int(data.get("semester", 1))
        else:
            student_id = request.args.get("student_id") or session.get("student_id")
            semester = int(request.args.get("semester", 1))

        if not student_id:
            return jsonify({"status": "error", "message": "학번 정보가 존재하지 않습니다."}), 400

        # 진단 로직 함수 실행
        result, status_code = diagnose_graduation(student_id, current_semester=semester)
        
        # 에러 응답 처리
        if "error" in result:
            return jsonify({"status": "error", "message": result["error"]}), status_code

        return jsonify({"status": "success", "data": result}), 200

    except Exception as e:
        # 터미널에 상세 에러 출력
        import traceback
        print("=== 진단 로직 예외 발생 ===")
        traceback.print_exc()
        
        return jsonify({
            "status": "error", 
            "message": f"진단 로직 처리 중 서버 오류가 발생했습니다: {str(e)}"
        }), 500