# student1.py
from app import app
from models import db, Student, Course, StudentCourse, GraduationRequirement

STUDENT_ID = "20211234"

with app.app_context():
    # 1. 졸업 요건 데이터 확인/생성
    req = GraduationRequirement.query.filter_by(major="컴퓨터공학과").first()
    if not req:
        req = GraduationRequirement(
            major="컴퓨터공학과",
            total_credit=130,
            major_required=15,
            major_elective=45,
            general=32
        )
        db.session.add(req)

    # 2. 과목 데이터 설정
    courses_data = [
        # [필수/학부기초] 정확히 12학점 이수 ('컴퓨터 네트워크' 3학점 미이수)
        {"course_name": "컴퓨터 네트워크", "category": "필수/학부기초", "credit": 3, "semester": 1}, # ❌ 미이수
        {"course_name": "운영체제", "category": "필수/학부기초", "credit": 3, "semester": 1},
        {"course_name": "컴퓨터 구조", "category": "필수/학부기초", "credit": 3, "semester": 2},
        {"course_name": "자료구조", "category": "필수/학부기초", "credit": 3, "semester": 1},
        {"course_name": "알고리즘", "category": "필수/학부기초", "credit": 3, "semester": 2},

        # [전공선택] 51학점
        {"course_name": "인공지능", "category": "전공선택", "credit": 3, "semester": 1},
        {"course_name": "머신러닝", "category": "전공선택", "credit": 3, "semester": 2},
        {"course_name": "딥러닝", "category": "전공선택", "credit": 3, "semester": 1},
        {"course_name": "데이터베이스", "category": "전공선택", "credit": 3, "semester": 1},
        {"course_name": "소프트웨어공학", "category": "전공선택", "credit": 3, "semester": 2},
        {"course_name": "웹프로그래밍", "category": "전공선택", "credit": 3, "semester": 1},
        {"course_name": "모바일앱개발", "category": "전공선택", "credit": 3, "semester": 2},
        {"course_name": "클라우드컴퓨팅", "category": "전공선택", "credit": 3, "semester": 1},
        {"course_name": "정보보안", "category": "전공선택", "credit": 3, "semester": 2},
        {"course_name": "컴퓨터그래픽스", "category": "전공선택", "credit": 3, "semester": 1},
        {"course_name": "빅데이터분석", "category": "전공선택", "credit": 3, "semester": 2},
        {"course_name": "사물인터넷", "category": "전공선택", "credit": 3, "semester": 1},
        {"course_name": "임베디드시스템", "category": "전공선택", "credit": 3, "semester": 2},
        {"course_name": "컴파일러", "category": "전공선택", "credit": 3, "semester": 1},
        {"course_name": "자연어처리", "category": "전공선택", "credit": 3, "semester": 2},
        {"course_name": "영상처리", "category": "전공선택", "credit": 3, "semester": 1},
        {"course_name": "신경망개론", "category": "전공선택", "credit": 3, "semester": 2},

        # [교양] 32학점
        {"course_name": "대학영어", "category": "교양", "credit": 3, "semester": 1},
        {"course_name": "글쓰기와소통", "category": "교양", "credit": 3, "semester": 1},
        {"course_name": "철학의이해", "category": "교양", "credit": 3, "semester": 2},
        {"course_name": "심리학개론", "category": "교양", "credit": 3, "semester": 1},
        {"course_name": "경제학원론", "category": "교양", "credit": 3, "semester": 2},
        {"course_name": "서양미술사", "category": "교양", "credit": 3, "semester": 1},
        {"course_name": "우주의이해", "category": "교양", "credit": 3, "semester": 2},
        {"course_name": "음악의세계", "category": "교양", "credit": 3, "semester": 1},
        {"course_name": "역사와사회", "category": "교양", "credit": 3, "semester": 2},
        {"course_name": "논리와사고", "category": "교양", "credit": 3, "semester": 1},
        {"course_name": "체육과건강", "category": "교양", "credit": 2, "semester": 1},

        # [일반선택] 38학점
        {"course_name": "일반선택1", "category": "일반선택", "credit": 3, "semester": 1},
        {"course_name": "일반선택2", "category": "일반선택", "credit": 3, "semester": 2},
        {"course_name": "일반선택3", "category": "일반선택", "credit": 3, "semester": 1},
        {"course_name": "일반선택4", "category": "일반선택", "credit": 3, "semester": 2},
        {"course_name": "일반선택5", "category": "일반선택", "credit": 3, "semester": 1},
        {"course_name": "일반선택6", "category": "일반선택", "credit": 3, "semester": 2},
        {"course_name": "일반선택7", "category": "일반선택", "credit": 3, "semester": 1},
        {"course_name": "일반선택8", "category": "일반선택", "credit": 3, "semester": 2},
        {"course_name": "일반선택9", "category": "일반선택", "credit": 3, "semester": 1},
        {"course_name": "일반선택10", "category": "일반선택", "credit": 3, "semester": 2},
        {"course_name": "일반선택11", "category": "일반선택", "credit": 3, "semester": 1},
        {"course_name": "일반선택12", "category": "일반선택", "credit": 3, "semester": 2},
        {"course_name": "일반선택13", "category": "일반선택", "credit": 2, "semester": 1},
    ]

    for c in courses_data:
        course = Course.query.filter_by(course_name=c["course_name"]).first()
        if not course:
            course = Course(
                course_name=c["course_name"],
                category=c["category"],
                credit=c["credit"],
                semester=c["semester"]
            )
            db.session.add(course)
    db.session.commit()

    # 3. Student 등록 확인
    student = Student.query.filter_by(student_id=STUDENT_ID).first()
    if not student:
        student = Student(student_id=STUDENT_ID, name="김순천", major="컴퓨터공학과", grade=4)
        db.session.add(student)
        db.session.commit()

    # 4. 수강 내역 초기화 및 재등록
    StudentCourse.query.filter_by(student_id=STUDENT_ID).delete()

    completed_names = [c["course_name"] for c in courses_data if c["course_name"] != "컴퓨터 네트워크"]
    
    total_credits = 0
    req_credits = 0

    for name in completed_names:
        course = Course.query.filter_by(course_name=name).first()
        if course:
            sc = StudentCourse(student_id=STUDENT_ID, course_id=course.course_id)
            db.session.add(sc)
            total_credits += course.credit
            if course.category == "필수/학부기초":
                req_credits += course.credit

    db.session.commit()
    print("✅ Student1 시나리오 설정 완료!")
    print(f"   [총 취득 학점]: {total_credits} / 130  (130학점 초과)")
    print(f"   [필수/학부기초]: {req_credits} / 15  ('컴퓨터 네트워크' 미이수)")