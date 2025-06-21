import os
import sys
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

# Создаем Flask приложение
app = Flask(__name__)
CORS(app)

# Конфигурация из переменных окружения
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
ADMIN_CHAT_ID = os.environ.get('TELEGRAM_ADMIN_CHAT_ID')
WEBAPP_URL = os.environ.get('WEBAPP_URL', 'https://web-production-268a.up.railway.app')
RESORT_NAME = os.environ.get('RESORT_NAME', 'Горный Курорт Oqtoshsoy')
RESORT_PHONE = os.environ.get('RESORT_PHONE', '+998 90 123 45 67')
DEBUG = os.environ.get('DEBUG', 'false').lower() == 'true'

print(f"🔧 Конфигурация:")
print(f"   WEBAPP_URL: {WEBAPP_URL}")
print(f"   RESORT_NAME: {RESORT_NAME}")
print(f"   BOT_TOKEN: {'✅ Set' if TELEGRAM_BOT_TOKEN else '❌ Missing'}")
print(f"   ADMIN_CHAT: {'✅ Set' if ADMIN_CHAT_ID else '❌ Missing'}")

# Импорт базы данных
try:
    from database import init_database, get_rooms, create_booking, get_booking, get_setting

    # Инициализируем базу данных при запуске
    init_database()
    print("✅ База данных подключена")
    USE_DATABASE = True
except ImportError:
    print("⚠️ Файл database.py не найден, используем данные в памяти")
    USE_DATABASE = False
    # Fallback данные если нет database.py
    ROOMS_DATA = [
        {
            'id': 1,
            'name': 'Двухместный Стандарт',
            'capacity': 2,
            'weekdayPrice': {'without': 250000, 'with': 300000},
            'weekendPrice': {'without': 350000, 'with': 400000},
            'description': 'Уютный номер для двоих с прекрасным видом на горы',
            'amenities': ['Wi-Fi', 'Кондиционер', 'Телевизор']
        },
        {
            'id': 2,
            'name': 'Двухместный Люкс',
            'capacity': 2,
            'weekdayPrice': {'without': 400000, 'with': 450000},
            'weekendPrice': {'without': 500000, 'with': 550000},
            'description': 'Роскошный номер люкс для особых случаев',
            'amenities': ['Wi-Fi', 'Кондиционер', 'Телевизор', 'Мини-бар']
        },
        {
            'id': 3,
            'name': 'Четырехместный Стандарт',
            'capacity': 4,
            'weekdayPrice': {'without': 450000, 'with': 500000},
            'weekendPrice': {'without': 600000, 'with': 650000},
            'description': 'Просторный номер для семьи или компании друзей',
            'amenities': ['Wi-Fi', 'Кондиционер', 'Телевизор', 'Холодильник']
        },
        {
            'id': 4,
            'name': 'Четырехместный VIP',
            'capacity': 4,
            'weekdayPrice': {'without': 650000, 'with': 700000},
            'weekendPrice': {'without': 800000, 'with': 850000},
            'description': 'VIP номер с дополнительными удобствами',
            'amenities': ['Wi-Fi', 'Кондиционер', 'Телевизор', 'Мини-бар', 'Балкон']
        },
        {
            'id': 5,
            'name': 'Шестиместный Коттедж',
            'capacity': 6,
            'weekdayPrice': {'without': 1150000, 'with': 1200000},
            'weekendPrice': {'without': 1450000, 'with': 1500000},
            'description': 'Отдельный коттедж для большой компании',
            'amenities': ['Wi-Fi', 'Кондиционер', 'Телевизор', 'Кухня', 'Терраса']
        }
    ]


