import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import streamlit as st


with open('pages/config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

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
        with open('pages/config.yaml', 'w') as file:
            yaml.dump(config, file, default_flow_style=False)
except Exception as e:
    st.error(e)
