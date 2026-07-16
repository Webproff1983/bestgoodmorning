#!/usr/bin/env python3
import os
import sys
import datetime as dt
import random
import xml.etree.ElementTree as ET
import requests

# ============ НАСТРОЙКИ ============
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Координаты Костюковичей для погоды
LATITUDE = 53.3136
LONGITUDE = 32.0639

# Персональные данные (Рак, 18.07.1975)
WIFE_BIRTH_DATE = "18.07.1975"
WIFE_ZODIAC_SIGN = "cancer"

# ============ ВАРИАТИВНОСТЬ ПРИВЕТСТВИЙ ============
MORNING_GREETINGS = [
    "Доброе утро, любимая! ❤️ Пусть этот день принесет тебе много улыбок и тепла.",
    "С добрым утром, моя радость! 🥰 Желаю тебе легкого и чудесного дня.",
    "Доброе утро, мое солнышко! ☀️ Пусть сегодня всё складывается легко и просто.",
    "Доброе утро, прекрасная моя! 🌺 Желаю, чтобы этот день был наполнен приятными моментами.",
    "С добрым утречком, любимая! Котик мой 😘 Пусть день начнется с хороших новостей!",
    "Доброе утро, нежная моя! 🕊️ Желаю тебе отличного настроения на весь день!",
    "Прекрасного утра тебе, моя любовь! 💞 Пусть этот день будет особенным и радостным."
]

# ============ ИСТОЧНИКИ ДАННЫХ ============

def get_weather():
    """Получает актуальную погоду в Костюковичах через Open-Meteo API"""
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={LATITUDE}"
        f"&longitude={LONGITUDE}"
        f"&current=temperature_2m,relative_humidity_2m,weather_code"
        f"&daily=temperature_2m_max,temperature_2m_min"
        f"&timezone=Europe/Minsk"
    )
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            data = response.json()
            curr = data["current"]
            daily = data["daily"]
            
            temp_now = round(curr["temperature_2m"])
            temp_max = round(daily["temperature_2m_max"][0])
            temp_min = round(daily["temperature_2m_min"][0])
            code = curr["weather_code"]
            
            # Декодируем код погоды в понятную фразу и эмодзи
            wmo_codes = {
                0: "ясно ☀️", 1: "преимущественно ясно 🌤️", 2: "переменная облачность ⛅", 
                3: "пасмурно ☁️", 45: "туманно 🌫️", 48: "туманно 🌫️",
                51: "морось 🌧️", 53: "умеренная морось 🌧️", 55: "плотная морось 🌧️",
                61: "слабый дождь 🌦️", 63: "умеренный дождь 🌧️", 65: "сильный дождь 🌧️",
                71: "слабый снегопад 🌨️", 73: "умеренный снегопад 🌨️", 75: "сильный снегопад ❄️",
                80: "слабый ливень 🌦️", 81: "умеренный ливень 🌧️", 82: "сильный ливень ⛈️",
                95: "гроза ⛈️"
            }
            desc = wmo_codes.get(code, "облачно ☁️")
            
            sign_now = "+" if temp_now > 0 else ""
            sign_max = "+" if temp_max > 0 else ""
            sign_min = "+" if temp_min > 0 else ""
            
            return f"🌡️ Сейчас <b>{sign_now}{temp_now}°C</b> ({desc}). Днем ожидается до <b>{sign_max}{temp_max}°C</b>, ночью <b>{sign_min}{temp_min}°C</b>."
    except Exception as e:
        print(f"Ошибка получения погоды: {e}")
    return "🌡️ Не удалось загрузить прогноз погоды на сегодня."


def get_quote():
    """Получает вдохновляющую цитату дня с переводом на русский"""
    try:
        response = requests.get("https://favqs.com/api/qotd", timeout=10)
        if response.status_code == 200:
            data = response.json()
            eng_text = data['quote']['body']
            author = data['quote']['author']
            
            # Переводим на русский язык через API Google Translate
            translate_url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=ru&dt=t&q={eng_text}"
            tr_res = requests.get(translate_url, timeout=10).json()
            ru_text = tr_res[0][0][0]
            return f"«{ru_text}»\n— <i>{author}</i>"
    except Exception as e:
        print(f"Ошибка получения цитаты: {e}")
    return "«Начни оттуда, где ты сейчас. Используй то, что у тебя есть. Делай то, что можешь».\n— <i>Артур Эш</i>"


