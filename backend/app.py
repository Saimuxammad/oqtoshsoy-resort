import os
import sys
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import requests
import json
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///avtosay_resort.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_ADMIN_CHAT_ID')

db = SQLAlchemy(app)
migrate = Migrate(app, db)


# Database Models
class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    weekday_price_with_meal = db.Column(db.Integer, nullable=False)
    weekday_price_without_meal = db.Column(db.Integer, nullable=False)
    weekend_price_with_meal = db.Column(db.Integer, nullable=False)
    weekend_price_without_meal = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    bookings = db.relationship('Booking', backref='room', lazy=True)
    availability = db.relationship('Availability', backref='room', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'capacity': self.capacity,
            'weekdayPrice': {
                'with': self.weekday_price_with_meal,
                'without': self.weekday_price_without_meal
            },
            'weekendPrice': {
                'with': self.weekend_price_with_meal,
                'without': self.weekend_price_without_meal
            },
            'description': self.description,
            'image': self.image_url
        }


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_phone = db.Column(db.String(20), nullable=False)
    customer_email = db.Column(db.String(100))
    checkin_date = db.Column(db.Date, nullable=False)
    checkout_date = db.Column(db.Date, nullable=False)
    guests_count = db.Column(db.Integer, nullable=False)
    meal_option = db.Column(db.String(20), nullable=False)  # 'with' or 'without'
    total_price = db.Column(db.Integer, nullable=False)
    special_requests = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, cancelled
    telegram_user_id = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'room_name': self.room.name,
            'customer_name': self.customer_name,
            'customer_phone': self.customer_phone,
            'checkin_date': self.checkin_date.isoformat(),
            'checkout_date': self.checkout_date.isoformat(),
            'guests_count': self.guests_count,
            'meal_option': self.meal_option,
            'total_price': self.total_price,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }


class Availability(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    notes = db.Column(db.Text)

    __table_args__ = (db.UniqueConstraint('room_id', 'date'),)


class AdminUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    telegram_user_id = db.Column(db.Integer)
    role = db.Column(db.String(20), default='admin')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)

    return decorated_function


# Routes
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/rooms')
def get_rooms():
    rooms = Room.query.filter_by(is_active=True).all()
    return jsonify([room.to_dict() for room in rooms])


