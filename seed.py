from app import app
from models import db, Student, Course, StudentCourse, GraduationRequirement, User

with app.app_context():
    db.drop_all()
    db.create_all()

    # 1. 졸업 요건 생성
    req = GraduationRequirement(
        major="컴퓨터공학과",
        total_credit=130,
        major_required=15,
        major_elective=45,
        general=32
    )
    db.session.add(req)

    # 2. 학생 데이터 생성 (student1: 필수 과목 누락 / student2: 졸업 요건 완벽 충족)
    student1 = Student(student_id="20211234", name="김순천", major="컴퓨터공학과", grade=4)
    student2 = Student(student_id="20215678", name="이졸업", major="컴퓨터공학과", grade=4)
    db.session.add_all([student1, student2])

    # 3. 로그인 유저 생성
    user1 = User(username="student2021", student_id="20211234")
    user1.set_password("1234")
    
    # student2 계정 정보: ID (student2021pass) / PW (5678)
    user2 = User(username="student2021pass", student_id="20215678")
    user2.set_password("5678")

    db.session.add_all([user1, user2])
    db.session.commit()
    print("DB 유저 등록 완료!")
    print(" - [학생1] ID: student2021     / PW: 1234 (학번: 20211234)")
    print(" - [학생2] ID: student2021pass / PW: 5678 (학번: 20215678)")

    # 4. 과목 데이터 생성 (학생2의 133학점 이수를 위해 전선/교양 과목 추가)
    courses = [
        # 지정 필수 및 학부기초 과목 (총 15학점)
        Course(course_id="CS101", course_name="선형대수", category="학부기초", credit=3, semester=1),
        Course(course_id="CS102", course_name="디지털로직", category="학부기초", credit=3, semester=1),
        Course(course_id="CS103", course_name="컴퓨터 구조", category="학부기초", credit=3, semester=2),
        Course(course_id="CS104", course_name="운영체제", category="전공필수", credit=3, semester=1),
        Course(course_id="CS105", course_name="컴퓨터 네트워크", category="전공필수", credit=3, semester=2),
        
        # 전공선택 과목 (총 48학점 분량)
        Course(course_id="CS201", course_name="자료구조", category="전공선택", credit=3, semester=1),
        Course(course_id="CS202", course_name="알고리즘", category="전공선택", credit=3, semester=2),
        Course(course_id="CS203", course_name="데이터베이스", category="전공선택", credit=3, semester=1),
        Course(course_id="CS204", course_name="소프트웨어공학", category="전공선택", credit=3, semester=2),
        Course(course_id="CS205", course_name="인공지능개론", category="전공선택", credit=3, semester=1),
        Course(course_id="CS206", course_name="클라우드컴퓨팅", category="전공선택", credit=3, semester=2),
        Course(course_id="CS207", course_name="웹프로그래밍", category="전공선택", credit=3, semester=1),
        Course(course_id="CS208", course_name="캡스톤디자인1", category="전공선택", credit=3, semester=1),
        Course(course_id="CS209", course_name="캡스톤디자인2", category="전공선택", credit=3, semester=2),
        Course(course_id="CS210", course_name="모바일프로그래밍", category="전공선택", credit=3, semester=1),
        Course(course_id="CS211", course_name="정보보안", category="전공선택", credit=3, semester=2),
        Course(course_id="CS212", course_name="빅데이터분석", category="전공선택", credit=3, semester=1),
        Course(course_id="CS213", course_name="컴퓨터그래픽스", category="전공선택", credit=3, semester=2),
        Course(course_id="CS214", course_name="임베디드시스템", category="전공선택", credit=3, semester=1),
        Course(course_id="CS215", course_name="딥러닝실습", category="전공선택", credit=3, semester=2),
        Course(course_id="CS216", course_name="오픈소스프로젝트", category="전공선택", credit=3, semester=1),

        # 교양 과목 (총 32학점 분량)
        Course(course_id="GE101", course_name="대학영어", category="교양", credit=3, semester=0),
        Course(course_id="GE102", course_name="글쓰기", category="교양", credit=3, semester=0),
        Course(course_id="GE103", course_name="컴퓨팅사고", category="교양", credit=3, semester=0),
        Course(course_id="GE104", course_name="철학과삶", category="교양", credit=3, semester=0),
        Course(course_id="GE105", course_name="한국사의이해", category="교양", credit=3, semester=0),
        Course(course_id="GE106", course_name="심리학개론", category="교양", credit=3, semester=0),
        Course(course_id="GE107", course_name="경제학의이해", category="교양", credit=3, semester=0),
        Course(course_id="GE108", course_name="세계문화기행", category="교양", credit=3, semester=0),
        Course(course_id="GE109", course_name="현대사회와윤리", category="교양", credit=3, semester=0),
        Course(course_id="GE110", course_name="과학기술과사회", category="교양", credit=3, semester=0),
        Course(course_id="GE111", course_name="음악의지평", category="교양", credit=2, semester=0),
    ]
    db.session.add_all(courses)
    db.session.commit()

    # 5-1. 학생1 (김순천) 이수 내역: CS105(컴퓨터 네트워크) 누락
    student1_taken = [
        "CS101", "CS102", "CS103", "CS104",
        "CS201", "CS202", "CS203", "CS204", "CS205", "CS206", "CS207", "CS208", "CS209",
        "GE101", "GE102", "GE103", "GE104", "GE105"
    ]
    for cid in student1_taken:
        db.session.add(StudentCourse(student_id="20211234", course_id=cid))

    # 5-2. 학생2 (이졸업) 이수 내역: 총 133학점 (전필 15 + 전선 48 + 교양 32 = 완벽 충족)
    student2_taken = [
        # 전공필수 및 학부기초 15학점 전체
        "CS101", "CS102", "CS103", "CS104", "CS105", 
        # 전공선택 48학점 전체
        "CS201", "CS202", "CS203", "CS204", "CS205", "CS206", "CS207", "CS208", 
        "CS209", "CS210", "CS211", "CS212", "CS213", "CS214", "CS215", "CS216",
        # 교양 32학점 전체
        "GE101", "GE102", "GE103", "GE104", "GE105", "GE106", "GE107", "GE108", "GE109", "GE110", "GE111"
    ]
    for cid in student2_taken:
        db.session.add(StudentCourse(student_id="20215678", course_id=cid))

    db.session.commit()
    print("시나리오별 시드 데이터 리셋 및 초기화가 성공적으로 완료되었습니다!")