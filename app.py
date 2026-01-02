import streamlit as st
import os
from pathlib import Path
import markdown
from natsort import natsorted


# Настройка страницы
st.set_page_config(
    page_title="Навигатор по документации",
    page_icon="📚",
    layout="wide"
)

# Инициализация состояния
if 'current_path' not in st.session_state:
    st.session_state.current_path = []
if 'selected_file' not in st.session_state:
    st.session_state.selected_file = None

# Функция для получения содержимого текущей папки
def get_folder_contents(root_path, current_path):
    """Получает папки и файлы в текущей директории"""
    full_path = os.path.join(root_path, *current_path) if current_path else root_path
    
    folders = []
    files = []
    
    try:
        items = natsorted(os.listdir(full_path), key=lambda x: str(x))
        for item in items:
            item_path = os.path.join(full_path, item)
            if os.path.isdir(item_path):
                # Проверяем, есть ли внутри MD файлы (рекурсивно)
                has_md = any(Path(item_path).rglob('*.md'))
                if has_md:
                    folders.append(item)
            elif item.endswith('.md'):
                files.append(item)
    except Exception as e:
        st.error(f"Ошибка чтения папки: {e}")
    
    return folders, files

# Функция для подсчета MD файлов
def count_md_files(path):
    """Подсчитывает количество MD файлов в папке и подпапках"""
    return sum(1 for _ in Path(path).rglob('*.md'))

