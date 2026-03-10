from flask import Flask, request, jsonify
from flask_cors import CORS
from flask import send_from_directory


app = Flask(__name__)
CORS(app)



@app.route("/api/health-check", methods=["POST"])
def health_check():
    data = request.get_json()
    text = data.get("text", "").lower()

    # Physical health keywords
    physical_high = ["vomiting", "dizziness", "high fever", "diagnosed"]
    physical_medium = ["fever", "body pain", "headache", "fatigue"]

    # Mental health keywords
    mental_low = ["feeling low", "stressed", "not motivated"]
    mental_high = ["burnt out", "overwhelmed", "anxious"]

    physical_score = 0
    mental_score = 0

    for w in physical_high:
        if w in text:
            physical_score += 40

    for w in physical_medium:
        if w in text:
            physical_score += 20

    for w in mental_high:
        if w in text:
            mental_score += 40

    for w in mental_low:
        if w in text:
            mental_score += 20

    if physical_score >= 40:
        physical_status = "Needs Rest & Care"
    elif physical_score >= 20:
        physical_status = "Monitor & Take Precautions"
    else:
        physical_status = "Physically Stable"

    if mental_score >= 40:
        mental_status = "Emotional Overload"
    elif mental_score >= 20:
        mental_status = "Low Mood / Stress"
    else:
        mental_status = "Mentally Stable"

    return jsonify({
        "physical_status": physical_status,
        "mental_status": mental_status,
        "message": "This is a self-reflection tool, not a medical diagnosis. Take care of yourself 💙"
    })
@app.route("/api/daily-quiz", methods=["POST"])
def daily_quiz():
    data = request.get_json()

    sleep = data.get("sleep")      # good / ok / poor
    stress = data.get("stress")    # low / medium / high
    energy = data.get("energy")    # high / medium / low

    score = 0

    if sleep == "poor":
        score += 20
    elif sleep == "ok":
        score += 10

    if stress == "high":
        score += 20
    elif stress == "medium":
        score += 10

    if energy == "low":
        score += 20
    elif energy == "medium":
        score += 10

    if score >= 40:
        status = "High Strain"
        message = "Your responses suggest you may need rest and support today."
    elif score >= 20:
        status = "Needs Attention"
        message = "Take small breaks and listen to your body."
    else:
        status = "Doing Well"
        message = "You seem to be managing well today. Keep taking care!"

    return jsonify({
        "daily_status": status,
        "score": score,
        "message": message
    })
@app.route("/ui")
def ui():
    return send_from_directory(".", "index.html")

@app.route("/")
def home():
    return send_from_directory(".", "index.html")



if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")

