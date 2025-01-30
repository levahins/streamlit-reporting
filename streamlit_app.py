import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
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

                    # Проверяем, что raw_data не пустой
                    if isinstance(raw_data, list) and len(raw_data) > 0:
                        # Преобразуем вложенные массивы в DataFrame
                        df = pd.DataFrame(raw_data[1:], columns=raw_data[0])

                        # Попытка преобразовать числовые столбцы к float
                        for col in df.columns[1:]:
                            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

                        # Преобразование данных таблицы в сериализуемые типы
                        df = df.astype(str)

                        # Рассчет итоговой строки
                        numeric_columns = df.select_dtypes(include=["number"]).columns
                        total_row = {col: df[col].astype(float).sum() if col in numeric_columns else "Итого" for col in df.columns}

                        # Настраиваем интерактивную таблицу
                        st.subheader("📊 Интерактивная таблица")
                        gb = GridOptionsBuilder.from_dataframe(df)
                        gb.configure_pagination(paginationAutoPageSize=True)  # Пагинация
                        gb.configure_default_column(editable=False, groupable=True, sortable=True)  # Настройки колонок
                        gridOptions = gb.build()

                        # Указываем итоговую строку явно
                        gridOptions["suppressAggFuncInHeader"] = True
                        gridOptions["pinnedBottomRowData"] = [total_row]

                        # Отображаем таблицу
                        AgGrid(df, gridOptions=gridOptions, height=400, theme="streamlit")

                        # Отображаем график
                        st.subheader("📈 График")
                        fig, ax = plt.subplots(figsize=(5, 4))
                        ax.bar(df[df.columns[0]], df[df.columns[1]].astype(float), color="skyblue")
                        ax.set_xlabel("Категории")
                        ax.set_ylabel("Значения")
                        ax.set_title("Распределение значений")
                        plt.xticks(rotation=45, ha="right")
                        st.pyplot(fig)
                    else:
                        st.warning("Данные отсутствуют или пустые.")
                else:
                    st.warning("Ответ от Webhook не содержит ожидаемого ключа 'data'.")
            except requests.exceptions.RequestException as e:
                st.error(f"Ошибка при запросе к n8n: {str(e)}")
            except Exception as e:
                st.error(f"Неожиданная ошибка: {str(e)}")
    else:
        st.warning("Введите запрос!")
