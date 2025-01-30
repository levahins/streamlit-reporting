import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder

# URL n8n Webhook
N8N_WEBHOOK_URL = "https://spot2d.app.n8n.cloud/webhook-test/93ad63a0-8bab-4cf1-b446-f71ae3f988fa"

# Заголовок
st.title("📊 Аналитическая система")

# Инструкция
st.markdown("""
### ℹ️ Как пользоваться этим инструментом?
Этот инструмент позволяет получать данные о продажах на основе вашего текстового запроса.  
Просто опишите, что вам нужно, например:  
📌 *"Продажи по дистрибьюторам и товарам за январь в штуках и деньгах"*  
и система автоматически обработает запрос и выдаст нужные данные.  
🔹 **Вам не нужно разбираться в технических деталях** — просто сформулируйте запрос естественным языком.
""")

st.subheader("Введите запрос на естественном языке")

# Форма для ввода запроса
user_input = st.text_input("Введите текстовый запрос:", "")

if st.button("Сформировать отчет"):
    if user_input:
        with st.spinner("Генерируем отчет... ⏳"):
            try:
                response = requests.post(N8N_WEBHOOK_URL, json={"query": user_input})
                response.raise_for_status()
                result = response.json()

                if "data" in result and isinstance(result["data"], str):
                    # Разбиваем CSV-данные на строки
                    raw_data = result["data"].strip().split("\r\n")

                    # Разделяем заголовки и строки
                    headers = [header.strip('"') for header in raw_data[0].split(";")]
                    rows = [row.split(";") for row in raw_data[1:]]

                    # Преобразуем данные в DataFrame
                    df = pd.DataFrame(rows, columns=headers)

                    # Приводим числовые значения к float
                    for col in headers[1:]:
                        df[col] = pd.to_numeric(df[col].str.replace('"', ''), errors="coerce").fillna(0)

                    # Определяем числовые колонки
                    numeric_columns = df.select_dtypes(include=["number"]).columns

                    # Сортируем по первой числовой колонке
                    if len(numeric_columns) > 0:
                        df = df.sort_values(by=numeric_columns[0], ascending=False)

                    # Рассчитываем итоговую строку
                    total_row = {col: df[col].sum() if col in numeric_columns else "Итого" for col in df.columns}

                    # Настраиваем AgGrid для правильного отображения чисел
                    gb = GridOptionsBuilder.from_dataframe(df)
                    gb.configure_pagination(paginationAutoPageSize=True)
                    gb.configure_default_column(editable=False, groupable=True, sortable=True)

                    # Применяем форматирование чисел (без кавычек)
                    for col in numeric_columns:
                        gb.configure_column(col, type=["numericColumn", "number"], valueFormatter="x.toLocaleString()")

                    gridOptions = gb.build()
                    gridOptions["suppressAggFuncInHeader"] = True
                    gridOptions["pinnedBottomRowData"] = [total_row]

                    # Отображаем интерактивную таблицу
                    st.subheader("📊 Интерактивная таблица")
                    AgGrid(df, gridOptions=gridOptions, height=500, theme="streamlit")

                    # Отображаем график
                    st.subheader("📈 Интерактивные графики")
                    selected_metric = st.selectbox("Выберите метрику для графика:", numeric_columns)
                    fig = px.bar(
                        df[:-1],  # Исключаем итоговую строку
                        x=df.columns[0],
                        y=selected_metric,
                        labels={df.columns[0]: "Категории", selected_metric: "Значения"},
                        title=f"Распределение по {selected_metric}",
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
