from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
import requests
from datetime import datetime
import json

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', 'YOUR_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', 'YOUR_CHAT_ID')

# Переводы для мультиязычности
translations = {
    'uz': {
        'nav_home': 'Bosh sahifa',
        'nav_rooms': 'Xonalar va narxlar',
        'nav_services': 'Xizmatlar',
        'nav_gallery': 'Galereya',
        'nav_booking': 'Bron qilish',
        'nav_contacts': 'Aloqa',
        'hero_title': 'Oqtoshsoy - Premium tog\' kurorti',
        'hero_subtitle': 'Tabiat qo\'ynida hashamatli dam olish',
        'hero_cta': 'Hoziroq bron qiling',
        'about_title': 'Oqtoshsoy haqida',
        'about_text': 'Oqtoshsoy - bu O\'zbekistonning go\'zal tog\'lari orasida joylashgan zamonaviy dam olish maskani. Bizda oilaviy dam olish uchun barcha sharoitlar yaratilgan.',
        'features_comfort': 'Qulay xonalar',
        'features_nature': 'Go\'zal tabiat',
        'features_service': 'Yuqori darajadagi xizmat',
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
        'with_meals': 'Ovqat bilan',
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
        'parking': 'Parking',
        'wifi': 'Wi-Fi',
        'billiard': 'Bilyard',
        'salt_room': 'Tuzli xona',
        'gazebo_small': 'Kichik taptchan (7 kishi)',
        'gazebo_large': 'Katta taptchan (14 kishi)',
        'extra_mattress': 'Qo\'shimcha matras',
        'checkin': 'Kirish vaqti',
        'checkout': 'Chiqish vaqti',
        'family_only': 'Faqat oilaviy dam olish!',
        'reserve_now': 'Hoziroq bron qiling'
    },
    'ru': {
        'nav_home': 'Главная',
        'nav_rooms': 'Номера и цены',
        'nav_services': 'Услуги',
        'nav_gallery': 'Галерея',
        'nav_booking': 'Бронирование',
        'nav_contacts': 'Контакты',
        'hero_title': 'Oqtoshsoy - Премиальный горный курорт',
        'hero_subtitle': 'Роскошный отдых на лоне природы',
        'hero_cta': 'Забронировать сейчас',
        'about_title': 'О курорте Oqtoshsoy',
        'about_text': 'Oqtoshsoy - это современная зона отдыха, расположенная среди живописных гор Узбекистана. У нас созданы все условия для семейного отдыха.',
        'features_comfort': 'Комфортные номера',
        'features_nature': 'Красивая природа',
        'features_service': 'Высокий уровень сервиса',
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
        'with_meals': 'С питанием',
        'without_meals': 'Без питания',
        'weekdays': 'Будние дни',
        'weekends': 'Выходные дни',
        'included_services': 'Включено в стоимость',
        'additional_services': 'Дополнительные услуги',
        'breakfast': 'Завтрак',
        'lunch': 'Обед',
        'dinner': 'Ужин',
        'pool': 'Бассейн (3 вида)',
        'tennis': 'Настольный теннис',
        'playground': 'Детская площадка',
        'parking': 'Парковка',
        'wifi': 'Wi-Fi',
        'billiard': 'Бильярд',
        'salt_room': 'Соляная комната',
        'gazebo_small': 'Малая беседка (7 человек)',
        'gazebo_large': 'Большая беседка (14 человек)',
        'extra_mattress': 'Дополнительный матрас',
        'checkin': 'Время заезда',
        'checkout': 'Время выезда',
        'family_only': 'Только семейный отдых!',
        'reserve_now': 'Забронировать сейчас'
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
    return session.get('lang', 'ru')


def set_locale(lang):
    session['lang'] = lang


@app.context_processor
def inject_locale():
    return {
        'lang': get_locale(),
        't': translations.get(get_locale(), translations['ru'])
    }


@app.route('/set_language/<lang>')
def set_language(lang):
    if lang in ['uz', 'ru']:
        set_locale(lang)
    return redirect(request.referrer or url_for('index'))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/rooms')
def rooms():
    return render_template('rooms.html', rooms=rooms_data)


@app.route('/services')
def services():
    return render_template('services.html')


@app.route('/gallery')
def gallery():
    return render_template('gallery.html')


@app.route('/booking')
def booking():
    return render_template('booking.html', rooms=rooms_data)


@app.route('/contacts')
def contacts():
    return render_template('contacts.html')


@app.route('/submit-booking', methods=['POST'])
def submit_booking():
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
💬 Комментарий | Izoh: {data.get('comment', 'Нет | Yo\'q')}
"""

        # Отправляем в Telegram
        telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        telegram_data = {
            'chat_id': TELEGRAM_CHAT_ID,
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

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({
            'success': False,
            'message': translations[get_locale()]['booking_error']
        }), 500


if __name__ == '__main__':
    app.run(debug=True)