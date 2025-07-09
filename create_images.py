import os
from PIL import Image, ImageDraw, ImageFont

# Создаем папки если их нет
os.makedirs('static/images/gallery', exist_ok=True)


# Функция для создания изображения-заглушки
def create_placeholder(filename, text, size=(800, 600), color=(100, 100, 100)):
    # Создаем новое изображение
    img = Image.new('RGB', size, color)
    draw = ImageDraw.Draw(img)

    # Пытаемся использовать системный шрифт
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        font = ImageFont.load_default()

    # Получаем размер текста
    text_width = draw.textlength(text, font=font)
    text_height = 40  # примерная высота

    # Вычисляем позицию для центрирования текста
    x = (size[0] - text_width) // 2
    y = (size[1] - text_height) // 2

    # Рисуем текст
    draw.text((x, y), text, fill=(255, 255, 255), font=font)

    # Сохраняем изображение
    img.save(filename)
    print(f"Создан: {filename}")


# Создаем изображения-заглушки
images = [
    ('static/images/logo.png', 'LOGO', (200, 100), (0, 0, 0)),
    ('static/images/hero-bg.jpg', 'OQTOSHSOY RESORT', (1920, 1080), (50, 50, 50)),
    ('static/images/gallery/room1.jpg', 'Room 1', (800, 600), (80, 80, 120)),
    ('static/images/gallery/room2.jpg', 'Room 2', (800, 600), (80, 120, 80)),
    ('static/images/gallery/room3.jpg', 'Room 3', (800, 600), (120, 80, 80)),
    ('static/images/gallery/pool.jpg', 'Pool', (800, 600), (80, 120, 150)),
    ('static/images/gallery/nature1.jpg', 'Nature 1', (800, 600), (100, 140, 100)),
    ('static/images/gallery/nature2.jpg', 'Nature 2', (800, 600), (100, 120, 80)),
    ('static/images/gallery/restaurant.jpg', 'Restaurant', (800, 600), (150, 100, 80)),
    ('static/images/gallery/exterior.jpg', 'Exterior', (800, 600), (120, 120, 120)),
    ('static/images/gallery/playground.jpg', 'Playground', (800, 600), (150, 120, 100)),
    ('static/images/gallery/billiard.jpg', 'Billiard', (800, 600), (100, 100, 150)),
    ('static/images/gallery/terrace.jpg', 'Terrace', (800, 600), (130, 110, 100)),
    ('static/images/gallery/view.jpg', 'Mountain View', (800, 600), (100, 130, 150)),
    ('static/images/gallery/nature.jpg', 'Nature', (800, 600), (90, 140, 90)),
]

for filename, text, size, color in images:
    create_placeholder(filename, text, size, color)

print("\nВсе изображения-заглушки созданы!")
print("Позже замените их на реальные фотографии вашего курорта.")