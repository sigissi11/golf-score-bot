from flask import Flask, request, jsonify
from datetime import datetime
import sqlite3

app = Flask(__name__)

DB_PATH = 'score.db'

# DB 초기화
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS scores (
            user TEXT PRIMARY KEY,
            score INTEGER,
            last_update TEXT
        )
    ''')
    conn.commit()
    conn.close()

# 점수 추가
def add_score(user, point):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT score FROM scores WHERE user = ?", (user,))
    row = c.fetchone()
    if row:
        new_score = row[0] + point
        c.execute("UPDATE scores SET score = ?, last_update = ? WHERE user = ?", (new_score, datetime.now(), user))
    else:
        c.execute("INSERT INTO scores (user, score, last_update) VALUES (?, ?, ?)", (user, point, datetime.now()))
    conn.commit()
    conn.close()

# 점수 전체 조회
def get_all_scores():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT user, score FROM scores ORDER BY score DESC")
    result = c.fetchall()
    conn.close()
    return result

# 점수 초기화
def reset_scores():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM scores")
    conn.commit()
    conn.close()

# 웹훅 라우터
@app.route('/hook', methods=['POST'])
def webhook():
    data = request.get_json()
    msg = data.get('msg', '')
    user = data.get('user', '')

    if msg.startswith('/정라'):
        add_score(user, 5)
    elif msg.startswith('/정스'):
        add_score(user, 3)
    elif msg.startswith('/벙주'):
        add_score(user, 2)
    elif msg.startswith('/벙'):
        add_score(user, 1)
    elif msg.startswith('/전체기록'):
        score_list = get_all_scores()
        return jsonify({'records': score_list})
    elif msg.startswith('/초기화'):
        reset_scores()
    else:
        return jsonify({'status': 'ignored'})

    return jsonify({'status': 'ok'})

# 앱 실행
if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