# Функция для чтения MD файла
def read_md_file(file_path):
    """Читает содержимое MD файла"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Ошибка чтения файла: {str(e)}"


# Основной код
def main():
    data_path = "data"
    
    # Проверка существования папки
    if not os.path.exists(data_path):
        st.error(f"Папка '{data_path}' не найдена!")
        st.info("Создайте папку 'data' в директории с приложением")
        return
    
    # Боковая панель
    st.sidebar.title("🗂️ Навигация")
    

    
    st.sidebar.divider()
    
    # Хлебные крошки (навигация)
    if st.session_state.current_path:
        st.sidebar.markdown("**📍 Текущий путь:**")
        
        # Кнопка "В корень"
        if st.sidebar.button("🏠 Корень", use_container_width=True):
            st.session_state.current_path = []
            st.session_state.selected_file = None
            st.rerun()
        
        # Показываем путь с кнопками
        for i, part in enumerate(st.session_state.current_path):
            indent = "　" * i
            if st.sidebar.button(f"{indent}📁 {part}", key=f"breadcrumb_{i}", use_container_width=True):
                st.session_state.current_path = st.session_state.current_path[:i+1]
                st.session_state.selected_file = None
                st.rerun()
    else:
        st.sidebar.markdown("**📍 Корневая папка**")
    
    st.sidebar.divider()
    
    # Навигация между файлами в боковой панели
    if st.session_state.selected_file:
        st.sidebar.markdown("**🧭 Навигация по файлам**")
        
        _, current_files = get_folder_contents(data_path, st.session_state.current_path)
        current_index = current_files.index(st.session_state.selected_file) if st.session_state.selected_file in current_files else -1
        
        # Предыдущий файл
        if current_index > 0:
            if st.sidebar.button("⬅️ Предыдущий файл", use_container_width=True, key="sidebar_prev"):
                st.session_state.selected_file = current_files[current_index - 1]
                st.rerun()
        else:
            st.sidebar.button("⬅️ Предыдущий файл", disabled=True, use_container_width=True, key="sidebar_prev_disabled")
        
        # Следующий файл
        if current_index < len(current_files) - 1 and current_index != -1:
            if st.sidebar.button("Следующий файл ➡️", use_container_width=True, key="sidebar_next"):
                st.session_state.selected_file = current_files[current_index + 1]
                st.rerun()
        else:
            st.sidebar.button("Следующий файл ➡️", disabled=True, use_container_width=True, key="sidebar_next_disabled")
        
        # Позиция
        if current_index != -1:
            st.sidebar.caption(f"Файл {current_index + 1} из {len(current_files)}")
        
        st.sidebar.divider()
    
    # Статистика
    current_full_path = os.path.join(data_path, *st.session_state.current_path)
    total_files = count_md_files(current_full_path)
    st.sidebar.metric("📊 Файлов в текущей папке", total_files)
    
    # Основная область
    if st.session_state.selected_file:
        # Показываем содержимое файла
        file_path = os.path.join(data_path, *st.session_state.current_path, st.session_state.selected_file)
        
        # Получаем список всех файлов в текущей папке для навигации
        _, current_files = get_folder_contents(data_path, st.session_state.current_path)
        current_index = current_files.index(st.session_state.selected_file) if st.session_state.selected_file in current_files else -1
        
        # Навигация между файлами
        col1, col2, col3, col4 = st.columns([1, 1, 3, 1])
        
        with col1:
            # Предыдущий файл
            if current_index > 0:
                if st.button("⬅️ Предыдущий", use_container_width=True):
                    st.session_state.selected_file = current_files[current_index - 1]
                    st.rerun()
            else:
                st.button("⬅️ Предыдущий", disabled=True, use_container_width=True)
        
        with col2:
            # Следующий файл
            if current_index < len(current_files) - 1 and current_index != -1:
                if st.button("Следующий ➡️", use_container_width=True):
                    st.session_state.selected_file = current_files[current_index + 1]
                    st.rerun()
            else:
                st.button("Следующий ➡️", disabled=True, use_container_width=True)
        
        with col3:
            # Показываем позицию
            if current_index != -1:
                st.markdown(f"<div style='text-align: center; padding-top: 8px;'>Файл {current_index + 1} из {len(current_files)}</div>", unsafe_allow_html=True)
        
        with col4:
            # Кнопка назад к списку
            if st.button("📋 К списку", use_container_width=True):
                st.session_state.selected_file = None
                st.rerun()
        
        st.divider()
        
        st.title(f"📄 {st.session_state.selected_file}")
        
        # Показываем путь
        if st.session_state.current_path:
            path_str = " / ".join(st.session_state.current_path)
            st.caption(f"📁 {path_str}")
        
        # Кнопка скачивания
        content = read_md_file(file_path)
        st.download_button(
            label="⬇️ Скачать",
            data=content,
            file_name=st.session_state.selected_file,
            mime="text/markdown"
        )
        
        st.divider()
        
        # Режим отображения
        view_mode = st.radio(
            "Режим:",
            ["📖 Форматированный", "📖 Форматированный +", "📝 Исходный код"],
            horizontal=True
        )
        
        if view_mode == "📖 Форматированный +":
            html_content = markdown.markdown(
                content,
                extensions=['extra', 'codehilite', 'fenced_code', 'tables']
            )
            st.markdown(html_content, unsafe_allow_html=True)
        elif view_mode == "📖 Форматированный":
            st.markdown(content, unsafe_allow_html=True)
        else:
            st.code(content, language="markdown", line_numbers=True)
        
        # Навигация между файлами после текста
        st.divider()
        st.markdown("### 🧭 Навигация")
        
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            # Предыдущий файл
            if current_index > 0:
                if st.button("⬅️ Предыдущий", use_container_width=True, key="bottom_prev"):
                    st.session_state.selected_file = current_files[current_index - 1]
                    st.rerun()
            else:
                st.button("⬅️ Предыдущий", disabled=True, use_container_width=True, key="bottom_prev_disabled")
        
        with col2:
            # Следующий файл
            if current_index < len(current_files) - 1 and current_index != -1:
                if st.button("Следующий ➡️", use_container_width=True, key="bottom_next"):
                    st.session_state.selected_file = current_files[current_index + 1]
                    st.rerun()
            else:
                st.button("Следующий ➡️", disabled=True, use_container_width=True, key="bottom_next_disabled")
        
        with col3:
            # Кнопка назад к списку
            if st.button("📋 Вернуться к списку файлов", use_container_width=True, key="bottom_back"):
                st.session_state.selected_file = None
                st.rerun()
    
    else:
        # Показываем содержимое текущей папки
        if st.session_state.current_path:
            st.title(f"📁 {st.session_state.current_path[-1]}")
            path_str = " / ".join(st.session_state.current_path)
            st.caption(f"Путь: `{path_str}`")
        else:
            st.title("📚 Навигатор документации")
            st.caption("Выберите категорию для начала работы")
        
        st.divider()
        
        # Получаем содержимое
        folders, files = get_folder_contents(data_path, st.session_state.current_path)
        
        # Отображаем папки
        # if folders:
        #     st.subheader("📂 Папки")
            
        #     cols = st.columns(2)
        #     for idx, folder in enumerate(folders):
        #         folder_path = os.path.join(data_path, *st.session_state.current_path, folder)
        #         file_count = count_md_files(folder_path)
                
        #         with cols[idx % 2]:
        #             if st.button(
        #                 f"📁 {folder}\n\n`{file_count} файлов`",
        #                 key=f"folder_{idx}",
        #                 use_container_width=True
        #             ):
        #                 st.session_state.current_path.append(folder)
        #                 st.session_state.selected_file = None
        #                 st.rerun()

        if folders:
            st.subheader("📂 Папки")
            
            
            for idx, folder in enumerate(folders):
                folder_path = os.path.join(data_path, *st.session_state.current_path, folder)
                file_count = count_md_files(folder_path)
                
            
                if st.button(
                    f"📁 {folder}\n\n`{file_count} файлов`",
                    key=f"folder_{idx}",
                    use_container_width=True
                ):
                    st.session_state.current_path.append(folder)
                    st.session_state.selected_file = None
                    st.rerun()
        
        # Отображаем файлы
        # if files:
        #     st.subheader(f"📄 Файлы ({len(files)})")
            
        #     for idx, file in enumerate(files):
        #         col1, col2 = st.columns([5, 1])
                
        #         with col1:
        #             st.markdown(f"**{file}**")
                
        #         with col2:
        #             if st.button("Открыть", key=f"file_{idx}"):
        #                 st.session_state.selected_file = file
        #                 st.rerun()
                
        #         if idx < len(files) - 1:
        #             st.divider()
        
        if files:
            st.subheader(f"📄 Файлы ({len(files)})")
            
            for idx, file in enumerate(files):
                if st.button(f"**{file}**", key=f"file_{idx}"):
                        st.session_state.selected_file = file
                        st.rerun()
        
        if not folders and not files:
            st.info("Эта папка пуста")
    

if __name__ == "__main__":
    main()