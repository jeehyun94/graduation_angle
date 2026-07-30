from flask import Flask
from models import db
from diagnose import diagnose_bp
from auth import auth_bp
from kmooc import kmooc_bp

app = Flask(__name__)
app.secret_key = "super-secret-key"  # 세션 사용을 위해 필수!
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# 블루프린트 등록 (app 생성 후에 일괄 등록)
app.register_blueprint(diagnose_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(kmooc_bp)  # 👈 이 위치로 이동!

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    # 💡 실행 시 Flask에 등록된 전체 라우트(URL) 목록을 터미널에 출력
    print("\n--- 등록된 전체 URL 목록 ---")
    print(app.url_map)
    print("----------------------------\n")

    app.run(debug=True, port=5000)