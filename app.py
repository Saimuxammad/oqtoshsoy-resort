import sys
import os

# Добавляем папку backend в путь
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Импортируем основное приложение из backend/app.py
from backend.app import app

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
