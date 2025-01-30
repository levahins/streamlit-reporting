import streamlit as st
import requests

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

                # Проверяем, если ответ содержит данные
                if len(result) > 0 and "message" in result[0]:
                    # Извлекаем сообщение
                    message = result[0]["message"]

                    # Отображаем как текстовый отчет
                    st.subheader("📄 Текстовый отчет")
                    st.text(message)

                    # Преобразуем Markdown в таблицу, если нужно
                    if "--- | ---" in message:
                        st.subheader("📊 Табличный вид")
                        table_data = [
                            row.split(" | ")
                            for row in message.split("\n")
                            if " | " in row
                        ]
                        table_header = table_data[0]
                        table_rows = table_data[1:]
                        
                        # Отображаем таблицу
                        st.table([dict(zip(table_header, row)) for row in table_rows])
                else:
                    st.warning("Пустой ответ от вебхука.")
            except requests.exceptions.RequestException as e:
                st.error(f"Ошибка при запросе к n8n: {str(e)}")
    else:
        st.warning("Введите запрос!")
