#!/usr/bin/env python3
import os
import sys
import datetime as dt
import xml.etree.ElementTree as ET
import requests

# ============ НАСТРОЙКИ ============
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Персональные данные (Рак, 18.07.1975)
WIFE_BIRTH_DATE = "18.07.1975"
WIFE_ZODIAC_SIGN = "cancer"

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
    # Резервная цитата
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
    
    interpretations = {
        1: "День начинаний и активных действий. Время сделать первый шаг к важной цели.",
        2: "День баланса и интуиции. Доверяйте своим чувствам, сегодня важно слышать окружающих.",
        3: "Творческий день. Самовыражение, улыбки и легкое общение принесут сегодня радость.",
        4: "День практических решений и порядка. Наведите уют в мыслях и планах.",
        5: "День перемен и приключений. Будьте открыты новому, звезды сулят интересные сюрпризы!",
        6: "День гармонии и заботы. Побалуйте себя чем-то приятным и подарите тепло близким.",
        7: "День внутренней перезагрузки. Идеально подходит для размышлений, чтения и отдыха.",
        8: "День больших достижений и сильных решений. Верьте в свои силы — сегодня всё получится!",
        9: "День подведения итогов. Время отпустить старые заботы и освободить место для новой радости."
    }
    
    desc = interpretations.get(personal_day_number, "Благоприятный день для любых гармоничных начинаний.")
    return personal_day_number, desc


def main():
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Ошибка: Настройки Telegram не заданы в Секретах!")
        return

    # Собираем данные
    quote = get_quote()
    horoscope = get_horoscope()
    num_val, num_desc = calculate_numerology()
    
    # Формируем дату на русском языке
    months = ["января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа", "сентября", "октября", "ноября", "декабря"]
    today = dt.datetime.now()
    date_title = f"{today.day} {months[today.month - 1]} {today.year}"
    
    # Красивый текст сообщения
    message_text = (
        f"🌅 <b>Доброе утро, любимая!</b> ❤️\n"
        f"📅 Сегодня <b>{date_title}</b>\n\n"
        f"✨ <b>Мотивация дня:</b>\n"
        f"{quote}\n\n"
        f"🔮 <b>Гороскоп на сегодня (Рак):</b>\n"
        f"{horoscope}\n\n"
        f"🔢 <b>Нумерологический расклад:</b>\n"
        f"Твое личное число дня сегодня — <b>{num_val}</b>.\n"
        f"👉 <i>{num_desc}</i>\n\n"
        f"Желаю тебе самого теплого, легкого и прекрасного дня! Люблю тебя! 🥰"
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
