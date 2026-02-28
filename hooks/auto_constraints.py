from pathlib import Path
from bs4 import BeautifulSoup

def on_page_markdown(markdown: str, page, config, files) -> str:
    if not page.meta:
        return markdown

    docs_dir = Path(config['docs_dir'])
    templates_dir = docs_dir / '_templates'

    additions = []

    for key, filename in [
        ('plan', 'constraints_plan.md'),
        ('permissions', 'constraints_permissions.md'),
        ('roles', 'constraints_roles.md'),
    ]:
        if key in page.meta and page.meta[key]:
            path = templates_dir / filename
            if path.is_file():
                try:
                    content = path.read_text(encoding='utf-8').strip()
                    if content:
                        additions.append(content)
                except Exception as e:
                    print(f"Ошибка в {filename}: {e}")

    if not additions:
        return markdown

    # Шаблоны уже содержат {{ page.meta.xxx }}, но хук срабатывает ДО рендеринга macros
    # Поэтому нужно вручную отрендерить содержимое шаблонов
    from jinja2 import Environment, FileSystemLoader

    j2_env = Environment(loader=FileSystemLoader(str(templates_dir)))

    rendered_additions = []
    for content in additions:
        try:
            template = j2_env.from_string(content)
            rendered = template.render(
                page=page,
                config=config,
                **page.meta  # ← даёт прямой доступ к roles, plan и т.д.
            )
            rendered_additions.append(rendered.strip())
        except Exception as e:
            print(f"Jinja ошибка в шаблоне: {e}")
            rendered_additions.append(content)  # fallback на сырой текст

    if rendered_additions:
        block = "\n\n".join(rendered_additions) + "\n\n---\n\n"
        markdown = block + markdown

    return markdown

def on_page_content(html: str, page, config, files) -> str:
    if not page.meta:
        return html

    # Проверяем, есть ли хотя бы один из ключей (чтобы не трогать все страницы)
    has_constraints = any(
        key in page.meta and page.meta[key]
        for key in ['plan', 'permissions', 'roles']
    )
    if not has_constraints:
        return html

    soup = BeautifulSoup(html, 'html.parser')

    # Находим все admonition-блоки в самом начале основного контента
    # Обычно они внутри <div class="md-content__inner"> или похожего
    main_content = soup.select_one('article.md-content__inner') or soup.body

    if not main_content:
        return html  # на всякий случай

    # Собираем первые admonition-элементы (до первого не-admonition)
    admonitions = []
    current = main_content.find(True)  # первый дочерний тег

    while current and 'admonition' in current.get('class', []):
        admonitions.append(current.extract())  # вырезаем и сохраняем
        current = main_content.find(True)

    if not admonitions:
        return str(soup)  # ничего не нашли — возвращаем как есть

    # Создаём контейнер
    container = soup.new_tag('div')
    container['class'] = 'admonition-container'

    for adm in admonitions:
        container.append(adm)

    # Вставляем контейнер в начало основного контента
    if main_content.contents:
        main_content.insert(0, container)
    else:
        main_content.append(container)

    return str(soup)