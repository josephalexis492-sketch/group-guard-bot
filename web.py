from flask import Flask, jsonify
from main import stats

app = Flask(__name__)

@app.route("/")
def dashboard():
    return f"""
    <h1>Verifier Dashboard</h1>
    <p>Total Joins: {stats['joins']}</p>
    <p>Verified: {stats['verified']}</p>
    <p>Kicked: {stats['kicked']}</p>
    """

@app.route("/api")
def api():
    return jsonify(stats)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)