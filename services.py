def diagnose_graduation(student_id, current_semester=1):
    """
    current_semester: 현재 남아있는 학기 중 진단 시점의 학기 (예: 1학기 or 2학기)
    """
    student = Student.query.get(student_id)
    if not student:
        return {"error": "학생 정보를 찾을 수 없습니다."}

    # 1. 학생의 이수 과목 목록 조회
    student_courses = StudentCourse.query.filter_by(student_id=student_id).all()
    taken_course_ids = [sc.course_id for sc in student_courses]
    taken_courses = Course.query.filter(Course.course_id.in_(taken_course_ids)).all() if taken_course_ids else []

    # 2. 전공 기준 조회
    req = GraduationRequirement.query.filter_by(major=student.major).first()
    if not req:
        return {"error": "해당 전공의 졸업 요건 정보가 없습니다."}

    # 3. 학점 계산
    earned_total = sum(c.credit for c in taken_courses)
    earned_major_req = sum(c.credit for c in taken_courses if c.category == '전공필수')
    earned_major_ele = sum(c.credit for c in taken_courses if c.category == '전공선택')
    earned_general = sum(c.credit for c in taken_courses if '교양' in c.category)

    # 4. 미이수 전공필수 과목 진단
    all_major_required_courses = Course.query.filter_by(category='전공필수').all()
    missing_required = [c for c in all_major_required_courses if c.course_id not in taken_course_ids]

    # 5. [핵심] 1년 1회 개설 과목 미이수로 인한 졸업 연기 경고 로직
    warnings = []
    for miss_course in missing_required:
        # 개설 학기 제약이 있는 과목인데, 현재/다음 학기에 바로 개설되지 않는 경우
        if miss_course.offered_semester != 0:
            if miss_course.offered_semester != current_semester:
                warnings.append({
                    "course_name": miss_course.course_name,
                    "offered_semester": f"{miss_course.offered_semester}학기",
                    "message": f"🚨 [졸업 연기 위험] '{miss_course.course_name}' 과목은 {miss_course.offered_semester}학기에만 개설되는 전공필수 과목입니다."
                })

    # 6. 종합 진단 결과 반환
    is_graduable = (
        earned_total >= req.total_credit and
        earned_major_req >= req.major_required and
        earned_major_ele >= req.major_elective and
        earned_general >= req.general and
        len(missing_required) == 0
    )

    return {
        "student_id": student.student_id,
        "is_graduable": is_graduable,
        "summary": {
            "total_credit": f"{earned_total} / {req.total_credit}",
            "major_required": f"{earned_major_req} / {req.major_required}",
            "major_elective": f"{earned_major_ele} / {req.major_elective}",
            "general": f"{earned_general} / {req.general}"
        },
        "missing_required_courses": [c.course_name for c in missing_required],
        "warnings": warnings
    }