import os
from dotenv import load_dotenv

# Загружаем .env файл из корневой директории
load_dotenv(dotenv_path='../.env')

import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import requests
import json

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Configuration
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_ADMIN_CHAT_ID = os.environ.get('TELEGRAM_ADMIN_CHAT_ID')
WEBAPP_URL = os.environ.get('WEBAPP_URL', 'http://localhost:5000')

print(f"TOKEN from env: {TELEGRAM_BOT_TOKEN}")
print(f"CHAT_ID from env: {TELEGRAM_ADMIN_CHAT_ID}")
print(f"WEBAPP_URL: {WEBAPP_URL}")


class OqtoshsoyBot:
    def __init__(self):
        self.application = None

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        try:
            user = update.effective_user

            welcome_text = f"""
🏔️ <b>Добро пожаловать в Горный Курорт Oqtoshsoy, {user.first_name}!</b>

Незабываемый отдых в сердце гор Ташкентской области.

🌟 <b>Что у нас есть:</b>
• Комфортные номера с видом на горы
• Чистый горный воздух
• Современные удобства
• Дружелюбный персонал
• Доступные цены

Выберите действие:
            """

            keyboard = [
                [
                    InlineKeyboardButton("🏠 Номера и цены", callback_data="rooms"),
                    InlineKeyboardButton("📅 Забронировать", callback_data="booking")
                ],
                [
                    InlineKeyboardButton("📞 Контакты", callback_data="contact"),
                    InlineKeyboardButton("ℹ️ О курорте", callback_data="info")
                ]
            ]

            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                welcome_text,
                parse_mode='HTML',
                reply_markup=reply_markup
            )
        except Exception as e:
            logger.error(f"Error in start_command: {e}")
            await update.message.reply_text("Произошла ошибка. Попробуйте позже.")

    async def rooms_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send rooms information"""
        message = """
🏠 <b>Наши номера:</b>

<b>🌟 Стандартный номер</b>
👥 2 человека
💰 Будни: 200,000 - 250,000 сум
💰 Выходные: 250,000 - 300,000 сум

<b>🌟 Семейный номер</b>
👥 4 человека
💰 Будни: 350,000 - 400,000 сум
💰 Выходные: 400,000 - 450,000 сум

<b>🌟 Люкс номер</b>
👥 2-3 человека
💰 Будни: 450,000 - 500,000 сум
💰 Выходные: 500,000 - 550,000 сум

<i>Цены указаны за сутки (без питания - с питанием)</i>