@app.route('/')
def index():
    """Главная страница"""
    return f"""
    <html>
    <head>
        <title>🏔️ {RESORT_NAME}</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                margin: 0; 
                padding: 20px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }}
            .container {{ 
                max-width: 900px; 
                margin: 0 auto; 
                background: white; 
                padding: 40px; 
                border-radius: 20px; 
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            }}
            h1 {{ color: #2c5f2d; text-align: center; margin-bottom: 30px; font-size: 2.5em; }}
            .btn {{ 
                background: #4CAF50; 
                color: white; 
                padding: 12px 24px; 
                text-decoration: none; 
                border-radius: 8px; 
                margin: 8px; 
                display: inline-block;
                transition: all 0.3s ease;
            }}
            .btn:hover {{ background: #45a049; transform: translateY(-2px); }}
            .status {{ 
                background: #e7f3e7; 
                padding: 20px; 
                border-radius: 10px; 
                margin: 20px 0; 
                border-left: 5px solid #4CAF50;
            }}
            .feature-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin: 30px 0;
            }}
            .feature-card {{
                background: #f8f9fa;
                padding: 20px;
                border-radius: 10px;
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏔️ {RESORT_NAME}</h1>

            <div class="status">
                <h3>✅ Система активна!</h3>
                🕐 <strong>Время сервера:</strong> {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}<br>
                🤖 <strong>Telegram бот:</strong> {'✅ Подключен' if TELEGRAM_BOT_TOKEN else '❌ Не настроен'}<br>
                💾 <strong>База данных:</strong> {'✅ SQLite' if USE_DATABASE else '⚠️ В памяти'}<br>
                📞 <strong>Телефон:</strong> {RESORT_PHONE}
            </div>

            <h2>🎯 API и функции:</h2>
            <div style="text-align: center;">
                <a href="/api/rooms" class="btn">📋 Список номеров</a>
                <a href="/api/test" class="btn">🔧 Тест API</a>
                <a href="/health" class="btn">💚 Health Check</a>
                <a href="/mini-app" class="btn">📱 Мини-приложение</a>
            </div>

            <div class="feature-grid">
                <div class="feature-card">
                    <h3>🏨 Номера</h3>
                    <p>От стандартных до VIP апартаментов</p>
                </div>
                <div class="feature-card">
                    <h3>🏊 Бассейн</h3>
                    <p>Панорамный бассейн с видом на горы</p>
                </div>
                <div class="feature-card">
                    <h3>🎾 Спорт</h3>
                    <p>Теннис, настольный теннис, бильярд</p>
                </div>
                <div class="feature-card">
                    <h3>👨‍👩‍👧‍👦 Семейный отдых</h3>
                    <p>Детская площадка и развлечения</p>
                </div>
            </div>

            <h2>📱 Telegram бот:</h2>
            <p style="text-align: center;">
                Найдите нашего бота в Telegram: <strong>@oqtoshsoy_resort_bot</strong><br>
                <small>Бронирование, информация о номерах, поддержка 24/7</small>
            </p>
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
        'version': '2.0.0',
        'database': 'sqlite' if USE_DATABASE else 'memory',
        'telegram_bot': 'configured' if TELEGRAM_BOT_TOKEN else 'not_configured'
    })


@app.route('/api/test')
def api_test():
    """Тест API"""
    return jsonify({
        'status': 'success',
        'message': 'API работает отлично!',
        'timestamp': datetime.now().isoformat(),
        'data': {
            'resort_name': RESORT_NAME,
            'location': 'Ташкентская область',
            'features': ['Горы', 'Бассейн', 'Теннис', 'Детская зона'],
            'webapp_url': WEBAPP_URL,
            'phone': RESORT_PHONE,
            'database_type': 'SQLite' if USE_DATABASE else 'Memory'
        }
    })


@app.route('/api/rooms')
def api_rooms():
    """API для получения списка номеров"""
    try:
        if USE_DATABASE:
            rooms = get_rooms()
            return jsonify(rooms)
        else:
            # Fallback к данным в памяти
            return jsonify(ROOMS_DATA)
    except Exception as e:
        print(f"Error getting rooms: {e}")
        return jsonify(ROOMS_DATA)


@app.route('/api/rooms/<int:room_id>')
def api_room_detail(room_id):
    """API для получения детальной информации о номере"""
    try:
        if USE_DATABASE:
            rooms = get_rooms()
            room = next((r for r in rooms if r['id'] == room_id), None)
        else:
            room = next((r for r in ROOMS_DATA if r['id'] == room_id), None)

        if room:
            return jsonify(room)
        return jsonify({'error': 'Room not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


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

        # Проверяем даты
        try:
            checkin = datetime.strptime(data['checkin_date'], '%Y-%m-%d').date()
            checkout = datetime.strptime(data['checkout_date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format (use YYYY-MM-DD)'}), 400

        if checkin >= checkout:
            return jsonify({'error': 'Checkout date must be after checkin date'}), 400

        if checkin < datetime.now().date():
            return jsonify({'error': 'Checkin date cannot be in the past'}), 400

        # Создаем бронирование
        if USE_DATABASE:
            booking_id = create_booking(data)
            booking = get_booking(booking_id)
        else:
            # Fallback для памяти
            booking = {
                'booking_id': f"BK{datetime.now().strftime('%Y%m%d%H%M%S')}",
                'status': 'pending',
                'created_at': datetime.now().isoformat(),
                **data
            }

        # Отправляем уведомление в Telegram
        if TELEGRAM_BOT_TOKEN and ADMIN_CHAT_ID:
            send_booking_notification(booking, data)

        return jsonify({
            'success': True,
            'booking': booking,
            'message': 'Бронирование создано успешно!'
        })

    except Exception as e:
        print(f"Booking error: {e}")
        return jsonify({'error': 'Internal server error'}), 500


def send_booking_notification(booking, data):
    """Отправка уведомления о бронировании"""
    import requests

    try:
        # Получаем информацию о номере
        if USE_DATABASE:
            rooms = get_rooms()
            room = next((r for r in rooms if r['id'] == data['room_id']), None)
        else:
            room = next((r for r in ROOMS_DATA if r['id'] == data['room_id']), None)

        room_name = room['name'] if room else f"Номер #{data['room_id']}"

        message = f"""🆕 <b>Новое бронирование!</b>

