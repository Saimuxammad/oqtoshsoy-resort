import os
import sys
from flask import Flask, render_template

# Добавляем путь к templates
template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frontend', 'templates')
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frontend', 'static')

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.config['SECRET_KEY'] = 'test-key'

@app.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        return f'''
        <h1>🔧 Диагностика ошибки:</h1>
        <p><strong>Ошибка:</strong> {str(e)}</p>
        <p><strong>Template dir:</strong> {template_dir}</p>
        <p><strong>Template exists:</strong> {os.path.exists(os.path.join(template_dir, 'index.html'))}</p>
        <p><strong>Static dir:</strong> {static_dir}</p>
        <hr>
        <h2>🏔️ Простая страница курорта:</h2>
        <h1>Добро пожаловать в Oqtoshsoy Resort!</h1>
        <p>Сайт работает, исправляем шаблоны...</p>
        '''

@app.route('/test')
def test():
    return '<h1>✅ Тестовая страница работает!</h1>'

if __name__ == '__main__':
    print("🚀 Запуск диагностического сервера...")
    print(f"📁 Templates: {template_dir}")
    print(f"📁 Static: {static_dir}")
    app.run(debug=True, host='0.0.0.0', port=5000)