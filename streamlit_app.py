import streamlit as st
import requests
import pandas as pd

# URL n8n Webhook
N8N_WEBHOOK_URL = "https://spot2d.app.n8n.cloud/webhook-test/93ad63a0-8bab-4cf1-b446-f71ae3f988fa"

st.title("📊 Аналитическая система")
st.subheader("Введите запрос на естественном языке")

# Форма для ввода текста
user_input = st.text_input("Введите текстовый запрос:", "")

if st.button("Сформировать отчет"):
    if user_input:
        with st.spinner("Генерируем отчет... ⏳"):
            try:
                # Отправляем запрос на Webhook
                response = requests.post(N8N_WEBHOOK_URL, json={"query": user_input})
                response.raise_for_status()

                # Получаем результат
                result = response.json()

                # Проверяем, если результат содержит данные
                if len(result) > 0 and "data" in result[0]:
                    raw_data = result[0]["data"]

                    # Преобразуем массив массивов в DataFrame
                    if raw_data and isinstance(raw_data, list):
                        df = pd.DataFrame(raw_data[1:], columns=raw_data[0])

                        # Отображаем таблицу
                        st.subheader("📊 Таблица данных")
                        st.table(df)
                    else:
                        st.warning("Нет данных для отображения.")
                else:
                    st.warning("Ответ от Webhook не содержит данных.")
            except requests.exceptions.RequestException as e:
                st.error(f"Ошибка при запросе к n8n: {str(e)}")
    else:
        st.warning("Введите запрос!")
