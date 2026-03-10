import sqlite3
import datetime
import re
from flask import Flask, request, render_template, jsonify, redirect, url_for

app = Flask(__name__)
DB_NAME = "honeypot.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS logs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  ip_address TEXT,
                  timestamp DATETIME,
                  attack_type TEXT,
                  username TEXT,
                  password_attempt TEXT)''')
    conn.commit()
    conn.close()

def log_attempt(ip_address, attack_type, username, password_attempt):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO logs (ip_address, timestamp, attack_type, username, password_attempt) VALUES (?, ?, ?, ?, ?)",
              (ip_address, datetime.datetime.now(), attack_type, username, password_attempt))
    conn.commit()
    conn.close()

def check_sqli(text):
    # Basic SQL injection patterns
    sqli_patterns = [
        r"(?i)OR\s+1\s*=\s*1",
        r"(--|\#|/\*)",
        r"(?i)UNION\s+SELECT",
        r"['\"]"
    ]
    for pattern in sqli_patterns:
        if re.search(pattern, text):
            return True
    return False

def check_brute_force(ip_address):
    # Check if more than 5 attempts within the last 5 minutes from this IP
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    five_mins_ago = datetime.datetime.now() - datetime.timedelta(minutes=5)
    c.execute("SELECT COUNT(*) FROM logs WHERE ip_address=? AND timestamp > ?", (ip_address, five_mins_ago))
    count = c.fetchone()[0]
    conn.close()
    return count >= 5

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        # Real IP behind proxy/load balancer
        ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
        if ip_address:
            ip_address = ip_address.split(',')[0].strip()
        else:
            ip_address = 'Unknown'
            
        attack_type = "Failed Login"
        
        is_sqli = check_sqli(username) or check_sqli(password)
        if is_sqli:
            attack_type = "SQL Injection"
        elif check_brute_force(ip_address):
            attack_type = "Brute Force"
            
        log_attempt(ip_address, attack_type, username, password)
        
        # Always fail the login since it's a decoy honeypot
        return render_template('login.html', error="Invalid username or password.")
        
    return render_template('login.html')

@app.route('/admin')
def admin():
    # Simple query auth for demo purposes
    if request.args.get('secret') != 'superadmin123':
        return "Unauthorized. Access requires the correct token parameter.", 401
    return render_template('admin.html')

@app.route('/api/logs')
def api_logs():
    if request.args.get('secret') != 'superadmin123':
        return jsonify({"error": "Unauthorized"}), 401
        
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM logs ORDER BY timestamp DESC LIMIT 100")
    rows = c.fetchall()
    
    logs = []
    for row in rows:
        logs.append({
            "id": row["id"],
            "ip_address": row["ip_address"],
            "timestamp": row["timestamp"],
            "attack_type": row["attack_type"],
            "username": row["username"],
            "password_attempt": row["password_attempt"]
        })
    conn.close()
    return jsonify(logs)

if __name__ == '__main__':
    init_db()
    # Run on all interfaces to capture external attacks if desired, but default to localhost for safety
    app.run(host='0.0.0.0', port=5000, debug=True)
