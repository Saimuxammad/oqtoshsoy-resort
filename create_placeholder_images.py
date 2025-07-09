import os
from PIL import Image, ImageDraw, ImageFont
import random

# Создаем папки если их нет
os.makedirs('static/images/gallery', exist_ok=True)


def create_placeholder(filename, text, size=(800, 600)):
    # Случайный приятный цвет фона
    colors = [
        (100, 120, 140),  # Серо-синий
        (120, 100, 130),  # Фиолетово-серый
        (100, 130, 120),  # Зелено-серый
        (130, 110, 100),  # Коричнево-серый
        (110, 110, 120),  # Нейтральный серый
    ]

    color = random.choice(colors)

    # Создаем изображение
    img = Image.new('RGB', size, color)
    draw = ImageDraw.Draw(img)

    # Добавляем текст
    text_color = (255, 255, 255)

    # Пытаемся использовать системный шрифт
    try:
        font_size = int(min(size) / 10)
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()

    # Центрируем текст
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x = (size[0] - text_width) // 2
    y = (size[1] - text_height) // 2

    # Рисуем тень
    shadow_offset = 2
    draw.text((x + shadow_offset, y + shadow_offset), text, fill=(0, 0, 0, 128), font=font)

    # Рисуем основной текст
    draw.text((x, y), text, fill=text_color, font=font)

    # Добавляем декоративную рамку
    border_width = 20
    draw.rectangle(
        [(border_width, border_width),
         (size[0] - border_width, size[1] - border_width)],
        outline=(255, 255, 255, 50),
        width=2
    )

    # Сохраняем
    img.save(filename, quality=95)
    print(f"✓ Создан: {filename}")


# Создаем изображения
images_to_create = [
    # Основные изображения
    ('static/images/logo.jpg', 'OQTOSHSOY\nRESORT', (300, 150)),
    ('static/images/hero-bg.jpg', 'OQTOSHSOY\nMOUNTAIN RESORT', (1920, 1080)),

    # Галерея
    ('static/images/gallery/room1.jpg', 'Standard Room', (800, 600)),
    ('static/images/gallery/room2.jpg', 'Lux Room', (800, 600)),
    ('static/images/gallery/room3.jpg', 'VIP Room', (800, 600)),
    ('static/images/gallery/pool.jpg', 'Swimming Pool', (800, 600)),
    ('static/images/gallery/nature.jpg', 'Mountain View', (800, 600)),
    ('static/images/gallery/nature1.jpg', 'Nature View 1', (800, 600)),
    ('static/images/gallery/nature2.jpg', 'Nature View 2', (800, 600)),
    ('static/images/gallery/restaurant.jpg', 'Restaurant', (800, 600)),
    ('static/images/gallery/exterior.jpg', 'Exterior View', (800, 600)),
    ('static/images/gallery/playground.jpg', 'Kids Playground', (800, 600)),
    ('static/images/gallery/billiard.jpg', 'Billiard Room', (800, 600)),
    ('static/images/gallery/terrace.jpg', 'Terrace View', (800, 600)),
    ('static/images/gallery/view.jpg', 'Panoramic View', (800, 600)),
]

# Создаем все изображения
for filename, text, size in images_to_create:
    create_placeholder(filename, text, size)

print("\n✅ Все изображения-заглушки созданы!")
print("📌 Позже замените их на реальные фотографии вашего курорта.")