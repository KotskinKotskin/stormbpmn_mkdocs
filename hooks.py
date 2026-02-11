"""
MkDocs hooks для загрузки навигации из локализованных toc.yaml файлов
"""
import os
import yaml
from pathlib import Path

def on_config(config, **kwargs):
    """
    Загрузка навигации из toc.yaml файлов для каждой локали
    """
    docs_dir = Path(config['docs_dir'])
    
    # Проверяем, используется ли плагин i18n
    plugins = config.get('plugins', {})
    i18n_plugin = None
    
    for plugin in plugins:
        if isinstance(plugin, dict) and 'i18n' in plugin:
            i18n_plugin = plugin['i18n']
            break
    
    if i18n_plugin:
        # Если используется i18n, навигация обрабатывается плагином
        # Загружаем навигацию из ru/toc.yaml как базовую
        default_lang = 'ru'
        toc_file = docs_dir / default_lang / 'toc.yaml'
        
        if toc_file.exists():
            with open(toc_file, 'r', encoding='utf-8') as f:
                nav_config = yaml.safe_load(f)
                if nav_config:
                    config['nav'] = nav_config
                    print(f"✓ Загружена базовая навигация из {toc_file}")
        else:
            print(f"⚠ Файл {toc_file} не найден")
    else:
        # Если i18n не используется, загружаем навигацию для одного языка
        language = config.get('theme', {}).get('language', 'ru')
        toc_file = docs_dir / language / 'toc.yaml'
        
        if toc_file.exists():
            with open(toc_file, 'r', encoding='utf-8') as f:
                nav_config = yaml.safe_load(f)
                if nav_config:
                    config['nav'] = update_nav_paths(nav_config, language)
                    print(f"✓ Загружена навигация из {toc_file}")
        else:
            print(f"⚠ Файл {toc_file} не найден")
    
    return config

def update_nav_paths(nav_items, language):
    """
    Обновляет пути в навигации, добавляя префикс языка
    """
    if isinstance(nav_items, list):
        return [update_nav_paths(item, language) for item in nav_items]
    elif isinstance(nav_items, dict):
        updated = {}
        for key, value in nav_items.items():
            if isinstance(value, str) and value.endswith('.md'):
                # Добавляем префикс языка к путям файлов
                updated[key] = f"{language}/{value}"
            elif isinstance(value, list):
                updated[key] = update_nav_paths(value, language)
            else:
                updated[key] = value
        return updated
    else:
        return nav_items
