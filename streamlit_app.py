import streamlit as st
import requests
import pandas as pd
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder

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

                # Проверяем, что результат содержит ключ "data"
                if "data" in result:
                    raw_data = result["data"]

                    # Преобразуем массив массивов в DataFrame
                    if isinstance(raw_data, list):
                        df = pd.DataFrame(raw_data[1:], columns=raw_data[0])

                        # Преобразуем числовые значения
                        for col in df.columns[1:]:  # Пропускаем первый столбец (категории)
                            df[col] = pd.to_numeric(df[col], errors='coerce')

                        # Сортируем таблицу по убыванию значений в первом числовом столбце
                        df = df.sort_values(by=df.columns[1], ascending=False)

                        # Добавляем строку с суммой значений
                        sum_row = ["Итого"] + list(df.iloc[:, 1:].sum())
                        df.loc["Итого"] = sum_row

                        # Настраиваем интерактивную таблицу
                        st.subheader("📊 Интерактивная таблица")
                        gb = GridOptionsBuilder.from_dataframe(df)
                        gb.configure_pagination(paginationAutoPageSize=True)  # Пагинация
                        gb.configure_default_column(editable=False, groupable=True)  # Настройки колонок
                        gridOptions = gb.build()

                        # Отображаем таблицу
                        AgGrid(df, gridOptions=gridOptions, height=400, theme="streamlit")
                    else:
                        st.warning("Нет данных для отображения.")
                else:
                    st.warning("Ответ от Webhook не содержит ожидаемого ключа 'data'.")
            except requests.exceptions.RequestException as e:
                st.error(f"Ошибка при запросе к n8n: {str(e)}")
            except Exception as e:
                st.error(f"Неожиданная ошибка: {str(e)}")
    else:
        st.warning("Введите запрос!")
