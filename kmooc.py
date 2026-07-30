# kmooc.py
import requests
import xml.etree.ElementTree as ET
from flask import Blueprint, jsonify, request

kmooc_bp = Blueprint('kmooc', __name__)

# 공공데이터포털에서 발급받은 K-MOOC API 인증키 (발급 전에는 아래 모의 데이터가 자동 반환됩니다)
KMOOC_API_KEY = "YOUR_PUBLIC_DATA_API_KEY" 
KMOOC_URL = "http://api.kmooc.kr/service/courseresult/courseList"

@kmooc_bp.route('/api/kmooc-recommend', methods=['GET'])
def get_kmooc_recommend():
    keyword = request.args.get('keyword', '컴퓨터')
    
    # API 키 미발급 시 사용할 테스트용 모의(Mock) 데이터
    if KMOOC_API_KEY == "YOUR_PUBLIC_DATA_API_KEY":
        mock_courses = [
            {
                "title": f"파이썬으로 배우는 {keyword} 기초",
                "org_name": "서울대학교",
                "url": "https://www.kmooc.kr",
                "summary": "학점 인정 및 기초 개념 확립 강좌"
            },
            {
                "title": f"현대 사회와 {keyword} 기술의 이해",
                "org_name": "KAIST",
                "url": "https://www.kmooc.kr",
                "summary": "교양 및 필수 학점 보강을 위한 추천 강좌"
            }
        ]
        return jsonify({"status": "success", "data": mock_courses}), 200

    # 공공데이터포털 실제 API 호출
    params = {
        'serviceKey': KMOOC_API_KEY,
        'Search': keyword,
        'page': 1,
        'ListSize': 4
    }

    try:
        response = requests.get(KMOOC_URL, params=params, timeout=5)
        
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            courses = []
            
            for item in root.findall('.//item'):
                title = item.findtext('courseTitle', '강좌명 없음')
                org = item.findtext('orgName', '기관명 없음')
                course_id = item.findtext('courseId', '')
                
                courses.append({
                    "title": title,
                    "org_name": org,
                    "url": f"https://www.kmooc.kr/courses/{course_id}" if course_id else "https://www.kmooc.kr",
                    "summary": f"{org} 제공 강좌"
                })
                
            return jsonify({"status": "success", "data": courses}), 200
        else:
            return jsonify({"status": "error", "message": "K-MOOC API 응답 실패"}), 500

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500