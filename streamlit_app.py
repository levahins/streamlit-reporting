import streamlit as st
import requests
import pandas as pd
import plotly.express as px
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

                        # Преобразование всех данных в сериализуемые типы
                        df = df.astype({col: float for col in df.select_dtypes(include=["number"]).columns})

                        # Сортировка таблицы по убыванию значений в первом числовом столбце
                        numeric_columns = df.select_dtypes(include=["number"]).columns
                        if len(numeric_columns) > 0:
                            df = df.sort_values(by=numeric_columns[0], ascending=False)

                        # Рассчет итоговой строки
                        total_row = {col: df[col].sum() if col in numeric_columns else "Итого" for col in df.columns}

                        # Преобразование строки "Итого" в сериализуемый формат
                        total_row = {key: float(value) if isinstance(value, (int, float)) else value for key, value in total_row.items()}

                        # Добавляем возможность выбора метрик
                        selected_metrics = st.multiselect(
                            "Выберите метрики для графика:", numeric_columns, default=numeric_columns[:1]
                        )

                        # Создаем Dashboard с таблицей и графиками
                        col1, col2 = st.columns(2)

                        # Отображаем таблицу в первой колонке
                        with col1:
                            st.subheader("📊 Интерактивная таблица")
                            gb = GridOptionsBuilder.from_dataframe(df)
                            gb.configure_pagination(paginationAutoPageSize=True)  # Пагинация
                            gb.configure_default_column(editable=False, groupable=True, sortable=True)  # Настройки колонок
                            gridOptions = gb.build()

                            # Указываем итоговую строку явно
                            gridOptions["suppressAggFuncInHeader"] = True
                            gridOptions["pinnedBottomRowData"] = [total_row]
                            AgGrid(df, gridOptions=gridOptions, height=500, theme="streamlit")

                        # Отображаем интерактивные графики во второй колонке
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
                        st.warning("Данные отсутствуют или пустые.")
                else:
                    st.warning("Ответ от Webhook не содержит ожидаемого ключа 'data'.")
            except requests.exceptions.RequestException as e:
                st.error(f"Ошибка при запросе к n8n: {str(e)}")
            except Exception as e:
                st.error(f"Неожиданная ошибка: {str(e)}")
    else:
        st.warning("Введите запрос!")
