import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
import io

# URL n8n Webhook
N8N_WEBHOOK_URL = "https://spot2d.app.n8n.cloud/webhook-test/93ad63a0-8bab-4cf1-b446-f71ae3f988fa"

st.title("📊 Аналитическая система")
st.subheader("Введите запрос на естественном языке")

# Форма для ввода запроса
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

                # Проверяем, содержит ли результат ключ "data"
                if isinstance(result, list) and len(result) > 0 and "data" in result[0]:
                    # Извлекаем CSV-данные из JSON
                    csv_data = result[0]["data"]

                    # Убираем лишние кавычки в начале и конце (если есть)
                    csv_data = csv_data.strip("\"")

                    # Преобразуем строку CSV в DataFrame
                    df = pd.read_csv(io.StringIO(csv_data), sep=";", engine="python")

                    # Попытка преобразовать числовые столбцы в float
                    for col in df.columns[1:]:
                        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

                    # Определение числовых столбцов
                    numeric_columns = df.select_dtypes(include=["number"]).columns

                    # Сортировка по первой числовой колонке
                    if len(numeric_columns) > 0:
                        df = df.sort_values(by=numeric_columns[0], ascending=False)

                    # Рассчитываем итоговую строку
                    total_row = {col: df[col].sum() if col in numeric_columns else "Итого" for col in df.columns}
                    total_row = {key: float(value) if isinstance(value, (int, float)) else value for key, value in total_row.items()}

                    # Выбор метрик для графиков
                    selected_metrics = st.multiselect(
                        "Выберите метрики для графика:", numeric_columns, default=numeric_columns[:1]
                    )

                    # Создаем Dashboard с таблицей и графиками
                    col1, col2 = st.columns(2)

                    # Отображаем таблицу
                    with col1:
                        st.subheader("📊 Интерактивная таблица")
                        gb = GridOptionsBuilder.from_dataframe(df)
                        gb.configure_pagination(paginationAutoPageSize=True)
                        gb.configure_default_column(editable=False, groupable=True, sortable=True)
                        gridOptions = gb.build()
                        gridOptions["suppressAggFuncInHeader"] = True
                        gridOptions["pinnedBottomRowData"] = [total_row]
                        AgGrid(df, gridOptions=gridOptions, height=500, theme="streamlit")

                    # Отображаем графики
                    with col2:
                        st.subheader("📈 Интерактивные графики")
                        for metric in selected_metrics:
                            fig = px.bar(
                                df[:-1],  # Исключаем итоговую строку
                                x=df.columns[0],
                                y=metric,
                                labels={df.columns[0]: "Категории", metric: "Значения"},
                                title=f"Распределение по {metric}",
                                text_auto=True,
                            )
                            st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("Ошибка: Webhook вернул пустые или некорректные данные.")
            except requests.exceptions.RequestException as e:
                st.error(f"Ошибка при запросе к n8n: {str(e)}")
            except Exception as e:
                st.error(f"Неожиданная ошибка: {str(e)}")
    else:
        st.warning("Введите запрос!")
