import streamlit as st
import pandas as pd
import plotly.express as px
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder

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
                # Заглушка для имитации ответа вебхука
                result = {
                    "data": [
                        {
                            "Дистриб'ютор": "DS-Turkey-Adana",
                            "Оборот в штуках": 80739,
                            "Оборот в грошах дистриб'ютора": 602461820
                        },
                        {
                            "Дистриб'ютор": "DS-Turkey-Ankara",
                            "Оборот в штуках": 15500,
                            "Оборот в грошах дистриб'ютора": 151002701
                        },
                        {
                            "Дистриб'ютор": "DS-Turkey-Aydin",
                            "Оборот в штуках": 13156,
                            "Оборот в грошах дистриб'ютора": 114514466
                        },
                        {
                            "Дистриб'ютор": "DS-Turkey-Batman",
                            "Оборот в штуках": 83480,
                            "Оборот в грошах дистриб'ютора": 685734988
                        }
                    ]
                }

                # Проверяем, что данные присутствуют
                if "data" in result and isinstance(result["data"], list):
                    # Преобразуем данные в DataFrame
                    df = pd.DataFrame(result["data"])

                    # Определяем числовые колонки
                    numeric_columns = df.select_dtypes(include=["number"]).columns

                    # Сортируем по первой числовой колонке
                    if len(numeric_columns) > 0:
                        df = df.sort_values(by=numeric_columns[0], ascending=False)

                    # Рассчитываем итоговую строку
                    total_row = {col: df[col].sum() if col in numeric_columns else "Итого" for col in df.columns}

                    # Настраиваем AgGrid для правильного отображения данных
                    gb = GridOptionsBuilder.from_dataframe(df)
                    gb.configure_pagination(paginationAutoPageSize=True)
                    gb.configure_default_column(editable=False, groupable=True, sortable=True)

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
            except Exception as e:
                st.error(f"Неожиданная ошибка: {str(e)}")
    else:
        st.warning("Введите запрос!")
