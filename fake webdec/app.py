from flask import Flask, request, jsonify, render_template
import whois
from datetime import datetime
import sqlite3




app = Flask(__name__)



@app.route('/')
def home():
    return render_template('index.html')

@app.route('/check', methods=['POST'])
def check_website():
    data = request.get_json()
    url = data.get('url')
    

    # Input validation
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    score = 100
    reasons = []

    # HTTPS check
    https_score, https_status = check_https(url)
    score += https_score
    if https_score < 0:
        reasons.append("Website does not use HTTPS")
        
    


    # URL length check
    score += check_url_length(url)

    # Keyword check
    keyword_score = check_keywords(url)
    score += keyword_score
    if keyword_score < 0:
        reasons.append("Suspicious keywords found in URL")
        
    

    
    #Domain structure check
    score += check_domain_structure(url)
    #ip adrdress check
    ip_score = check_ip_address(url)
    score += ip_score

    if ip_score < 0:
        reasons.append("IP address used instead of domain name")
        
    

    
    #suspicious path check 
    path_score = check_suspicious_paths(url)
    score += path_score

    if path_score < 0:
        reasons.append("Suspicious URL path detected (login/reset/verify)")
        
    



    #Subdomain check
    score += check_subdomain_count(url)
    
    #Suspicious tld check
    tld_score = check_suspicious_tld(url)
    score += tld_score

    if tld_score < 0:
        reasons.append("Suspicious top-level domain used")
        
    

    
    
    # Domain age check
    domain_age_score, domain_age_years = check_domain_age(url)
    score += domain_age_score
    # Website category detection
    category = categorize_website(url)


    if domain_age_years is None:
        reasons.append("Domain age could not be determined")
        
    elif domain_age_years < 1:
        reasons.append("Domain is very new")
    


        



    
    #Trusted domins list 
    if extract_domain(url) in TRUSTED_DOMAINS:
        score = max(score, 85)

    # Keep score within 0–100
    score = max(0, min(score, 100))
    
    # Final classification
    # Final classification
    if score >= 80:
        result = "Safe"
        
    elif score >= 50:
        result = "Suspicious"
    else:
        result = "Fake"
    if not reasons:
        reasons.append("No major risk indicators detected")
    # Save scan to database
    import sqlite3

    conn = sqlite3.connect("website_scans.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO scans (url, score, result, category)
    VALUES (?, ?, ?, ?)
    """, (url, score, result, category))

    conn.commit()
    conn.close()

      
    
        

    return jsonify({
    "url": url,
    "https": https_status,
    "score": score,
    "result": result,
    "reasons": reasons,
    "category": category
})









def check_https(url):
    if url.startswith("https://"):
        return 0, "secure"
    return -25, "not secure"



def check_url_length(url):
    length = len(url)

    if length > 100:
        return -25
    elif length > 60:
        return -10
    else:
        return 0



def check_keywords(url):
    high_risk = [
        "login", "verify", "update", "secure", "account",
        "bank", "free", "signin", "confirm", "password"
    ]

    score = 0
    url_lower = url.lower()

    for word in high_risk:
        if word in url_lower:
            score -= 5

    return score

def check_domain_structure(url):
    score = 0

    if url.count("-") >= 3:
        score -= 15

    if url.count(".") > 3:
        score -= 10

    return score

import re

def check_ip_address(url):
    # Matches IPv4 addresses
    ip_pattern = r"(?:\d{1,3}\.){3}\d{1,3}"

    if re.search(ip_pattern, url):
        return -40  # heavy penalty
    return 0

def check_suspicious_paths(url):
    suspicious_paths = [
        "login",
        "verify",
        "update",
        "secure",
        "account",
        "password",
        "signin",
        "reset"
    ]

    score = 0
    url_lower = url.lower()

    for word in suspicious_paths:
        if f"/{word}" in url_lower:
            score -= 8 # medium penalty per match

    return score


def check_subdomain_count(url):
    score = 0

    # remove protocol
    clean_url = url.replace("https://", "").replace("http://", "")

    parts = clean_url.split(".")

    if len(parts) > 4:
        score -= 20

    return score



def check_suspicious_tld(url):
    suspicious_tlds = [
        ".tk", ".xyz", ".zip", ".click", ".top", ".gq", ".ml"
    ]

    for tld in suspicious_tlds:
        if url.endswith(tld) or tld + "/" in url:
            return -25

    return 0


def check_domain_age(url):
    try:
        domain = url.replace("http://", "").replace("https://", "").split("/")[0]
        w = whois.whois(domain)

        creation_date = w.creation_date

        if isinstance(creation_date, list):
            creation_date = creation_date[0]

        if not creation_date:
            return 0, None

        age_days = (datetime.now() - creation_date).days
        age_years = round(age_days / 365, 1)

        # scoring
        if age_days < 30:
            score = -40
        elif age_days < 180:
            score = -20 
        elif age_days < 365:
            score = -10
        else:
            score = 0

        return score, age_years

    except Exception:
        return -10, None
from urllib.parse import urlparse

def extract_domain(url):
    parsed = urlparse(url)
    domain = parsed.netloc

    # remove www.
    if domain.startswith("www."):
        domain = domain[4:]

    return domain
def keyword_category(url):
    url_lower = url.lower()

    if any(word in url_lower for word in ["bank", "finance", "loan", "pay"]):
        return "Banking / Finance"

    elif any(word in url_lower for word in ["shop", "store", "cart", "buy"]):
        return "E-commerce"

    elif any(word in url_lower for word in ["college", "university", ".edu"]):
        return "Education"

    elif any(word in url_lower for word in ["tech", "software", "cloud"]):
        return "Technology"

    elif any(word in url_lower for word in ["facebook", "instagram", "twitter"]):
        return "Social Media"

    return "Unknown"
def categorize_website(url):
    domain = extract_domain(url).lower()

    # TLD based detection
    if domain.endswith(".edu"):
        return "Education"
    if domain.endswith(".gov"):
        return "Government"

    # Keyword detection inside domain
    if any(word in domain for word in ["bank", "finance", "pay", "loan"]):
        return "Banking / Finance"

    if any(word in domain for word in ["shop", "store", "cart", "buy"]):
        return "E-commerce"

    if any(word in domain for word in ["tech", "cloud", "software", "ai"]):
        return "Technology"

    if any(word in domain for word in ["facebook", "instagram", "twitter"]):
        return "Social Media"

    return "General"





TRUSTED_DOMAINS = [
    "google.com",
    "github.com",
    "microsoft.com",
    "apple.com",
    "amazon.com"
]
KNOWN_WEBSITES = {
    "google.com": "Technology",
    "amazon.com": "E-commerce",
    "flipkart.com": "E-commerce",
    "sbi.co.in": "Banking",
    "icicibank.com": "Banking",
    "github.com": "Technology",
    "facebook.com": "Social Media",
    "instagram.com": "Social Media",
    "mit.edu": "Education",
    "wikipedia.org": "Information"
}
# ======================
# DATABASE INITIALIZATION
# ======================

def init_db():
    conn = sqlite3.connect("website_scans.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT,
            category TEXT,
            score INTEGER,
            result TEXT,
            domain_age REAL,
            scan_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()

@app.route("/history")
def history():

    conn = sqlite3.connect("website_scans.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM scans")
    rows = cursor.fetchall()

    conn.close()

    grouped = {}

    for row in rows:
        category = row[2] or "Uncategorized"

        if category not in grouped:
            grouped[category] = []

        grouped[category].append(row)

    return render_template("history.html", grouped=grouped)








init_db()

if __name__ == "__main__":
    app.run(debug=True)
