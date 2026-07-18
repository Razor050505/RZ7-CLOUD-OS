from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/status")
def status():
    return {
        "project": "RZ7 CLOUD OS",
        "version": "0.1-alpha",
        "status": "ONLINE"
    }

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)