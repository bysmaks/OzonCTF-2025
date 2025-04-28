from flask import Flask, send_from_directory, render_template, make_response

app = Flask(__name__)

# Отдает HTML страницу по пути "/"
@app.route('/')
def index():
    return render_template('index.html')

# Раздает файлы для всех остальных путей
@app.route('/<path:path>')
def serve_files(path):
    response = send_from_directory('static', path)
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    return response

if __name__=="__main__":
    app.run(host="0.0.0.0", port=8080)