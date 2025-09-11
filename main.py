from fastapi import FastAPI
from .models import MessageIn
from .storage import load_histories, save_histories
from .logic import handle_message

app = FastAPI()


@app.post("/message")
async def process_message(msg: MessageIn):
    histories = load_histories()

    # Если пользователь новый
    if msg.user_id not in histories:
        histories[msg.user_id] = {
            "messages": [],
            "metadata": {"stage": "первичное общение", "selected_style": None}
        }

    history = histories[msg.user_id]["messages"]
    metadata = histories[msg.user_id]["metadata"]

    # Сохраняем входящее сообщение
    history.append({"role": "user", "content": msg.message})

    # Обрабатываем сообщение через state machine
    result = handle_message(metadata["stage"], history, msg.message, metadata)

    # Обновляем стадию
    metadata["stage"] = result["next_stage"]

    # Сохраняем ответ
    history.append({"role": "assistant", "content": result["reply"]})

    save_histories(histories)

    return {
        "reply": result["reply"],
        "stage": metadata["stage"],
        "history": history
    }
