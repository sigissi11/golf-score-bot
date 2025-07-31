from flask import Flask, request
import sqlite3
import datetime

app = Flask(__name__)

# ✅ DB 초기화
def init_db():
    conn = sqlite3.connect("score.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS scores (
            name TEXT,
            date TEXT,
            type TEXT,
            point INTEGER
        )
    ''')
    conn.commit()
    conn.close()

# ✅ 점수 추가 함수
def add_score(name, type_text):
    point_table = {
        "정라": 5,
        "정스": 3,
        "벙주": 2,
        "벙": 1
    }

    if type_text not in point_table:
        return None

    point = point_table[type_text]
    conn = sqlite3.connect("score.db")
    c = conn.cursor()
    c.execute("INSERT INTO scores (name, date, type, point) VALUES (?, ?, ?, ?)",
              (name, datetime.date.today().isoformat(), type_text, point))
    conn.commit()
    conn.close()
    return point

# ✅ 랭킹 출력
def get_ranking():
    conn = sqlite3.connect("score.db")
    c = conn.cursor()
    c.execute("SELECT name, SUM(point) as total FROM scores GROUP BY name ORDER BY total DESC")
    data = c.fetchall()
    conn.close()

    if not data:
        return "🏌️ 랭킹 데이터가 없습니다."

    rank_text = "🏌️‍♂️ 골프방 누적 랭킹\n\n"
    for i, row in enumerate(data, 1):
        rank_text += f"{i}. {row[0]} - {row[1]}점\n"
    return rank_text

# ✅ 전체 기록 출력
def get_full_record():
    conn = sqlite3.connect("score.db")
    c = conn.cursor()
    c.execute("""
        SELECT name, type, COUNT(*) as cnt, SUM(point) as total 
        FROM scores 
        GROUP BY name, type 
        ORDER BY name, type
    """)
    rows = c.fetchall()
    conn.close()

    if not rows:
        return "📄 기록이 없습니다."

    result = "📋 전체 출석 기록\n"
    current_name = ""
    for name, ttype, cnt, total in rows:
        if name != current_name:
            result += f"\n👤 {name}\n"
            current_name = name
        result += f"  • {ttype}: {cnt}회 / {total}점\n"
    return result

# ✅ 모든 기록 초기화
def reset_all():
    conn = sqlite3.connect("score.db")
    c = conn.cursor()
    c.execute("DELETE FROM scores")
    conn.commit()
    conn.close()
    return "⚠️ 모든 출석 기록이 초기화되었습니다."

# ✅ Flask 라우팅
@app.route("/", methods=["POST"])
def bot():
    user_msg = request.form.get("content").strip()

    # 명령어 처리
    if user_msg == "/랭킹":
        return get_ranking()

    if user_msg == "/전체기록":
        return get_full_record()

    if user_msg == "/초기화":
        return reset_all()

    if user_msg.startswith("/"):
        try:
            parts = user_msg[1:].split(" ", 1)
            type_text, name = parts[0].strip(), parts[1].strip()
            point = add_score(name, type_text)
            if point is not None:
                return f"{name}님 {type_text} 참석 확인! +{point}점 적립 🎯"
            else:
                return f"⚠️ '{type_text}'는 유효한 출석 종류가 아닙니다."
        except:
            return "⚠️ 형식 오류! 예: `/정라 홍길동`처럼 입력해주세요."

    return "🤖 명령어:\n- `/정라 홍길동`\n- `/벙주 춘식`\n- `/랭킹`\n- `/전체기록`\n- `/초기화` (주의!)"

# ✅ 실행 시작
if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=8080)
