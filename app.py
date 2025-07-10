from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
import requests
from config import Config
# Добавьте эти импорты в начало app.py
from flask_compress import Compress
from flask import send_from_directory
import mimetypes

# Также добавьте в requirements.txt:
# Flask-Compress==1.13

# После создания приложения Flask добавьте:
app = Flask(__name__)
app.config.from_object(Config)

# Настройка компрессии
Compress(app)
app.config['COMPRESS_MIMETYPES'] = [
    'text/html', 'text/css', 'text/xml', 'application/json',
    'application/javascript', 'image/svg+xml', 'image/jpeg',
    'image/png', 'image/webp'
]
app.config['COMPRESS_LEVEL'] = 6
app.config['COMPRESS_MIN_SIZE'] = 500

# Настройка кэширования для статических файлов
@app.after_request
def add_cache_headers(response):
    if request.path.startswith('/static/'):
        # Кэширование изображений на 30 дней
        if any(request.path.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.webp', '.ico']):
            response.cache_control.max_age = 2592000  # 30 дней
            response.cache_control.public = True
        # Кэширование CSS и JS на 7 дней
        elif any(request.path.endswith(ext) for ext in ['.css', '.js']):
            response.cache_control.max_age = 604800  # 7 дней
            response.cache_control.public = True
    return response

# Оптимизированная отдача статических файлов
@app.route('/static/<path:filename>')
def optimized_static(filename):
    # Установка правильных MIME типов
    mimetype = mimetypes.guess_type(filename)[0]
    return send_from_directory('static', filename, mimetype=mimetype)
app = Flask(__name__)
app.config.from_object(Config)

# Переводы для мультиязычности
translations = {
    'uz': {
        'nav_home': 'Bosh sahifa',
        'nav_rooms': 'Xonalar va narxlar',
        'nav_services': 'Xizmatlar',
        'nav_gallery': 'Galereya',
        'nav_booking': 'Bron qilish',
        'nav_contacts': 'Aloqa',
        'hero_title': 'OQTOSHSOY RESORT - PREMIUM TOG\' KURORTI',
        'hero_subtitle': 'Tabiat qo\'ynida hashamatli dam olish',
        'hero_cta': 'Hoziroq bron qiling',
        'about_title': 'Oqtoshsoy resort kurorti haqida',
        'about_text': 'Oqtoshsoy resort- Tyan-Shan tog\'larining bag\'rida, Oqtosh qishlog\'ida, dengiz sathidan 1100 metr balandlikda joylashgan noyob kurort. 2 gektar hududda joylashgan kurortimiz tog\' daryolari va keng bargli o\'rmonlar bilan o\'ralgan.',
        'features_comfort': 'Shinam xonalar',
        'features_nature': 'Betakror tabiat',
        'features_service': 'Premium xizmat',
        'features_health': 'Faol dam olish',
        'booking_title': 'Xona bron qilish',
        'booking_name': 'Ismingiz',
        'booking_phone': 'Telefon raqam',
        'booking_date_in': 'Kirish sanasi',
        'booking_date_out': 'Chiqish sanasi',
        'booking_room_type': 'Xona turi',
        'booking_guests': 'Mehmonlar soni',
        'booking_comment': 'Qo\'shimcha izoh',
        'booking_submit': 'Yuborish',
        'contact_title': 'Biz bilan bog\'lanish',
        'contact_phone': 'Telefon',
        'contact_address': 'Manzil',
        'rooms_title': 'Xonalar va narxlar',
        'services_title': 'Bizning xizmatlarimiz',
        'gallery_title': 'Foto galereya',
        'booking_success': 'Sizning so\'rovingiz muvaffaqiyatli yuborildi!',
        'booking_error': 'Xatolik yuz berdi. Iltimos, qayta urinib ko\'ring.',
        'with_meals': 'To\'liq ovqat bilan',
        'without_meals': 'Ovqatsiz',
        'weekdays': 'Ish kunlari',
        'weekends': 'Dam olish kunlari',
        'included_services': 'Narxga kiritilgan xizmatlar',
        'additional_services': 'Qo\'shimcha xizmatlar',
        'breakfast': 'Nonushta',
        'lunch': 'Tushlik',
        'dinner': 'Kechki ovqat',
        'pool': 'Basseyn (3 xil)',
        'tennis': 'Tennis stol',
        'playground': 'Bolalar maydonchasi',
        'parking': 'Avtoturargoh',
        'wifi': 'Wi-Fi',
        'billiard': 'Bilyard',
        'salt_room': 'Tuzli xona',
        'spa': 'Spa-protseduralar',
        'massage': 'Massaj',
        'sauna': 'Fin saunasi',
        'restaurant': 'Restoran',
        'gazebo_small': 'Kichik taptchan (7 kishi)',
        'gazebo_large': 'Katta taptchan (14 kishi)',
        'extra_mattress': 'Qo\'shimcha matras',
        'checkin': 'Kirish vaqti',
        'checkout': 'Chiqish vaqti',
        'family_only': 'Faqat oilaviy dam olish!',
        'reserve_now': 'Hoziroq bron qiling',
        'our_location': 'Bizning manzilimiz',
        'working_hours': 'Ish vaqti',
        'healing_air': 'Musaffo tog\' havosi',
        'healing_text': 'Oqtosh daryolaridan tabiiy gidroionizatsiya',
        'distance_capital': 'Toshkentdan 80 km',
        'eco_zone': 'Ekologik toza hudud',
        'year_round': 'Yil davomida dam olish',
        'special_offers': 'Maxsus takliflar',
        'honeymoon_package': 'Asal oyi paketi',
        'family_package': 'Oilaviy paket',
        'gps_coordinates': 'GPS koordinatalari'
    },
    'ru': {
        'nav_home': 'Главная',
        'nav_rooms': 'Номера и цены',
        'nav_services': 'Услуги',
        'nav_gallery': 'Галерея',
        'nav_booking': 'Бронирование',
        'nav_contacts': 'Контакты',
        'hero_title': 'OQTOSHSOY RESORT - ПРЕМИАЛЬНЫЙ ГОРНЫЙ КУРОРТ',
        'hero_subtitle': 'Роскошный отдых в объятиях природы',
        'hero_cta': 'Забронировать сейчас',
        'about_title': 'О курорте Oqtoshsoy resort',
        'about_text': 'Oqtoshsoy resort - уникальный курорт в сердце Тянь-Шаня, расположенный в поселке Акташ на высоте 1100 метров над уровнем моря. Курорт занимает 2 гектара в экологически чистой зоне, окруженной широколиственными лесами и горными реками.',
        'features_comfort': 'Комфортные номера',
        'features_nature': 'Первозданная природа',
        'features_service': 'Премиум сервис',
        'features_health': 'Активный отдых',
        'booking_title': 'Забронировать номер',
        'booking_name': 'Ваше имя',
        'booking_phone': 'Номер телефона',
        'booking_date_in': 'Дата заезда',
        'booking_date_out': 'Дата выезда',
        'booking_room_type': 'Тип номера',
        'booking_guests': 'Количество гостей',
        'booking_comment': 'Дополнительный комментарий',
        'booking_submit': 'Отправить',
        'contact_title': 'Свяжитесь с нами',
        'contact_phone': 'Телефон',
        'contact_address': 'Адрес',
        'rooms_title': 'Номера и цены',
        'services_title': 'Наши услуги',
        'gallery_title': 'Фотогалерея',
        'booking_success': 'Ваша заявка успешно отправлена!',
        'booking_error': 'Произошла ошибка. Пожалуйста, попробуйте снова.',
        'with_meals': 'С полным пансионом',
        'without_meals': 'Без питания',
        'weekdays': 'Будние дни',
        'weekends': 'Выходные дни',
        'included_services': 'Включено в стоимость',
        'additional_services': 'Дополнительные услуги',
        'breakfast': 'Завтрак',
        'lunch': 'Обед',
        'dinner': 'Ужин',
        'pool': 'Бассейн (4 вида)',
        'tennis': 'Настольный теннис',
        'playground': 'Детская площадка',
        'parking': 'Парковка',
        'wifi': 'Wi-Fi',
        'billiard': 'Бильярд',
        'salt_room': 'Соляная комната',
        'spa': 'Spa-процедуры',
        'massage': 'Массаж',
        'sauna': 'Финская сауна',
        'restaurant': 'Ресторан',
        'gazebo_small': 'Малая беседка (7 человек)',
        'gazebo_large': 'Большая беседка (14 человек)',
        'extra_mattress': 'Дополнительный матрас',
        'checkin': 'Время заезда',
        'checkout': 'Время выезда',
        'family_only': 'Только семейный отдых!',
        'reserve_now': 'Забронировать сейчас',
        'our_location': 'Наш адрес',
        'working_hours': 'Время работы',
        'healing_air': 'Чистейший горный воздух',
        'healing_text': 'Естественная гидроионизация от горных рек Oqtosh',
        'distance_capital': '80 км от Ташкента',
        'eco_zone': 'Экологически чистая зона',
        'year_round': 'Круглогодичный отдых',
        'special_offers': 'Специальные предложения',
        'honeymoon_package': 'Медовый месяц',
        'family_package': 'Семейный пакет',
        'gps_coordinates': 'GPS координаты'
    }
}

# Данные о номерах
rooms_data = {
    'standard_2': {
        'uz': 'Standart - 2 kishi',
        'ru': 'Стандарт - 2 человека',
        'weekday_no_meal': 1100000,
        'weekend_no_meal': 1300000,
        'with_meal': 1800000,
        'capacity': 2
    },
    'lux_2': {
        'uz': 'Lyuks - 2 kishi',
        'ru': 'Люкс - 2 человека',
        'weekday_no_meal': 1500000,
        'weekend_no_meal': 1800000,
        'with_meal': 2200000,
        'capacity': 2
    },
    'standard_4': {
        'uz': 'Standart - 4 kishi',
        'ru': 'Стандарт - 4 человека',
        'weekday_no_meal': 1900000,
        'weekend_no_meal': 2200000,
        'with_meal': 2900000,
        'capacity': 4
    },
    'vip_small_4': {
        'uz': 'VIP (kichik) - 4 kishi',
        'ru': 'VIP (малый) - 4 человека',
        'weekday_no_meal': 2000000,
        'weekend_no_meal': 2350000,
        'with_meal': 3400000,
        'capacity': 4
    },
    'vip_large_4': {
        'uz': 'VIP (katta) - 4 kishi',
        'ru': 'VIP (большой) - 4 человека',
        'weekday_no_meal': 2200000,
        'weekend_no_meal': 2500000,
        'with_meal': 3600000,
        'capacity': 4
    },
    'apartment_4': {
        'uz': 'Apartament - 4 kishi',
        'ru': 'Апартамент - 4 человека',
        'weekday_no_meal': 2500000,
        'weekend_no_meal': 3000000,
        'with_meal': 3800000,
        'capacity': 4
    },
    'cottage_6': {
        'uz': 'Kottedj - 6 kishi',
        'ru': 'Коттедж - 6 человек',
        'weekday_no_meal': 5200000,
        'weekend_no_meal': 5500000,
        'with_meal': 6500000,
        'capacity': 6
    },
    'apartment_8': {
        'uz': 'Apartament - 8 kishi',
        'ru': 'Апартамент - 8 человек',
        'weekday_no_meal': 5500000,
        'weekend_no_meal': 6000000,
        'with_meal': 7500000,
        'capacity': 8
    }
}


def get_locale():
    """Получить текущий язык из сессии"""
    return session.get('lang', 'uz')


def set_locale(lang):
    """Установить язык в сессию"""
    session['lang'] = lang


@app.context_processor
def inject_locale():
    """Внедрить переменные языка во все шаблоны"""
    return {
        'lang': get_locale(),
        't': translations.get(get_locale(), translations['uz'])
    }


@app.route('/set_language/<lang>')
def set_language(lang):
    """Переключить язык"""
    if lang in ['uz', 'ru']:
        set_locale(lang)
    return redirect(request.referrer or url_for('index'))


@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html')


@app.route('/rooms')
def rooms():
    """Страница номеров и цен"""
    return render_template('rooms.html', rooms=rooms_data)


@app.route('/services')
def services():
    """Страница услуг"""
    return render_template('services.html')


@app.route('/gallery')
def gallery():
    """Страница галереи"""
    return render_template('gallery.html')


@app.route('/booking')
def booking():
    """Страница бронирования"""
    return render_template('booking.html', rooms=rooms_data)


@app.route('/contacts')
def contacts():
    """Страница контактов"""
    return render_template('contacts.html')


@app.route('/submit-booking', methods=['POST'])
def submit_booking():
    """Обработка формы бронирования"""
    try:
        data = request.json
        lang = get_locale()

        # Формируем сообщение для Telegram
        room_type = rooms_data.get(data['room_type'], {})
        room_name = room_type.get(lang, data['room_type'])

        message = f"""
🏨 Новое бронирование | Yangi bron

👤 Имя | Ism: {data['name']}
📞 Телефон | Telefon: {data['phone']}
📅 Заезд | Kirish: {data['check_in']}
📅 Выезд | Chiqish: {data['check_out']}
🏠 Номер | Xona: {room_name}
👥 Гостей | Mehmonlar: {data['guests']}
💬 Комментарий | Izoh: {data.get('comment', "Нет | Yo'q")}
"""

        # Отправляем в Telegram
        if app.config['TELEGRAM_BOT_TOKEN'] and app.config['TELEGRAM_CHAT_ID']:
            telegram_url = f"https://api.telegram.org/bot{app.config['TELEGRAM_BOT_TOKEN']}/sendMessage"
            telegram_data = {
                'chat_id': app.config['TELEGRAM_CHAT_ID'],
                'text': message,
                'parse_mode': 'HTML'
            }

            response = requests.post(telegram_url, json=telegram_data)

            if response.status_code == 200:
                return jsonify({
                    'success': True,
                    'message': translations[lang]['booking_success']
                })
            else:
                return jsonify({
                    'success': False,
                    'message': translations[lang]['booking_error']
                }), 500
        else:
            # Если Telegram не настроен, все равно возвращаем успех
            print("Telegram не настроен. Данные бронирования:")
            print(message)
            return jsonify({
                'success': True,
                'message': translations[lang]['booking_success']
            })

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({
            'success': False,
            'message': translations[get_locale()]['booking_error']
        }), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)