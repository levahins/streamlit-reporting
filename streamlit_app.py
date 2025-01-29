import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

# URL n8n Webhook
N8N_WEBHOOK_URL = "https://n8n.yourdomain.com/webhook/chatgpt_report"

st.title("📊 Аналитическая система")
st.subheader("Введите запрос на естественном языке")

# Форма для запроса
user_input = st.text_input("Введите текстовый запрос:", "")

if st.button("Сформировать отчет"):
    if user_input:
        with st.spinner("Генерируем отчет... ⏳"):
            response = requests.post(N8N_WEBHOOK_URL, json={"query": user_input})
            if response.status_code == 200:
                data = response.json()

                # Преобразуем JSON в DataFrame
                df = pd.DataFrame(data)

                # Показываем таблицу
                st.subheader("📄 Данные отчета")
                st.dataframe(df)

                # Визуализация: график продаж
                st.subheader("📊 График продаж")
                fig, ax = plt.subplots()
                ax.bar(df["category"], df["sales_units"])
                st.pyplot(fig)
            else:
                st.error("Ошибка! Не удалось получить данные.")
    else:
        st.warning("Введите запрос!")
