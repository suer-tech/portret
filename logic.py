import os
from typing import Dict, List, Any

from sqlalchemy.testing.suite.test_reflection import metadata

from ai_client import handle_stage_style
from .stages import STAGES
from . import ai_client


def handle_message(current_stage: str, history: List[Dict[str, str]], message: str, metadata: Dict) -> Dict:
    # Карта обработчиков по стадиям
    stage_handlers = {
        "первичное общение": ai_client.handle_stage_primary,
        "выбор стиля": handle_style_stage_logic,
        "выбор сроков и города": ai_client.handle_stage_city,
        "Расчет стоимости": ai_client.handle_stage_cost,
        "отправка реквизитов": ai_client.handle_stage_payment,
        "предложение дополнительных услуг": ai_client.handle_stage_additional,
        "предложение премиум холста": ai_client.handle_stage_premium,
        "предложение акции 1+1=3": ai_client.handle_stage_promo,
        "заключительное общение": ai_client.handle_stage_final,
    }

    handler = stage_handlers.get(current_stage)
    if not handler:
        return {"reply": "Неизвестная стадия", "next_stage": current_stage, "updated_history": history}

    result = handler(history, message)

    reply = result["reply"]
    ready_to_next = result.get("ready_to_next", False)
    force_next = result.get("force_next_stage")
    updated_history = result.get("updated_history", history)

    next_stage = current_stage

    # Принудительный переход стадии (например, при фото)
    if force_next:
        next_stage = force_next
    elif ready_to_next and current_stage in STAGES:
        idx = STAGES.index(current_stage)
        if idx + 1 < len(STAGES):
            next_stage = STAGES[idx + 1]
    send_message(reply)
    return {"reply": reply, "next_stage": next_stage, "updated_history": updated_history}


#----------------------------------------------------------------------------------------------------------------------
#--------------------------Обработка этапа 2 Выбор стиля---------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------

# Путь к папке с примерами стилей
STYLE_EXAMPLES_DIR = "static/style_examples"
STYLE_EXAMPLES_FILES = [
    f for f in os.listdir(STYLE_EXAMPLES_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))
]

def handle_style_stage_logic(history: List[Dict[str, str]], message: str, metadata: Dict) -> Dict[str, Any]:
    # Объединяем все тексты из истории сообщений для проверки состояния
    history_texts = " ".join([m["content"] for m in history])

    # Если в истории нет сообщения о 10 примерах, добавляем сообщения и 10 фото
    if "Отправляю примеры наших работ" not in history_texts:
        images_list = STYLE_EXAMPLES_FILES[:10]
        images_links = [f"/static/style_examples/{img}" for img in images_list]
        reply_text = "Отправляю примеры наших работ:"
        history.append({"role": "assistant", "content": reply_text})
        for link in images_links:
            history.append({"role": "assistant", "content": link})
            send_message(reply_text)
        return {"reply": reply_text + " [10 примеров картин]", "ready_to_next": False, "updated_history": history}

    # Если нет сообщения о ручной прорисовке и до/после, добавляем это сообщение и несколько фото
    if "ручную прорисовку, а не обработку фильтрами" not in history_texts:
        reply_text = ("Мы используем только ручную прорисовку, а не обработку фильтрами ✍️ "
                      "Вот ещё наглядный пример до/после) Обратите внимание на детализацию:")
        additional_images = STYLE_EXAMPLES_FILES[10:13]
        images_links = [f"/static/style_examples/{img}" for img in additional_images]
        history.append({"role": "assistant", "content": reply_text})
        for link in images_links:
            history.append({"role": "assistant", "content": link})
            send_message(reply_text)
        return {"reply": reply_text + " [3 дополнительных примера]", "ready_to_next": False, "updated_history": history}

    # Если вопрос о выборе стиля не задан, задаем его и добавляем в историю
    if "Какой пример по стилистике Вам больше всего понравился?" not in history_texts:
        reply_text = "Какой пример по стилистике Вам больше всего понравился?"
        history.append({"role": "assistant", "content": reply_text})
        send_message(reply_text)
        return {"reply": reply_text, "ready_to_next": False, "updated_history": history}

    # Если вопрос о выборе стиля не задан, задаем его и добавляем в историю
    if metadata.get("selected_style"):
        reply_text = """Отлично по стилистике мы с Вами подобрали художественную живопись. И в качестве бонуса попрошу художника сделать для Вас 3 варианта макета с разными фонами, чтобы Вам было из чего выбрать.  
                        Так же отправляю Вам видео нашего готового портрета, чтобы Вы посмотрели, как примерно будет выглядеть и оценили качество и детализацию отрисовки."""
        history.append({"role": "assistant", "content": reply_text})
        send_message(reply_text)
        reply_text_2 = """Уточню последнюю деталь для расчета по стоимости, подскажите, в каком городе планируете получение готовой работы и к какой дате?"""
        send_message(reply_text_2)
        return {"reply": reply_text, "ready_to_next": False, "updated_history": history}

    # Если все выше отправлено, вызываем ИИ-модель для консультации по стилям, обработке возражений
    response = handle_stage_style(history, message)
    send_message(response)
    return response