from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# 유저 (로그인용)
class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False) # 로그인 아이디
    password_hash = db.Column(db.String(255), nullable=False)        # 암호화된 비밀번호
    student_id = db.Column(db.String(20), db.ForeignKey('student.student_id'), nullable=False) # 학생 테이블과 연결

    # 비밀번호 암호화 저장
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # 비밀번호 검증
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# 학생
class Student(db.Model):
    __tablename__ = "student"

    student_id = db.Column(
        db.String(20),
        primary_key=True
    )

    name = db.Column(
        db.String(20)
    )

    major = db.Column(
        db.String(50)
    )

    grade = db.Column(
        db.Integer
    )


# 과목
class Course(db.Model):
    __tablename__ = "course"

    course_id = db.Column(
        db.Integer,
        primary_key=True
    )

    course_name = db.Column(
        db.String(50)
    )

    category = db.Column(
        db.String(20)
    )

    credit = db.Column(
        db.Integer
    )

    semester = db.Column(
        db.Integer
    )


# 학생 수강 기록
class StudentCourse(db.Model):
    __tablename__ = "student_course"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    student_id = db.Column(
        db.String(20)
    )

    course_id = db.Column(
        db.Integer
    )


# 졸업 기준
class GraduationRequirement(db.Model):
    __tablename__ = "graduation_requirement"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    major = db.Column(
        db.String(50)
    )

    total_credit = db.Column(
        db.Integer
    )

    major_required = db.Column(
        db.Integer
    )

    major_elective = db.Column(
        db.Integer
    )

    general = db.Column(
        db.Integer
    )