@app.route('/api/availability')
def check_availability():
    room_id = request.args.get('room_id', type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    if not all([room_id, start_date, end_date]):
        return jsonify({'error': 'Missing required parameters'}), 400

    try:
        start = datetime.strptime(start_date, '%Y-%m-%d').date()
        end = datetime.strptime(end_date, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400

    # Check if room exists
    room = Room.query.get(room_id)
    if not room:
        return jsonify({'error': 'Room not found'}), 404

    # Check availability for date range
    current_date = start
    availability_data = {}

    while current_date < end:
        availability = Availability.query.filter_by(
            room_id=room_id,
            date=current_date
        ).first()

        if availability:
            availability_data[current_date.isoformat()] = availability.is_available
        else:
            # If no record exists, assume available
            availability_data[current_date.isoformat()] = True

        current_date += timedelta(days=1)

    return jsonify({
        'room_id': room_id,
        'availability': availability_data
    })


@app.route('/api/booking', methods=['POST'])
def create_booking():
    data = request.get_json()

    required_fields = ['room_id', 'customer_name', 'customer_phone',
                       'checkin_date', 'checkout_date', 'guests_count',
                       'meal_option', 'total_price']

    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        checkin = datetime.strptime(data['checkin_date'], '%Y-%m-%d').date()
        checkout = datetime.strptime(data['checkout_date'], '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400

    # Validate dates
    if checkin >= checkout:
        return jsonify({'error': 'Checkout date must be after checkin date'}), 400

    if checkin < datetime.now().date():
        return jsonify({'error': 'Checkin date cannot be in the past'}), 400

    # Check room exists
    room = Room.query.get(data['room_id'])
    if not room:
        return jsonify({'error': 'Room not found'}), 404

    # Check availability
    current_date = checkin
    while current_date < checkout:
        availability = Availability.query.filter_by(
            room_id=data['room_id'],
            date=current_date
        ).first()

        if availability and not availability.is_available:
            return jsonify({'error': f'Room not available on {current_date}'}), 400

        current_date += timedelta(days=1)

    # Create booking
    booking = Booking(
        room_id=data['room_id'],
        customer_name=data['customer_name'],
        customer_phone=data['customer_phone'],
        customer_email=data.get('customer_email'),
        checkin_date=checkin,
        checkout_date=checkout,
        guests_count=data['guests_count'],
        meal_option=data['meal_option'],
        total_price=data['total_price'],
        special_requests=data.get('special_requests'),
        telegram_user_id=data.get('telegram_user_id')
    )

    try:
        db.session.add(booking)

        # Block dates in availability
        current_date = checkin
        while current_date < checkout:
            availability = Availability.query.filter_by(
                room_id=data['room_id'],
                date=current_date
            ).first()

            if availability:
                availability.is_available = False
            else:
                new_availability = Availability(
                    room_id=data['room_id'],
                    date=current_date,
                    is_available=False
                )
                db.session.add(new_availability)

            current_date += timedelta(days=1)

        db.session.commit()

        # Send notification to Telegram
        send_booking_notification(booking)

        return jsonify({
            'success': True,
            'booking_id': booking.id,
            'message': 'Booking created successfully'
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create booking'}), 500


@app.route('/api/booking/<int:booking_id>')
def get_booking(booking_id):
    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({'error': 'Booking not found'}), 404

    return jsonify(booking.to_dict())


@app.route('/api/booking/<int:booking_id>', methods=['PUT'])
@login_required
def update_booking(booking_id):
    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({'error': 'Booking not found'}), 404

    data = request.get_json()

    # Update allowed fields
    if 'status' in data:
        booking.status = data['status']
    if 'special_requests' in data:
        booking.special_requests = data['special_requests']

    booking.updated_at = datetime.utcnow()

    try:
        db.session.commit()
        return jsonify({'success': True, 'message': 'Booking updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update booking'}), 500


@app.route('/api/booking/<int:booking_id>', methods=['DELETE'])
@login_required
def cancel_booking(booking_id):
    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({'error': 'Booking not found'}), 404

    # Free up the dates
    current_date = booking.checkin_date
    while current_date < booking.checkout_date:
        availability = Availability.query.filter_by(
            room_id=booking.room_id,
            date=current_date
        ).first()

        if availability:
            availability.is_available = True

        current_date += timedelta(days=1)

    # Mark booking as cancelled instead of deleting
    booking.status = 'cancelled'
    booking.updated_at = datetime.utcnow()

    try:
        db.session.commit()

        # Send cancellation notification
        send_cancellation_notification(booking)

        return jsonify({'success': True, 'message': 'Booking cancelled successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to cancel booking'}), 500


# Admin routes
@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400

    admin = AdminUser.query.filter_by(username=username, is_active=True).first()

    if admin and check_password_hash(admin.password_hash, password):
        session['admin_logged_in'] = True
        session['admin_id'] = admin.id
        return jsonify({'success': True, 'message': 'Login successful'})

    return jsonify({'error': 'Invalid credentials'}), 401


@app.route('/api/admin/logout', methods=['POST'])
def admin_logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_id', None)
    return jsonify({'success': True, 'message': 'Logged out successfully'})


@app.route('/api/admin/bookings')
@login_required
def admin_get_bookings():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')

    query = Booking.query

    if status:
        query = query.filter_by(status=status)

    bookings = query.order_by(Booking.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'bookings': [booking.to_dict() for booking in bookings.items],
        'total': bookings.total,
        'pages': bookings.pages,
        'current_page': page
    })


@app.route('/api/admin/stats')
@login_required
def admin_stats():
    today = datetime.now().date()

    # Total bookings
    total_bookings = Booking.query.count()

    # Bookings today
    bookings_today = Booking.query.filter(
        Booking.created_at >= today
    ).count()

    # Active bookings
    active_bookings = Booking.query.filter(
        Booking.status.in_(['pending', 'confirmed']),
        Booking.checkout_date >= today
    ).count()

    # Revenue this month
    start_of_month = today.replace(day=1)
    monthly_revenue = db.session.query(db.func.sum(Booking.total_price)).filter(
        Booking.created_at >= start_of_month,
        Booking.status.in_(['confirmed', 'pending'])
    ).scalar() or 0

    # Occupancy rate for next 30 days
    occupied_days = 0
    total_days = 0

    for i in range(30):
        check_date = today + timedelta(days=i)
        for room in Room.query.filter_by(is_active=True).all():
            total_days += 1
            availability = Availability.query.filter_by(
                room_id=room.id,
                date=check_date,
                is_available=False
            ).first()
            if availability:
                occupied_days += 1

    occupancy_rate = (occupied_days / total_days * 100) if total_days > 0 else 0

    return jsonify({
        'total_bookings': total_bookings,
        'bookings_today': bookings_today,
        'active_bookings': active_bookings,
        'monthly_revenue': monthly_revenue,
        'occupancy_rate': round(occupancy_rate, 1)
    })


@app.route('/api/admin/availability', methods=['POST'])
@login_required
def update_availability():
    data = request.get_json()
    room_id = data.get('room_id')
    date_str = data.get('date')
    is_available = data.get('is_available')

    if not all([room_id, date_str, is_available is not None]):
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400

    # Check if room exists
    room = Room.query.get(room_id)
    if not room:
        return jsonify({'error': 'Room not found'}), 404

    # Update or create availability record
    availability = Availability.query.filter_by(
        room_id=room_id,
        date=date
    ).first()

    if availability:
        availability.is_available = is_available
    else:
        availability = Availability(
            room_id=room_id,
            date=date,
            is_available=is_available
        )
        db.session.add(availability)

    try:
        db.session.commit()
        return jsonify({'success': True, 'message': 'Availability updated'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update availability'}), 500


# Telegram webhook
@app.route('/webhook/telegram', methods=['POST'])
def telegram_webhook():
    data = request.get_json()

    if 'message' in data:
        message = data['message']
        chat_id = message['chat']['id']
        text = message.get('text', '')

        # Handle Telegram bot commands
        if text.startswith('/start'):
            send_telegram_message(chat_id, get_welcome_message())
        elif text.startswith('/rooms'):
            send_rooms_info(chat_id)
        elif text.startswith('/book'):
            send_booking_instructions(chat_id)
        elif text.startswith('/help'):
            send_help_message(chat_id)

    return jsonify({'ok': True})


# Utility functions
def send_telegram_message(chat_id, text, keyboard=None):
    """Send message to Telegram"""
    if not TELEGRAM_BOT_TOKEN:
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML'
    }

    if keyboard:
        payload['reply_markup'] = keyboard

    try:
        response = requests.post(url, json=payload)
        return response.status_code == 200
    except Exception as e:
        print(f"Error sending Telegram message: {e}")
        return False


def send_booking_notification(booking):
    """Send booking notification to admin"""
    message = f"""
🆕 <b>Новое бронирование!</b>

📋 <b>Детали:</b>
• Номер: {booking.room.name}
• Гость: {booking.customer_name}
• Телефон: {booking.customer_phone}
• Даты: {booking.checkin_date} - {booking.checkout_date}
• Гостей: {booking.guests_count}
• Питание: {'С питанием' if booking.meal_option == 'with' else 'Без питания'}
• Сумма: {booking.total_price:,} сум

💬 Особые пожелания: {booking.special_requests or 'Нет'}

🆔 ID бронирования: {booking.id}
    """

    if TELEGRAM_CHAT_ID:
        send_telegram_message(TELEGRAM_CHAT_ID, message)


def send_cancellation_notification(booking):
    """Send cancellation notification"""
    message = f"""
❌ <b>Отмена бронирования</b>

📋 <b>Детали:</b>
• ID: {booking.id}
• Номер: {booking.room.name}
• Гость: {booking.customer_name}
• Даты: {booking.checkin_date} - {booking.checkout_date}
• Сумма: {booking.total_price:,} сум
    """

    if TELEGRAM_CHAT_ID:
        send_telegram_message(TELEGRAM_CHAT_ID, message)


def get_welcome_message():
    """Get welcome message for Telegram bot"""
    return """
🏔️ <b>Добро пожаловать в Горный Курорт Автосай!</b>

Мы предлагаем комфортный отдых в живописной горной местности Ташкентской области.

<b>Что вы можете сделать:</b>
/rooms - Посмотреть номера и цены
/book - Забронировать номер
/contact - Связаться с нами
/help - Получить помощь

🌐 Наш сайт: [ссылка на сайт]
📱 Instagram: @avtosay_resort
"""


def send_rooms_info(chat_id):
    """Send rooms information"""
    rooms = Room.query.filter_by(is_active=True).all()

    message = "🏠 <b>Наши номера:</b>\n\n"

    for room in rooms:
        message += f"""
<b>{room.name}</b> (до {room.capacity} гостей)
💰 Будни: {room.weekday_price_without_meal:,} - {room.weekday_price_with_meal:,} сум
💰 Выходные: {room.weekend_price_without_meal:,} - {room.weekend_price_with_meal:,} сум

"""

    message += "\nДля бронирования используйте команду /book"
    send_telegram_message(chat_id, message)


def send_booking_instructions(chat_id):
    """Send booking instructions"""
    message = """
📝 <b>Бронирование номера</b>

Для бронирования номера:
1. Перейдите на наш сайт: [ссылка]
2. Выберите даты и количество гостей
3. Выберите подходящий номер
4. Заполните контактные данные
5. Подтвердите бронирование

Или свяжитесь с нами напрямую:
📞 +998 XX XXX XX XX
📧 info@avtosay-resort.uz

Мы ответим в течение нескольких минут!
"""
    send_telegram_message(chat_id, message)


def send_help_message(chat_id):
    """Send help message"""
    message = """
ℹ️ <b>Помощь</b>

<b>Доступные команды:</b>
/start - Главное меню
/rooms - Номера и цены
/book - Бронирование
/contact - Контакты
/help - Эта справка

<b>О курорте:</b>
🏔️ Горный курорт в Ташкентской области
🏊 Бассейн, теннис, бильярд
👨‍👩‍👧‍👦 Семейный отдых
🍽️ Питание по желанию

<b>Связь с нами:</b>
📞 +998 XX XXX XX XX
📧 info@avtosay-resort.uz
📱 @avtosay_resort
"""
    send_telegram_message(chat_id, message)


# Initialize database
def init_db():
    """Initialize database with sample data"""
    db.create_all()

    # Check if rooms already exist
    if Room.query.count() == 0:
        # Add sample rooms
        rooms_data = [
            {
                'name': 'Двухместный Стандарт',
                'capacity': 2,
                'weekday_price_with_meal': 300000,
                'weekday_price_without_meal': 250000,
                'weekend_price_with_meal': 400000,
                'weekend_price_without_meal': 350000,
                'description': 'Уютный номер для двоих с прекрасным видом на горы'
            },
            {
                'name': 'Двухместный Люкс',
                'capacity': 2,
                'weekday_price_with_meal': 450000,
                'weekday_price_without_meal': 400000,
                'weekend_price_with_meal': 550000,
                'weekend_price_without_meal': 500000,
                'description': 'Роскошный номер люкс для особых случаев'
            },
            {
                'name': 'Четырехместный Стандарт',
                'capacity': 4,
                'weekday_price_with_meal': 500000,
                'weekday_price_without_meal': 450000,
                'weekend_price_with_meal': 650000,
                'weekend_price_without_meal': 600000,
                'description': 'Просторный номер для семьи или компании друзей'
            },
            {
                'name': 'Четырехместный Малый VIP',
                'capacity': 4,
                'weekday_price_with_meal': 700000,
                'weekday_price_without_meal': 650000,
                'weekend_price_with_meal': 850000,
                'weekend_price_without_meal': 800000,
                'description': 'VIP номер с дополнительными удобствами'
            },
            {
                'name': 'Четырехместный Большой VIP',
                'capacity': 4,
                'weekday_price_with_meal': 900000,
                'weekday_price_without_meal': 850000,
                'weekend_price_with_meal': 1100000,
                'weekend_price_without_meal': 1050000,
                'description': 'Большой VIP номер с эксклюзивными услугами'
            },
            {
                'name': 'Четырехместный Апартамент',
                'capacity': 4,
                'weekday_price_with_meal': 800000,
                'weekday_price_without_meal': 750000,
                'weekend_price_with_meal': 1000000,
                'weekend_price_without_meal': 950000,
                'description': 'Апартамент с кухней и гостиной зоной'
            },
            {
                'name': 'Шестиместный Коттедж',
                'capacity': 6,
                'weekday_price_with_meal': 1200000,
                'weekday_price_without_meal': 1150000,
                'weekend_price_with_meal': 1500000,
                'weekend_price_without_meal': 1450000,
                'description': 'Отдельный коттедж для большой компании'
            },
            {
                'name': 'Восьмиместный Президентский',
                'capacity': 8,
                'weekday_price_with_meal': 2000000,
                'weekday_price_without_meal': 1950000,
                'weekend_price_with_meal': 2500000,
                'weekend_price_without_meal': 2450000,
                'description': 'Президентский апартамент максимального комфорта'
            }
        ]

        for room_data in rooms_data:
            room = Room(**room_data)
            db.session.add(room)

        # Add admin user
        admin = AdminUser(
            username='admin',
            password_hash=generate_password_hash('admin123'),
            role='admin'
        )
        db.session.add(admin)

        db.session.commit()
        print("Database initialized with sample data")


if __name__ == '__main__':
    with app.app_context():
        init_db()

    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=os.environ.get('FLASK_ENV') == 'development')