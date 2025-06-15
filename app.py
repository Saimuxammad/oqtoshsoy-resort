import os
import sys
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

# Создаем Flask приложение
app = Flask(__name__)
CORS(app)

# Конфигурация
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Простая база данных в памяти для начала
ROOMS_DATA = [
    {
        'id': 1,
        'name': 'Стандартный номер',
        'capacity': 2,
        'weekdayPrice': {'without': 350000, 'with': 450000},
        'weekendPrice': {'without': 400000, 'with': 500000},
        'description': 'Уютный стандартный номер с базовыми удобствами'
    },
    {
        'id': 2,
        'name': 'Люкс номер',
        'capacity': 4,
        'weekdayPrice': {'without': 600000, 'with': 750000},
        'weekendPrice': {'without': 700000, 'with': 850000},
        'description': 'Просторный люкс с видом на горы'
    },
    {
        'id': 3,
        'name': 'Семейный номер',
        'capacity': 6,
        'weekdayPrice': {'without': 800000, 'with': 1000000},
        'weekendPrice': {'without': 950000, 'with': 1200000},
        'description': 'Большой семейный номер для комфортного отдыха'
    }
]


@app.route('/')
def index():
    """Главная страница"""
    return """
    <html>
    <head>
        <title>🏔️ Oqtoshsoy Resort</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
            h1 { color: #2c5f2d; text-align: center; }
            .btn { background: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin: 5px; }
            .btn:hover { background: #45a049; }
            .status { background: #e7f3e7; padding: 15px; border-radius: 5px; margin: 20px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏔️ Горный Курорт Oqtoshsoy</h1>

            <div class="status">
                ✅ <strong>Сайт успешно запущен!</strong><br>
                🕐 Время сервера: """ + datetime.now().strftime('%d.%m.%Y %H:%M:%S') + """<br>
                🤖 Telegram бот: Работает<br>
                🌐 Web API: Активен
            </div>

            <h2>🎯 Доступные функции:</h2>
            <a href="/api/rooms" class="btn">📋 API - Номера</a>
            <a href="/api/test" class="btn">🔧 Тест API</a>
            <a href="/health" class="btn">💚 Health Check</a>

            <h2>📱 Telegram бот:</h2>
            <p>Найдите нашего бота в Telegram: <strong>@your_resort_bot</strong></p>

            <h2>🏨 О курорте:</h2>
            <p>Горный курорт Oqtoshsoy предлагает незабываемый отдых в живописной местности с чистым горным воздухом.</p>

            <h3>🌟 Удобства:</h3>
            <ul>
                <li>30+ комфортных номеров</li>
                <li>Бассейн с видом на горы</li>
                <li>Теннис и настольный теннис</li>
                <li>Детская игровая зона</li>
                <li>Питание по желанию</li>
            </ul>
        </div>
    </body>
    </html>
    """


@app.route('/health')
def health():
    """Health check для Railway"""
    return jsonify({
        'status': 'healthy',
        'service': 'Oqtoshsoy Resort API',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })


@app.route('/api/test')
def api_test():
    """Тест API"""
    return jsonify({
        'status': 'success',
        'message': 'API работает отлично!',
        'timestamp': datetime.now().isoformat(),
        'data': {
            'resort_name': 'Oqtoshsoy Resort',
            'location': 'Ташкентская область',
            'features': ['Горы', 'Бассейн', 'Теннис', 'Детская зона']
        }
    })


@app.route('/api/rooms')
def api_rooms():
    """API для получения списка номеров"""
    return jsonify(ROOMS_DATA)


@app.route('/api/rooms/<int:room_id>')
def api_room_detail(room_id):
    """API для получения детальной информации о номере"""
    room = next((r for r in ROOMS_DATA if r['id'] == room_id), None)
    if room:
        return jsonify(room)
    return jsonify({'error': 'Room not found'}), 404


@app.route('/api/booking', methods=['POST'])
def api_booking():
    """API для создания бронирования"""
    try:
        data = request.get_json()

        # Базовая валидация
        required_fields = ['room_id', 'checkin_date', 'checkout_date', 'customer_name', 'customer_phone']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400

        # Создаем бронирование
        booking = {
            'booking_id': f"BK{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'status': 'pending',
            'created_at': datetime.now().isoformat(),
            **data
        }

        return jsonify({
            'success': True,
            'booking': booking,
            'message': 'Бронирование создано успешно!'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/mini-app')
def mini_app():
    """Мини-приложение для Telegram"""
    return """
    <html>
    <head>
        <title>Oqtoshsoy Resort - Бронирование</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f0f2f5; }
            .container { max-width: 400px; margin: 0 auto; }
            .card { background: white; padding: 20px; border-radius: 10px; margin: 10px 0; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
            .btn { background: #007AFF; color: white; padding: 12px; border: none; border-radius: 8px; width: 100%; font-size: 16px; }
            .btn:hover { background: #0056B3; }
            h1 { text-align: center; color: #2c5f2d; margin-bottom: 30px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏔️ Oqtoshsoy Resort</h1>

            <div class="card">
                <h3>📅 Быстрое бронирование</h3>
                <p>Выберите даты и номер для бронирования</p>
                <button class="btn" onclick="alert('Форма бронирования скоро будет готова!')">
                    Забронировать номер
                </button>
            </div>

            <div class="card">
                <h3>🏨 Наши номера</h3>
                <p>• Стандартный номер (2 гостя)<br>
                • Люкс номер (4 гостя)<br>
                • Семейный номер (6 гостей)</p>
                <button class="btn" onclick="loadRooms()">Посмотреть цены</button>
            </div>

            <div class="card">
                <h3>📞 Связаться с нами</h3>
                <button class="btn" onclick="window.open('tel:+998901234567')">
                    Позвонить
                </button>
            </div>
        </div>

        <script>
            function loadRooms() {
                fetch('/api/rooms')
                    .then(response => response.json())
                    .then(data => {
                        let info = 'Наши номера:\\n\\n';
                        data.forEach(room => {
                            info += room.name + ' - от ' + room.weekdayPrice.without.toLocaleString() + ' сум\\n';
                        });
                        alert(info);
                    })
                    .catch(error => alert('Ошибка загрузки данных'));
            }
        </script>
    </body>
    </html>
    """


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    # Для Railway используется переменная PORT
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)