import os
from pathlib import Path
import shutil


def rename_to_lowercase(directory):
    """
    Переименовывает все файлы изображений в нижний регистр
    """
    # Поддерживаемые форматы
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.JPG', '.JPEG', '.PNG', '.GIF', '.WEBP'}

    renamed_count = 0
    errors = []

    # Обходим все файлы
    for root, dirs, files in os.walk(directory):
        for filename in files:
            # Проверяем расширение
            if any(filename.endswith(ext) for ext in image_extensions):
                old_path = Path(root) / filename
                new_filename = filename.lower()
                new_path = Path(root) / new_filename

                # Если имя отличается
                if filename != new_filename:
                    try:
                        # В Windows нужно использовать временное имя
                        temp_path = Path(root) / f"temp_{new_filename}"

                        # Переименовываем через временное имя
                        old_path.rename(temp_path)
                        temp_path.rename(new_path)

                        print(f"✓ {filename} → {new_filename}")
                        renamed_count += 1

                    except Exception as e:
                        errors.append(f"✗ Ошибка с {filename}: {str(e)}")

    # Вывод статистики
    print(f"\n📊 Статистика переименования:")
    print(f"Переименовано файлов: {renamed_count}")

    if errors:
        print(f"\n❌ Ошибки ({len(errors)}):")
        for error in errors:
            print(error)

    return renamed_count


def update_html_templates():
    """
    Обновляет ссылки в HTML шаблонах на нижний регистр
    """
    templates_dir = Path("templates")

    # Файлы для проверки
    template_files = ['gallery.html', 'index.html']

    for template_file in template_files:
        template_path = templates_dir / template_file

        if template_path.exists():
            print(f"\n📝 Проверка {template_file}...")

            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Замены для разных форматов
            replacements = [
                ('.JPG', '.jpg'),
                ('.JPEG', '.jpeg'),
                ('.PNG', '.png'),
                ('.GIF', '.gif'),
                ('.WEBP', '.webp')
            ]

            modified = False
            for old_ext, new_ext in replacements:
                if old_ext in content:
                    content = content.replace(old_ext, new_ext)
                    modified = True
                    print(f"  Заменено: {old_ext} → {new_ext}")

            if modified:
                # Сохраняем изменения
                with open(template_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"  ✓ {template_file} обновлен")
            else:
                print(f"  ℹ {template_file} не требует изменений")


if __name__ == "__main__":
    print("=== Переименование изображений в нижний регистр ===\n")

    # Переименовываем файлы в галерее
    gallery_path = "static/images/gallery"
    if os.path.exists(gallery_path):
        print(f"📁 Обработка папки: {gallery_path}")
        rename_to_lowercase(gallery_path)

    # Переименовываем все изображения
    images_path = "static/images"
    if os.path.exists(images_path):
        print(f"\n📁 Обработка папки: {images_path}")
        rename_to_lowercase(images_path)

    # Обновляем HTML шаблоны
    print("\n=== Обновление HTML шаблонов ===")
    update_html_templates()

    print("\n✅ Готово! Все файлы переименованы в нижний регистр.")