import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import streamlit as st
import os

# Путь к файлу конфигурации определен надежно
try:
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
    # ИЗМЕНЕНО: Параметр 'preauthorization' заменен на 'pre_authorization'
    if authenticator.register_user('Регистрация нового пользователя', pre_authorization=False):
        st.success('Пользователь успешно зарегистрирован')
        with open(config_path, 'w') as file:
            yaml.dump(config, file, default_flow_style=False)
except Exception as e:
    st.error(e)