"""
Модуль для загрузки переменных и макросов для mkdocs-macros плагина
"""
import yaml
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape


def define_env(env):
    """
    Функция для определения переменных и макросов для mkdocs-macros плагина.
    
    Args:
        env: Объект окружения от mkdocs-macros плагина
    """
    # Получаем путь к директории с документацией
    docs_dir = Path(env.conf['docs_dir'])
    
    # Добавляем общие переменные
    env.variables['product'] = 'StormBPMN'
    
    # Загружаем глобальные переменные
    global_vars_path = docs_dir / 'global_vars.yaml'
    if global_vars_path.exists():
        with open(global_vars_path, 'r', encoding='utf-8') as f:
            global_vars = yaml.safe_load(f) or {}
            # Добавляем глобальные переменные в окружение
            for key, value in global_vars.items():
                env.variables[key] = value


def notify_printer(env, template_path, **context):
    """
    Рендерит Jinja2 шаблон с переданными переменными.
    
    Args:
        env: Объект окружения от mkdocs-macros плагина
        template_path: Относительный путь к шаблону от корня docs_dir
        **context: Переменные для передачи в шаблон
    
    Returns:
        str: Отрендеренный markdown контент
    """
    # Получаем путь к директории с документацией
    docs_dir = Path(env.conf['docs_dir'])
    
    # Создаем Jinja2 окружение с загрузчиком из директории документации
    jinja_env = Environment(
        loader=FileSystemLoader(str(docs_dir)),
        autoescape=select_autoescape(['html', 'xml'])
    )
    
    # Добавляем все переменные из окружения mkdocs-macros в контекст
    template_context = dict(env.variables)
    template_context.update(context)
    
    # Загружаем и рендерим шаблон
    template = jinja_env.get_template(template_path)
    return template.render(**template_context)

def on_pre_page_macros(env):
    """
    Хук, который вызывается перед обработкой макросов на каждой странице.
    Автоматически добавляет макросы constraints в начало контента страницы.
    
    Args:
        env: Объект окружения от mkdocs-macros плагина
    """
    # Проверяем наличие метаданных у страницы
    if not hasattr(env, 'page') or not hasattr(env.page, 'meta'):
        return
    
    # Собираем все сгенерированные предупреждения
    notifications = []
    
    # Создаем контекст для шаблонов с метаданными страницы
    page_meta = env.page.meta
    
    # Проверяем каждый тип ограничений
    if 'role' in page_meta:
        template_path = 'ru/_templates/system/constraints_roles.template'
        rendered = notify_printer(
            env,
            template_path,
            page={'meta': page_meta},
            meta=page_meta
        )
        notifications.append(rendered)
    
    if 'plan' in page_meta:
        template_path = 'ru/_templates/system/constraints_plan.template'
        rendered = notify_printer(
            env,
            template_path,
            page={'meta': page_meta},
            meta=page_meta
        )
        notifications.append(rendered)
    
    if 'permissions' in page_meta:
        template_path = 'ru/_templates/system/constraints_permissions.template'
        rendered = notify_printer(
            env,
            template_path,
            page={'meta': page_meta},
            meta=page_meta
        )
        notifications.append(rendered)
    
    # Если есть сгенерированные уведомления, добавляем их в начало контента
    if notifications:
        # Оборачиваем уведомления в контейнер, если их больше одного
        if len(notifications) > 1:
            prefix_content = admonition_container_wrap(notifications)
        else:
            prefix_content = notifications[0] + '\n\n'
        # Добавляем в начало markdown контента страницы
        env.markdown = prefix_content + env.markdown


def admonition_container_wrap(notifications):
    """
    Оборачивает уведомления в HTML-контейнер для горизонтального размещения.
    
    Args:
        notifications: Список отрендеренных уведомлений (markdown строк)
    
    Returns:
        str: HTML-контейнер с уведомлениями и markdown контентом
    """
    # Используем markdown="block" для обработки markdown внутри HTML (требуется расширение md_in_html)
    # Важно: пустые строки до и после контента обязательны для корректной обработки
    container_content = '\n\n'.join(notifications)
    return f'<div markdown="block" class="admonition-container">\n\n{container_content}\n\n</div>\n\n'