📋 <b>Детали:</b>
• Номер: {room_name}
• Гость: {data['customer_name']}
• Телефон: {data['customer_phone']}
• Даты: {data['checkin_date']} - {data['checkout_date']}
• Гостей: {data.get('guests_count', 'не указано')}
• Питание: {data.get('meal_option', 'не указано')}

💬 Особые пожелания: {data.get('special_requests', 'Нет')}

🆔 ID: {booking.get('booking_id', 'N/A')}
🕐 Время: {datetime.now().strftime('%d.%m.%Y %H:%M')}
"""

        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            'chat_id': ADMIN_CHAT_ID,
            'text': message,
            'parse_mode': 'HTML'
        }

        response = requests.post(url, json=payload, timeout=10)
        print(f"Notification sent: {response.status_code}")

    except Exception as e:
        print(f"Failed to send notification: {e}")


@app.route('/mini-app')
def mini_app():
    """Мини-приложение для Telegram"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{RESORT_NAME} - Бронирование</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: #f0f2f5; 
                padding: 20px;
            }}
            .container {{ max-width: 400px; margin: 0 auto; }}
            .card {{ 
                background: white; 
                padding: 20px; 
                border-radius: 12px; 
                margin: 15px 0; 
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }}
            .btn {{ 
                background: #007AFF; 
                color: white; 
                padding: 14px; 
                border: none; 
                border-radius: 8px; 
                width: 100%; 
                font-size: 16px; 
                cursor: pointer;
                margin: 10px 0;
            }}
            .btn:hover {{ background: #0056B3; }}
            h1 {{ text-align: center; color: #2c5f2d; margin-bottom: 20px; }}
            h3 {{ color: #333; margin-bottom: 10px; }}
            .room-price {{ color: #007AFF; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏔️ {RESORT_NAME}</h1>

            <div class="card">
                <h3>📅 Быстрое бронирование</h3>
                <p>Выберите даты и номер для бронирования</p>
                <button class="btn" onclick="showBookingForm()">
                    Забронировать номер
                </button>
            </div>

            <div class="card">
                <h3>🏨 Наши номера</h3>
                <div id="rooms-list">
                    <p>Загрузка номеров...</p>
                </div>
                <button class="btn" onclick="loadRooms()">Обновить цены</button>
            </div>

            <div class="card">
                <h3>📞 Связаться с нами</h3>
                <button class="btn" onclick="window.open('tel:{RESORT_PHONE}')">
                    📞 Позвонить {RESORT_PHONE}
                </button>
            </div>

            <div class="card">
                <h3>ℹ️ О курорте</h3>
                <p>• 🏊 Бассейн с видом на горы<br>
                • 🎾 Теннис и настольный теннис<br>
                • 👨‍👩‍👧‍👦 Детская игровая зона<br>
                • 🍽️ Питание по желанию</p>
            </div>
        </div>

        <script>
            function loadRooms() {{
                fetch('/api/rooms')
                    .then(response => response.json())
                    .then(data => {{
                        let html = '';
                        data.forEach(room => {{
                            html += `
                                <div style="border-bottom: 1px solid #eee; padding: 10px 0;">
                                    <strong>${{room.name}}</strong> (до ${{room.capacity}} гостей)<br>
                                    <span class="room-price">
                                        От ${{room.weekdayPrice.without.toLocaleString()}} сум
                                    </span><br>
                                    <small>${{room.description}}</small>
                                </div>
                            `;
                        }});
                        document.getElementById('rooms-list').innerHTML = html;
                    }})
                    .catch(error => {{
                        document.getElementById('rooms-list').innerHTML = 
                            '<p style="color: red;">Ошибка загрузки номеров</p>';
                    }});
            }}

            function showBookingForm() {{
                alert('Форма бронирования скоро будет готова!\\n\\nА пока звоните: {RESORT_PHONE}');
            }}

            // Загружаем номера при старте
            loadRooms();
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


# Запуск приложения
if __name__ == '__main__':
    # Для Railway используется переменная PORT
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=DEBUG)