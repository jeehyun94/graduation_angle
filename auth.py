# auth.py

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import db, User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username_input = request.form.get("username")
        password = request.form.get("password")
        
        # 💡 아이디(username) 또는 학번(student_id) 중 하나라도 일치하는 유저 검색
        user = User.query.filter(
            (User.username == username_input) | (User.student_id == username_input)
        ).first()
        
        # 🔍 터미널 디버깅 출력
        print(f"--> 입력된 값: {username_input}, 비밀번호: {password}")
        print(f"--> DB에서 찾은 유저: {user}")

        if user:
            # 해시 비밀번호 검증
            if user.check_password(password):
                session["user_id"] = user.id
                session["student_id"] = user.student_id
                session["username"] = user.username
                print("--> 로그인 성공! 메인으로 이동합니다.")
                return redirect(url_for("diagnose.home"))
            else:
                print("--> ❌ 비밀번호 불일치!")
                flash("비밀번호가 올바르지 않습니다.")
        else:
            print("--> ❌ 존재하지 않는 아이디 또는 학번!")
            flash("존재하지 않는 아이디 또는 학번입니다.")

    return render_template("login.html")

@auth_bp.route("/logout")
def logout():
    session.clear()  # 세션 삭제
    return redirect(url_for("auth.login"))