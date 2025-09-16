import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

# --- НОВЫЙ, ИСПРАВЛЕННЫЙ КОД ---

st.set_page_config(page_title="Регистрация", page_icon="🔑")

# Загружаем конфигурацию
try:
    with open('pages/config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)
except FileNotFoundError:
    st.error("Файл конфигурации 'config.yaml' не найден. Убедитесь, что он находится в папке 'pages'.")
    st.stop()


# Инициализируем аутентификатор
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# Новый, современный способ вызова формы регистрации
try:
    if authenticator.register_user(form_name='Регистрация нового пользователя', location='main', preauthorization=False):
        st.success('Пользователь успешно зарегистрирован! Теперь вы можете войти на главной странице.')
        # Сохраняем обновленную конфигурацию
        with open('pages/config.yaml', 'w') as file:
            yaml.dump(config, file, default_flow_style=False)
except Exception as e:
    st.error(e)
