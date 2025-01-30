import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

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

                # Проверяем, если результат содержит ошибку
                if "error" in result:
                    st.error(f"Ошибка от n8n: {result['error']}")
                else:
                    # Преобразуем данные в DataFrame, если получен отчет
                    if "data" in result:
                        df = pd.DataFrame(result["data"])

                        # Отображаем таблицу
                        st.subheader("📄 Данные отчета")
                        st.dataframe(df)

                        # Создаем визуализацию: график продаж
                        st.subheader("📊 График продаж")
                        if "category" in df.columns and "sales_units" in df.columns:
                            fig, ax = plt.subplots()
                            ax.bar(df["category"], df["sales_units"])
                            st.pyplot(fig)
                        else:
                            st.warning("Данные не содержат необходимых полей для построения графика.")
                    else:
                        st.warning("Нет данных для отображения.")
            except requests.exceptions.RequestException as e:
                st.error(f"Ошибка при запросе к n8n: {str(e)}")
    else:
        st.warning("Введите запрос!")
