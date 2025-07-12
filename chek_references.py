import os
import re
from pathlib import Path


def check_image_references():
    """
    Проверяет все ссылки на изображения в проекте
    """
    # Расширения для поиска
    code_extensions = ['.html', '.css', '.js', '.py']
    image_patterns = [
        r'\.JPG', r'\.JPEG', r'\.PNG', r'\.GIF', r'\.WEBP',
        r'\.Jpg', r'\.Jpeg', r'\.Png', r'\.Gif', r'\.Webp'
    ]

    issues_found = []

    # Проверяем все файлы
    for root, dirs, files in os.walk('.'):
        # Пропускаем системные папки
        if any(skip in root for skip in ['.git', 'node_modules', '.venv', '__pycache__']):
            continue

        for file in files:
            if any(file.endswith(ext) for ext in code_extensions):
                file_path = Path(root) / file

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Проверяем каждый паттерн
                    for pattern in image_patterns:
                        matches = re.findall(pattern, content)
                        if matches:
                            issues_found.append({
                                'file': str(file_path),
                                'pattern': pattern,
                                'count': len(matches)
                            })

                except Exception as e:
                    print(f"Ошибка при чтении {file_path}: {e}")

    # Выводим результаты
    if issues_found:
        print("⚠️  Найдены ссылки с неправильным регистром:\n")
        for issue in issues_found:
            print(f"📄 {issue['file']}")
            print(f"   Найдено: {issue['count']} вхождений {issue['pattern']}")
            print()
    else:
        print("✅ Все ссылки на изображения в нижнем регистре!")


if __name__ == "__main__":
    check_image_references()