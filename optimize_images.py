from PIL import Image
import os
from pathlib import Path


def optimize_images(directory, quality=85, max_width=1920):
    """
    Оптимизирует все изображения в указанной директории

    Args:
        directory: путь к папке с изображениями
        quality: качество сжатия (1-100)
        max_width: максимальная ширина изображения
    """

    # Создаем папку для оптимизированных изображений
    optimized_dir = Path(directory).parent / f"{Path(directory).name}_optimized"
    optimized_dir.mkdir(exist_ok=True)

    # Поддерживаемые форматы
    supported_formats = ('.jpg', '.jpeg', '.png', '.webp')

    # Счетчики
    total_size_before = 0
    total_size_after = 0
    processed_count = 0

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(supported_formats):
                file_path = Path(root) / file

                # Создаем соответствующую структуру папок
                relative_path = file_path.relative_to(directory)
                output_path = optimized_dir / relative_path
                output_path.parent.mkdir(parents=True, exist_ok=True)

                try:
                    # Размер до оптимизации
                    size_before = file_path.stat().st_size
                    total_size_before += size_before

                    # Открываем изображение
                    with Image.open(file_path) as img:
                        # Конвертируем в RGB если необходимо
                        if img.mode in ('RGBA', 'LA', 'P'):
                            rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                            rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                            img = rgb_img

                        # Изменяем размер если слишком большое
                        if img.width > max_width:
                            ratio = max_width / img.width
                            new_height = int(img.height * ratio)
                            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)

                        # Сохраняем с оптимизацией
                        img.save(output_path, 'JPEG', quality=quality, optimize=True)

                    # Размер после оптимизации
                    size_after = output_path.stat().st_size
                    total_size_after += size_after

                    processed_count += 1
                    reduction = ((size_before - size_after) / size_before) * 100

                    print(f"✓ {file}: {size_before / 1024:.1f}KB → {size_after / 1024:.1f}KB (-{reduction:.1f}%)")

                except Exception as e:
                    print(f"✗ Ошибка при обработке {file}: {e}")

    # Итоговая статистика
    if processed_count > 0:
        total_reduction = ((total_size_before - total_size_after) / total_size_before) * 100
        print(f"\n📊 Статистика оптимизации:")
        print(f"Обработано файлов: {processed_count}")
        print(f"Общий размер до: {total_size_before / 1024 / 1024:.1f} MB")
        print(f"Общий размер после: {total_size_after / 1024 / 1024:.1f} MB")
        print(f"Сэкономлено: {(total_size_before - total_size_after) / 1024 / 1024:.1f} MB (-{total_reduction:.1f}%)")
        print(f"\nОптимизированные изображения сохранены в: {optimized_dir}")

        # После оптимизации можно заменить оригинальные файлы
        print("\n⚠️  Чтобы заменить оригинальные файлы оптимизированными:")
        print(f"1. Сделайте резервную копию папки {directory}")
        print(f"2. Удалите содержимое {directory}")
        print(f"3. Скопируйте файлы из {optimized_dir} в {directory}")
    else:
        print("Не найдено изображений для оптимизации")


# Использование скрипта
if __name__ == "__main__":
    # Укажите путь к папке с изображениями
    images_directory = "static/images"

    # Запускаем оптимизацию
    optimize_images(
        directory=images_directory,
        quality=85,  # Качество от 1 до 100
        max_width=1920  # Максимальная ширина
    )

    # Для более агрессивной оптимизации галереи
    gallery_directory = "static/images/gallery"
    optimize_images(
        directory=gallery_directory,
        quality=75,  # Меньшее качество для галереи
        max_width=1200  # Меньший размер для превью
    )