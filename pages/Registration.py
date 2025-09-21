import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import streamlit as st
import os

# ИЗМЕНЕНО: Надежное определение пути к файлу конфигурации
try:
    # __file__ указывает на текущий файл, os.path.dirname получает директорию этого файла
    # os.path.abspath получает абсолютный путь к директории pages
    # os.path.join собирает путь к config.yaml из корня проекта
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'pages/config.yaml')
    with open(config_path) as file:
        config = yaml.load(file, Loader=SafeLoader)
except FileNotFoundError:
    st.error(f"Критическая ошибка: Файл конфигурации 'config.yaml' не найден.")
    st.stop()


authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

try:
    if authenticator.register_user('Регистрация нового пользователя', preauthorization=False):
        st.success('Пользователь успешно зарегистрирован')
        # ИЗМЕНЕНО: Запись в файл по абсолютному пути
        with open(config_path, 'w') as file:
            yaml.dump(config, file, default_flow_style=False)
except Exception as e:
    st.error(e)