def get_horoscope(sign=WIFE_ZODIAC_SIGN):
    """Парсит точный ежедневный гороскоп с ignio.com"""
    try:
        response = requests.get("https://ignio.com/r/export/utf/xml/daily/com.xml", timeout=15)
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            today_node = root.find(f"./{sign}/today")
            if today_node is not None:
                return today_node.text.strip()
    except Exception as e:
        print(f"Ошибка получения гороскопа: {e}")
    return "Сегодня звезды советуют вам прислушаться к своей интуиции. Отличный день для создания уюта и приятного общения."


def calculate_numerology(birth_str=WIFE_BIRTH_DATE):
    """
    Автоматически рассчитывает Личное Число Дня.
    Сумма цифр даты рождения + сумма цифр сегодняшней даты, свернутая до 1-9.
    """
    def digit_sum(n):
        while n > 9:
            n = sum(int(digit) for digit in str(n))
        return n

    # Цифры даты рождения (18.07.1975 -> 1+8+0+7+1+9+7+5 = 38 -> 11 -> 2)
    birth_digits = sum(int(c) for c in birth_str if c.isdigit())
    birth_number = digit_sum(birth_digits)
    
    # Цифры сегодняшнего дня
    today = dt.datetime.now()
    today_str = today.strftime("%d%m%Y")
    today_digits = sum(int(c) for c in today_str if c.isdigit())
    today_number = digit_sum(today_digits)
    
    # Итоговое личное число дня
    personal_day_number = digit_sum(birth_number + today_number)
    
    # Подробные нумерологические расшифровки
    interpretations = {
        1: {
            "title": "Лидерство, новые старты и уверенность",
            "desc": "Сегодня день мощной личной энергии. Благоприятно начинать новые проекты, принимать смелые решения и полагаться исключительно на себя. Вселенная дает зеленый свет для проявления инициативы.",
            "focus": "Сконцентрируйся на личных желаниях и не бойся быть в центре внимания.",
            "talisman": "Янтарь ☀️ | Цвет дня: Золотой"
        },
        2: {
            "title": "Гармония, партнерство и интуиция",
            "desc": "День мягких энергий, дипломатии и сотрудничества. Сегодня невероятно обострена интуиция — прислушивайся к внутреннему голосу. Отличное время для душевных разговоров и укрепления союзов.",
            "focus": "Избегай спешки и резких суждений. Сила сегодня — в мягкости.",
            "talisman": "Жемчуг 🌙 | Цвет дня: Серебристый или белый"
        },
        3: {
            "title": "Творчество, общение и самовыражение",
            "desc": "Яркий, оптимистичный и легкий день. Время для самовыражения, творчества, встреч с друзьями и искреннего смеха. Любые идеи, рожденные сегодня, будут нести в себе созидательную искру.",
            "focus": "Дари радость окружающим и позволь себе немного побыть беззаботной.",
            "talisman": "Аметист 🔮 | Цвет дня: Желтый или фиолетовый"
        },
        4: {
            "title": "Стабильность, порядок и созидание",
            "desc": "День заземления, практичности и наведения порядка. Отлично подходит для того, чтобы разложить мысли «по полочкам», заняться обустройством уюта или завершением накопившихся дел. Труд сегодня принесет внутреннее спокойствие.",
            "focus": "Фокусируйся на деталях и создавай прочный фундамент для будущего.",
            "talisman": "Нефрит 🌳 | Цвет дня: Зеленый или коричневый"
        },
        5: {
            "title": "Свобода, перемены и новые впечатления",
            "desc": "День динамики, движения и неожиданных приятных сюрпризов. Отлично подходит для поездок, смены обстановки, спонтанных покупок или изучения чего-то нового. Рутина сегодня будет утомлять, так что впусти в жизнь свежий ветер!",
            "focus": "Будь гибкой и открытой к любым изменениям планов.",
            "talisman": "Бирюза ✈️ | Цвет дня: Голубой или бирюзовый"
        },
        6: {
            "title": "Любовь, семья, домашний очаг и красота",
            "desc": "Самый теплый и гармоничный день вибрации шестерки. Энергия направлена на заботу о близких, создание красоты вокруг себя и любовь. Отличное время для бьюти-процедур, свиданий, покупки декора в дом или просто теплого семейного вечера.",
            "focus": "Окружи себя эстетикой и подари тепло тем, кого любишь.",
            "talisman": "Розовый кварц 🌸 | Цвет дня: Розовый или пастельный"
        },
        7: {
            "title": "Мудрость, уединение и духовный рост",
            "desc": "День созерцания, глубоких размышлений и отдыха от суеты. Сегодня важно побыть наедине со своими мыслями, почитать книгу или прогуляться в тишине. Ответы на важные вопросы придут сами, если замедлить темп.",
            "focus": "Подари себе ментальный отдых и займись самопознанием.",
            "talisman": "Горный хрусталь 💎 | Цвет дня: Синий или фиолетовый"
        },
        8: {
            "title": "Успех, изобилие и материальные достижения",
            "desc": "День сильной материальной энергии, карьерных успехов и финансов. Подходящее время для крупных планов, покупок и оценки своих достижений. Твои авторитет и уверенность сегодня на высоте.",
            "focus": "Мысли масштабно и верь в то, что ты заслуживаешь самого лучшего.",
            "talisman": "Гранат 🍷 | Цвет дня: Красный или бордовый"
        },
        9: {
            "title": "Завершение, мудрость и освобождение",
            "desc": "День очищения и подведения итогов. Время освободить место для нового: завершить старые дела, отпустить обиды или ненужные мысли. Прекрасный момент для щедрости, благотворительности и внутренней гармонии.",
            "focus": "Наведи порядок в душе, заверши начатое и открой сердце будущему.",
            "talisman": "Опал ✨ | Цвет дня: Оливковый или золотистый"
        }
    }
    
    default_res = {
        "title": "Гармония и баланс",
        "desc": "Прекрасный, ровный день для любых созидательных дел и заботы о себе.",
        "focus": "Улыбайся и верь в свои силы.",
        "talisman": "Твоя улыбка 😊"
    }
    
    res = interpretations.get(personal_day_number, default_res)
    return personal_day_number, res


