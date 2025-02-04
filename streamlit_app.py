import streamlit as st
import requests

# URL вашего вебхука (обновлён)
N8N_WEBHOOK_URL = "https://spot2d.app.n8n.cloud/webhook/dialogue-simulated"

# Заголовок страницы и инструкция
st.title("💬 Диалог с аналитической системой")
st.markdown(
    """
    **Добро пожаловать!**

    Задавайте вопросы системе аналитики в свободной форме.  
    Система сгенерирует логичный и подробный ответ, как если бы анализировала реальные данные.
    """
)

# Инициализация истории диалога в session_state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Кнопка для начала нового диалога (очистка истории)
if st.button("Начать новый диалог"):
    st.session_state.chat_history = []

# Отображение истории переписки
st.markdown("### История диалога:")
for message in st.session_state.chat_history:
    if message["role"] == "user":
        st.markdown(f"**Вы:** {message['content']}")
    else:
        st.markdown(f"**Система:** {message['content']}")

st.markdown("---")

# Используем форму для ввода сообщения с clear_on_submit=True,
# а обработку отправки выносим за пределы блока формы, чтобы избежать двойного добавления.
with st.form(key="chat_form", clear_on_submit=True):
    user_message = st.text_input("Ваше сообщение:")
    submitted = st.form_submit_button("Отправить сообщение")

if submitted and user_message:
    # Добавляем сообщение пользователя в историю
    st.session_state.chat_history.append({"role": "user", "content": user_message})

    # Отправляем запрос на вебхук и получаем ответ системы
    with st.spinner("Ожидание ответа системы..."):
        try:
            response = requests.post(N8N_WEBHOOK_URL, json={"query": user_message})
            response.raise_for_status()
            result = response.json()
            # Ожидается, что webhook возвращает ответ в поле 'answer'
            answer = result.get("answer", "Система не вернула ответ.")
        except Exception as e:
            answer = f"Ошибка: {e}"

    # Добавляем ответ системы в историю диалога
    st.session_state.chat_history.append({"role": "system", "content": answer})
