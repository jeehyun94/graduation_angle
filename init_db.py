# init_db.py
from app import app
from models import db, User, Course

with app.app_context():
    db.create_all()

    # 1. 과목 데이터 준비
    courses = [
        {"code": "CS101", "name": "컴퓨터 네트워크", "category": "필수/학부기초", "credit": 3},
        {"code": "CS102", "name": "운영체제", "category": "필수/학부기초", "credit": 3},
        {"code": "CS103", "name": "컴퓨터 구조", "category": "필수/학부기초", "credit": 3},
        {"code": "CS201", "name": "자료구조", "category": "전공 선택", "credit": 3},
        {"code": "CS202", "name": "알고리즘", "category": "전공 선택", "credit": 3},
        {"code": "GE101", "name": "대학영어", "category": "교양 영역", "credit": 2},
    ]

    for c in courses:
        if not Course.query.filter_by(code=c["code"]).first():
            db.session.add(Course(**c))

    # 2. 로그인용 계정 생성 (20211234)
    user = User.query.filter_by(student_id="20211234").first()
    if not user:
        user = User(username="student2021", student_id="20211234")
        user.set_password("1234")
        db.session.add(user)

    db.session.commit()
    print("✅ 기본 DB 초기화 완료!")