def main():
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Ошибка: Настройки Telegram не заданы в Секретах!")
        return

    # Собираем данные
    greeting = random.choice(MORNING_GREETINGS)  # Случайное приветствие
    weather_text = get_weather()
    quote = get_quote()
    horoscope = get_horoscope()
    num_val, num_data = calculate_numerology()
    
    # Формируем дату на русском языке
    months = ["января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа", "сентября", "октября", "ноября", "декабря"]
    today = dt.datetime.now()
    date_title = f"{today.day} {months[today.month - 1]} {today.year}"
    
    # Красивый текст сообщения
    message_text = (
        f"🌅 <b>{greeting}</b>\n"
        f"📅 Сегодня <b>{date_title}</b>\n\n"
        f"☀️ <b>Погода в Костюковичах:</b>\n"
        f"{weather_text}\n\n"
        f"✨ <b>Мотивация дня:</b>\n"
        f"{quote}\n\n"
        f"🔮 <b>Гороскоп на сегодня (Рак):</b>\n"
        f"{horoscope}\n\n"
        f"🔢 <b>Нумерологический расклад:</b>\n"
        f"🔮 Твое личное число дня — <b>{num_val}</b> (<i>{num_data['title']}</i>).\n\n"
        f"📝 <b>Что это значит:</b>\n"
        f"{num_data['desc']}\n\n"
        f"🎯 <b>Фокус дня:</b> {num_data['focus']}\n"
        f"💎 <b>Талисман:</b> {num_data['talisman']}\n\n"
        f"Желаю тебе прекрасного дня! Люблю тебя! 🥰"
    )
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message_text,
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, data=payload, timeout=30)
        if response.status_code == 200:
            print("Сообщение успешно отправлено!")
        else:
            print(f"Ошибка отправки: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Ошибка при работе с Telegram API: {e}")

if __name__ == "__main__":
    main()
