import sys

from flask import Flask, render_template, request, jsonify

from src.web import processing

app = Flask(__name__, template_folder="./web/templates", static_folder="./web/static")

@app.route('/')
def index():
    return render_template('main.html')

@app.route('/input', methods=['POST'])
def handle_input():
    data = request.get_json()
    result = processing(data["urls"], data["min_quality"])
    return result
    
if __name__ == '__main__':
    app.run()
