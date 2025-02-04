import streamlit as st
import requests

# Убедитесь, что у вас Streamlit версии 1.22 или выше:
# pip install --upgrade streamlit

# URL вебхука (обновлён)
N8N_WEBHOOK_URL = "https://spot2d.app.n8n.cloud/webhook/dialogue-simulated"

st.title("💬 Чат с аналитической системой")

# Инициализируем историю сообщений в session_state, если её ещё нет
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Функция для отправки запроса на вебхук и получения ответа системы
def get_system_response(user_text):
    try:
        response = requests.post(N8N_WEBHOOK_URL, json={"query": user_text})
        response.raise_for_status()
        result = response.json()
        return result.get("answer", "Система не вернула ответ.")
    except Exception as e:
        return f"Ошибка: {e}"

# Отображение истории диалога, где каждое сообщение выводится как отдельный блок
for msg in st.session_state["messages"]:
    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])
    else:
        st.chat_message("assistant").write(msg["content"])

# Получение ввода от пользователя через специальное поле ввода для чата
user_input = st.chat_input("Ваше сообщение:")

if user_input:
    # Добавляем сообщение пользователя в историю и отображаем его
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)
    
    # Получаем ответ системы
    with st.spinner("Ожидание ответа системы..."):
        answer = get_system_response(user_input)
    
    # Сохраняем и отображаем ответ системы
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.chat_message("assistant").write(answer)