✨ <b>Все номера включают:</b>
• Кондиционер/отопление
• Горячая вода 24/7
• Wi-Fi
• Телевизор
• Холодильник
• Чистое постельное белье
        """

        keyboard = [
            [InlineKeyboardButton("📅 Забронировать", callback_data="booking")],
            [InlineKeyboardButton("🔙 Назад в меню", callback_data="main_menu")]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        if update.callback_query:
            await update.callback_query.edit_message_text(
                message,
                parse_mode='HTML',
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(
                message,
                parse_mode='HTML',
                reply_markup=reply_markup
            )

    async def booking_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle booking information"""
        message = """
📅 <b>Бронирование номера</b>

🎯 <b>Способы бронирования:</b>

<b>1️⃣ Через наш сайт</b>
• Полный каталог номеров
• Онлайн-форма бронирования
• Моментальное подтверждение

<b>2️⃣ Через Telegram</b>
• Напишите нам прямо здесь
• Быстрая обработка заявки
• Персональная консультация

<b>3️⃣ По телефону</b>
• Прямая связь с администратором
• Ответы на все вопросы

💬 <b>Для быстрого бронирования напишите:</b>
"Хочу забронировать [тип номера] с [дата] по [дата] на [количество] человек"

📋 <b>Пример:</b>
"Хочу забронировать семейный номер с 20 июня по 22 июня на 4 человека"
        """

        keyboard = [
            [
                InlineKeyboardButton("🏠 Номера и цены", callback_data="rooms"),
                InlineKeyboardButton("📞 Контакты", callback_data="contact")
            ],
            [
                InlineKeyboardButton("🔙 Назад в меню", callback_data="main_menu")
            ]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.callback_query.edit_message_text(
            message,
            parse_mode='HTML',
            reply_markup=reply_markup
        )

    async def contact_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send contact information"""
        message = """
📞 <b>Контактная информация</b>

🏔️ <b>Горный Курорт Oqtoshsoy</b>
📍 Ташкентская область, горная курортная зона

📞 <b>Телефон:</b> +998 XX XXX XX XX
📧 <b>Email:</b> info@oqtoshsoy-resort.uz
💬 <b>Telegram:</b> Этот бот

🕐 <b>Время работы:</b>
• Администрация: 24/7
• Ответ в Telegram: 8:00 - 22:00
• Среднее время ответа: 5-10 минут

🌐 <b>Наш сайт:</b> {webapp_url}

💬 <b>Напишите нам:</b>
Мы отвечаем быстро и помогаем с любыми вопросами!
        """.format(webapp_url=WEBAPP_URL)

        keyboard = [
            [InlineKeyboardButton("📞 Позвонить", url="tel:+998901234567")],
            [InlineKeyboardButton("🔙 Назад в меню", callback_data="main_menu")]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.callback_query.edit_message_text(
            message,
            parse_mode='HTML',
            reply_markup=reply_markup
        )

    async def resort_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send resort information"""
        message = """
🏔️ <b>О Горном Курорте Oqtoshsoy</b>

🌿 <b>Расположение:</b>
Наш курорт находится в живописной горной местности Ташкентской области, где чистый горный воздух и потрясающие пейзажи создают идеальную атмосферу для отдыха.

🏨 <b>Размещение:</b>
• Номера различных категорий
• От стандартных до люкс номеров
• Все номера с современными удобствами
• Прекрасные виды на горы

🎯 <b>Что мы предлагаем:</b>
🌬️ Чистый горный воздух
🏔️ Живописные пейзажи
🏡 Уютная атмосфера
👨‍👩‍👧‍👦 Семейный отдых
🚗 Удобная парковка
🍽️ Возможность заказа питания

👨‍👩‍👧‍👦 <b>Семейный отдых:</b>
Мы создали все условия для комфортного отдыха всей семьей!

💎 <b>Почему выбирают нас:</b>
✅ Горный чистый воздух
✅ Безопасная территория
✅ Дружелюбный персонал
✅ Разумные цены
✅ Индивидуальный подход
✅ Красивые виды
        """

        keyboard = [
            [InlineKeyboardButton("📅 Забронировать", callback_data="booking")],
            [InlineKeyboardButton("🔙 Назад в меню", callback_data="main_menu")]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.callback_query.edit_message_text(
            message,
            parse_mode='HTML',
            reply_markup=reply_markup
        )

    async def contact_admin(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle contact admin request"""
        message = """
👨‍💼 <b>Связь с администратором</b>

💬 <b>Прямая связь через Telegram:</b>
Просто напишите сообщение в этом чате, и администратор ответит вам в течение нескольких минут.

📞 <b>Телефон:</b> +998 XX XXX XX XX

⏰ <b>Время ответа:</b>
• Рабочее время: 5-10 минут
• Вечернее время: до 30 минут
• Ночные часы: до 1 часа

📝 <b>Для быстрой обработки укажите:</b>
• Желаемые даты заезда и выезда
• Количество гостей
• Тип номера (если знаете)
• Ваши контактные данные
• Особые пожелания

<i>Пример: "Здравствуйте! Хочу забронировать номер на 2 человек с 15 по 17 марта. Нужен стандартный номер. Телефон: +998901234567"</i>
        """

        keyboard = [
            [InlineKeyboardButton("📞 Позвонить", url="tel:+998XXXXXXXXX")],
            [InlineKeyboardButton("🔙 Назад в меню", callback_data="main_menu")]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.callback_query.edit_message_text(
            message,
            parse_mode='HTML',
            reply_markup=reply_markup
        )

    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback queries from inline keyboards"""
        query = update.callback_query
        await query.answer()

        try:
            if query.data == "main_menu":
                await self.show_main_menu(query)
            elif query.data == "rooms":
                await self.rooms_info(update, context)
            elif query.data == "booking":
                await self.booking_info(update, context)
            elif query.data == "contact":
                await self.contact_info(update, context)
            elif query.data == "info":
                await self.resort_info(update, context)
            elif query.data == "contact_admin":
                await self.contact_admin(update, context)
        except Exception as e:
            logger.error(f"Error handling callback query: {e}")
            await query.edit_message_text("Произошла ошибка. Попробуйте позже.")

    async def show_main_menu(self, query):
        """Show main menu"""
        message = """
🏔️ <b>Горный Курорт Oqtoshsoy</b>

Выберите действие:
        """

        keyboard = [
            [
                InlineKeyboardButton("🏠 Номера и цены", callback_data="rooms"),
                InlineKeyboardButton("📅 Забронировать", callback_data="booking")
            ],
            [
                InlineKeyboardButton("📞 Контакты", callback_data="contact"),
                InlineKeyboardButton("ℹ️ О курорте", callback_data="info")
            ]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            message,
            parse_mode='HTML',
            reply_markup=reply_markup
        )

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular text messages"""
        try:
            user_message = update.message.text.lower()
            user_name = update.effective_user.first_name
            user_id = update.effective_user.id

            # Check for booking-related keywords
            booking_keywords = ['бронь', 'забронировать', 'номер', 'заказ', 'резерв', 'бронирование']
            contact_keywords = ['контакт', 'телефон', 'связь', 'админ', 'администратор']
            price_keywords = ['цена', 'стоимость', 'сколько', 'цены']

            if any(keyword in user_message for keyword in booking_keywords):
                await self.handle_booking_inquiry(update, context)
            elif any(keyword in user_message for keyword in contact_keywords):
                await self.handle_contact_inquiry(update, context)
            elif any(keyword in user_message for keyword in price_keywords):
                await self.handle_price_inquiry(update, context)
            else:
                # General support response
                await self.handle_general_inquiry(update, context)

            # Forward message to admin
            await self.forward_to_admin(update, context)

        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await update.message.reply_text("Произошла ошибка. Попробуйте позже.")

    async def handle_booking_inquiry(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle booking-related messages"""
        message = f"""
📝 <b>Бронирование номера</b>

Отлично, {update.effective_user.first_name}! Поможем вам забронировать номер.

🎯 <b>Ваше сообщение передано администратору</b>
Ответ придет в течение 5-10 минут.

💡 <b>Тем временем можете:</b>
• Посмотреть наши номера и цены
• Изучить информацию о курорте
• Посетить наш сайт

📋 <b>Для ускорения обработки добавьте:</b>
• Даты заезда и выезда
• Количество гостей  
• Ваш номер телефона
        """

        keyboard = [
            [InlineKeyboardButton("🏠 Посмотреть номера", callback_data="rooms")],
            [InlineKeyboardButton("🔙 Главное меню", callback_data="main_menu")]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            message,
            parse_mode='HTML',
            reply_markup=reply_markup
        )

    async def handle_contact_inquiry(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle contact-related messages"""
        message = """
📞 <b>Контакты</b>

Администратор скоро ответит!

🏔️ <b>Горный Курорт Oqtoshsoy</b>
📞 Телефон: +998 XX XXX XX XX
💬 Telegram: прямо здесь

⏰ Среднее время ответа: 5-10 минут
        """

        keyboard = [
            [InlineKeyboardButton("📞 Позвонить", url="tel:+998901234567")],
            [InlineKeyboardButton("🔙 Назад в меню", callback_data="main_menu")]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            message,
            parse_mode='HTML',
            reply_markup=reply_markup
        )

    async def handle_price_inquiry(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle price-related messages"""
        await self.rooms_info(update, context)

    async def handle_general_inquiry(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle general messages"""
        user_name = update.effective_user.first_name

        message = f"""
Спасибо за сообщение, {user_name}! 😊

👨‍💼 <b>Ваше сообщение передано администратору</b>

⏰ Среднее время ответа: <b>5-10 минут</b>

💡 <b>Пока ждете, можете:</b>
• Посмотреть номера и цены
• Узнать больше о курорте
• Посетить наш сайт
        """

        keyboard = [
            [
                InlineKeyboardButton("🏠 Номера", callback_data="rooms"),
                InlineKeyboardButton("ℹ️ О курорте", callback_data="info")
            ]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            message,
            parse_mode='HTML',
            reply_markup=reply_markup
        )

    async def forward_to_admin(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Forward user message to admin"""
        if not TELEGRAM_ADMIN_CHAT_ID:
            return

        user = update.effective_user
        message_text = update.message.text

        admin_message = f"""
💬 <b>Новое сообщение от пользователя</b>

👤 <b>От:</b> {user.first_name or 'Неизвестно'} {user.last_name or ''}
🆔 <b>Username:</b> @{user.username or 'нет username'}
🔢 <b>ID:</b> {user.id}
⏰ <b>Время:</b> {datetime.now().strftime('%H:%M %d.%m.%Y')}

💬 <b>Сообщение:</b>
{message_text}

<i>Ответьте на это сообщение для отправки ответа пользователю</i>
        """

        try:
            await context.bot.send_message(
                chat_id=TELEGRAM_ADMIN_CHAT_ID,
                text=admin_message,
                parse_mode='HTML'
            )
        except Exception as e:
            logger.error(f"Error sending message to admin: {e}")

    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors"""
        logger.error(msg="Exception while handling an update:", exc_info=context.error)

        try:
            if update.effective_message:
                await update.effective_message.reply_text(
                    "Извините, произошла ошибка. Попробуйте позже или свяжитесь с администрацией."
                )
        except:
            pass

    def setup_handlers(self):
        """Setup bot handlers"""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))

        # Callback query handler
        self.application.add_handler(CallbackQueryHandler(self.handle_callback_query))

        # Message handler
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

        # Error handler
        self.application.add_error_handler(self.error_handler)

    def run(self):
        """Run the bot"""
        if not TELEGRAM_BOT_TOKEN:
            logger.error("TELEGRAM_BOT_TOKEN not set")
            return

        # Create application
        self.application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

        # Setup handlers
        self.setup_handlers()

        # Run the bot
        logger.info("Starting Oqtoshsoy Resort Bot...")
        self.application.run_polling(drop_pending_updates=True)


def main():
    """Main function"""
    bot = OqtoshsoyBot()
    bot.run()


if __name__ == '__main__':
    main()