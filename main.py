import os
import time
import asyncio
import uuid
from collections import defaultdict
from datetime import datetime

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from yookassa import Configuration, Payment


# =========================================================
# НАСТРОЙКИ
# =========================================================

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
KATYA_CHAT_ID = os.getenv("KATYA_CHAT_ID")

YOOKASSA_SHOP_ID = os.getenv("YOOKASSA_SHOP_ID")
YOOKASSA_SECRET_KEY = os.getenv("YOOKASSA_SECRET_KEY")

if not BOT_TOKEN:
    raise RuntimeError("Не найден BOT_TOKEN в .env")

if not YOOKASSA_SHOP_ID:
    raise RuntimeError("Не найден YOOKASSA_SHOP_ID в .env")

if not YOOKASSA_SECRET_KEY:
    raise RuntimeError("Не найден YOOKASSA_SECRET_KEY в .env")


Configuration.account_id = YOOKASSA_SHOP_ID
Configuration.secret_key = YOOKASSA_SECRET_KEY


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# =========================================================
# ССЫЛКИ
# =========================================================

INTERNATIONAL_PAYMENT_URL = (
    "https://numerology-expert.payform.ru/"
)

PERSONAL_MESSAGES_URL = (
    "https://t.me/katena_krzs"
)


# =========================================================
# ЗАЩИТА ОТ СПАМА
# =========================================================

user_requests = defaultdict(list)

RATE_LIMIT_COUNT = 5
RATE_LIMIT_SECONDS = 10

payment_in_progress = set()


def is_rate_limited(user_id: int) -> bool:

    now = time.monotonic()

    requests = user_requests[user_id]

    requests[:] = [
        request_time
        for request_time in requests
        if now - request_time < RATE_LIMIT_SECONDS
    ]

    if len(requests) >= RATE_LIMIT_COUNT:
        return True

    requests.append(now)

    return False


# =========================================================
# ПРОГРАММЫ
# =========================================================

PROGRAMS = {

    1: """Эта программа может стать началом нового этапа в вашей жизни, открывая двери к новым возможностям и росту.

Вероятность беременности может быть связана с вашей готовностью принимать изменения и новые начинания. Если вы испытываете страхи, неопределенность или сомнения, это нормально - многие проходят через такие чувства, но важно работать над этим, чтобы приблизить свою мечту, каждый шаг на этом пути может привести к долгожданному результату. С поддержкой и пониманием вы сможете преодолеть свои опасения и открыть себя для возможностей, которые могут привести к беременности.

Беременность, с точки зрения цифровой психологии, зависит не только от программы года, но и от проработки личных программ, а также от программ, которые рассчитываются на каждый месяц, день. Зная, как это проработать шансы на зачатие будут значительно выше.

Если вы готовы поработать над собой более детальнее, предлагаю расчет, где будут также рассчитаны месяца для благоприятного и возможного зачатия. В этом расчете будут рекомендации, направленные на проработку женского начала, которые увеличат ваши шансы на беременность.

Это не волшебство и не магия, но это то, что может приблизить Вас к заветной мечте.""",

    2: """Беременность

В том году у вас открывается уникальная возможность, которая может привести к беременности. Это время символизирует создание новой жизни и объединение, наполненное энергией любви и семейных ценностей. Программа, которую вы будете проходить, обладает мощной и чувственной атмосферой, способствующей раскрытию вашего внутреннего женского начала.

Ключевым аспектом данной программы является умение находить компромиссы с вашим партнером. Это включает в себя активное слушание и взаимопонимание, а также важность открытого общения. Необходимо делиться своими обидами и недопониманиями, быть искренними как с собой, так и с вашим близким человеком. Эти практики помогут вам не только укрепить вашу связь, но и создать необходимую эмоциональную основу для осуществления вашей мечты — беременности.

Беременность, с точки зрения цифровой психологии, зависит не только от программы года, но и от проработки личных программ, а также от программ, которые рассчитываются на каждый месяц, день. Зная, как это проработать шансы на зачатие будут значительно выше.

Если вы готовы поработать над собой более детальнее, предлагаю расчет, где будут также рассчитаны месяца для благоприятного и возможного зачатия. В этом расчете будут рекомендации, направленные на проработку женского начала, которые увеличат ваши шансы на беременность.

Это не волшебство и не магия, но это то, что может приблизить Вас к заветной мечте.""",

    3: """Потенциал данной программы в вопросе беременности очень высокий, вам остается по максимум следить за своим эмоциональным состоянием, здоровьем.

Ключевым аспектом данной программы является то, чтобы вы не боялись проявлений в обществе, не боялись своих желаний и ставили их на 1 место. Сначала забота о себе, чтобы достичь максимальной внутренней гармонии.

Беременность, с точки зрения цифровой психологии, зависит не только от программы года, но и от проработки личных программ, а также от программ, которые рассчитываются на каждый месяц, день. Зная, как это проработать шансы на зачатие будут значительно выше.

Если вы готовы поработать над собой более детальнее, предлагаю расчет, где будут также рассчитаны месяца для благоприятного и возможного зачатия. В этом расчете будут рекомендации, направленные на проработку женского начала, которые увеличат ваши шансы на беременность.

Это не волшебство и не магия, но это то, что может приблизить Вас к заветной мечте.""",

    4: """Ваша программа на этот год наполнена выраженной мужской энергией. Вероятность зачатия может вырасти, когда вы научитесь управлять этой энергией, трансформируя её в более женственную, гибкую и нежную. Важно, чтобы мужская энергия, с её ответственностью и строгостью, проявлялась только в профессиональной сфере и бизнесе, в то время как дома следует от неё освобождаться.

Чрезмерный контроль может стать препятствием на пути к зачатиям, как и многие другие упомянутые мною факторы.

Беременность, с точки зрения цифровой психологии, зависит не только от программы года, но и от проработки личных программ, а также от программ, которые рассчитываются на каждый месяц, день. Зная, как это проработать шансы на зачатие будут значительно выше.

Если вы готовы поработать над собой более детальнее, предлагаю расчет, где будут также рассчитаны месяца для благоприятного и возможного зачатия. В этом расчете будут рекомендации, направленные на проработку женского начала, которые увеличат ваши шансы на беременность.

Это не волшебство и не магия, но это то, что может приблизить Вас к заветной мечте.""",

    5: """Данная программа имеет шанс на зачатие и не редко это случается у тех, кто ждет 3 ребенка, то есть меняется статус – МНОГОДЕТНАЯ СЕМЬЯ. Но и статус для девушки – стать МАМОЙ впервые имеет место быть.

Ключевым аспектом данной программы является необходимость исследовать новые горизонты. Беременность может быть частью этого процесса, однако важно осознать, с какой целью вы стремитесь к этой цели. Это вызвано интересом и желанием «приключений» или же связано с семейными ценностями, имеющими для вас главное значение? Ваш ответ на этот вопрос окажет существенное влияние на дальнейшие шаги.

Беременность, с точки зрения цифровой психологии, зависит не только от программы года, но и от проработки личных программ, а также от программ, которые рассчитываются на каждый месяц, день. Зная, как это проработать шансы на зачатие будут значительно выше.

Если вы готовы поработать над собой более детальнее, предлагаю расчет, где будут также рассчитаны месяца для благоприятного и возможного зачатия. В этом расчете будут рекомендации, направленные на проработку женского начала, которые увеличат ваши шансы на беременность.

Это не волшебство и не магия, но это то, что может приблизить Вас к заветной мечте.""",

    6: """Одна из не многих программ, которая способствует и подталкивает вас к беременности. В этом году есть все шансы воплотить свою мечту – стать мамой.

Важным аспектом данной программы является умением выбирать и любить себя, заботиться и ни в коем случае не предавать свои ценности. Прислушиваться к своей интуиции и научиться делать выбор, так как чувствуете вы.

Беременность, с точки зрения цифровой психологии, зависит не только от программы года, но и от проработки личных программ, а также от программ, которые рассчитываются на каждый месяц, день. Зная, как это проработать шансы на зачатие будут значительно выше.

Если вы готовы поработать над собой более детальнее, предлагаю расчет, где будут также рассчитаны месяца для благоприятного и возможного зачатия. В этом расчете будут рекомендации, направленные на проработку женского начала, которые увеличат ваши шансы на беременность.

Это не волшебство и не магия, но это то, что может приблизить Вас к заветной мечте.""",

    7: """Данная программа имеет шансы на зачатие и рождение ребенка, но не большие. Для этой энергии важно не сдаваться, не возвращаться в прошлое, а искать новые пути решения. Застой и не желание, что-то предпринимать будет усугублять данный процесс. Также в этом году нельзя опрометчиво относиться к своему здоровью, нужно проверить досконально организм, а также соблюдать режим сна, питания и обязательно внедрять спорт. Только активные действия могут привести к результату.

Беременность, с точки зрения цифровой психологии, зависит не только от программы года, но и от проработки личных программ, а также от программ, которые рассчитываются на каждый месяц, день. Зная, как это проработать шансы на зачатие будут значительно выше.

Если вы готовы поработать над собой более детальнее, предлагаю расчет, где будут также рассчитаны месяца для благоприятного и возможного зачатия. В этом расчете будут рекомендации, направленные на проработку женского начала, которые увеличат ваши шансы на беременность.

Это не волшебство и не магия, но это то, что может приблизить Вас к заветной мечте.""",

    8: """Беременность в данную программу возможна, но, как и другие энергии, которые не направлены напрямую на зачатие, здесь есть свои нюансы.

Важным аспектом данной программы является то, насколько вы честны с собой, с партнером, насколько у вас есть доверие к людям и к жизни в целом. Ищите ли вы везде справедливость или понимаете, что каждая ситуация дана вам для того, чтобы вы извлекали уроки. Масштаб данной программы может подразумевать беременность, но так как она больше направлена на личный рост и карьеру, то здесь важно не зацикливаться на материальном, а направить эту мощь на построение в первую очередь доверительных отношений с партнером. И задаться вопросом, что вы хотите сейчас больше КАРЬЕРУ ИЛИ ДЕТЕЙ.

Беременность, с точки зрения цифровой психологии, зависит не только от программы года, но и от проработки личных программ, а также от программ, которые рассчитываются на каждый месяц, день. Зная, как это проработать шансы на зачатие будут значительно выше.

Если вы готовы поработать над собой более детальнее, предлагаю расчет, где будут также рассчитаны месяца для благоприятного и возможного зачатия. В этом расчете будут рекомендации, направленные на проработку женского начала, которые увеличат ваши шансы на беременность.

Это не волшебство и не магия, но это то, что может приблизить Вас к заветной мечте.""",

    9: """Одна из не многих программ, которая направлена на зачатие и рождение. В этом году высокие шансы поменять статус в обществе и стать мамой (беременной). Но есть определенные аспекты, с которыми нужно поработать. Самая главная проработка – это вы и ваши мысли. Очень часто в данную программу проявляются все наши страхи, недоверие к близким, что может помешать наступлению беременности. Сам процесс зачатия требует много энергии, сил и если все это будет уходить на ваши проблемы в голове, то ваша мечта может остаться только мечтой.

Беременность, с точки зрения цифровой психологии, зависит не только от программы года, но и от проработки личных программ, а также от программ, которые рассчитываются на каждый месяц, день. Зная, как это проработать шансы на зачатие будут значительно выше.

Если вы готовы поработать над собой более детальнее, предлагаю расчет, где будут также рассчитаны месяца для благоприятного и возможного зачатия. В этом расчете будут рекомендации, направленные на проработку женского начала, которые увеличат ваши шансы на беременность.

Это не волшебство и не магия, но это то, что может приблизить Вас к заветной мечте."""
}


# =========================================================
# КЛАВИАТУРЫ
# =========================================================

confirm_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="✅ Да, всё верно"),
            KeyboardButton(text="✏️ Изменить дату")
        ]
    ],
    resize_keyboard=True
)

interest_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Мне интересно")]
    ],
    resize_keyboard=True
)

choice_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🇷🇺 Для СНГ")],
        [KeyboardButton(text="🌍 Для других стран")],
        [KeyboardButton(text="💬 Отзывы")],
        [KeyboardButton(text="📋 Правила работы и оплат")]
    ],
    resize_keyboard=True
)

cis_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💰 Базовый расчёт — 600 ₽")],
        [KeyboardButton(text="💎 Расширенный расчёт — 1200 ₽")],
        [KeyboardButton(text="⬅️ Назад")]
    ],
    resize_keyboard=True
)

rules_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="⬅️ Назад")]
    ],
    resize_keyboard=True
)

international_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="⬅️ Назад")]
    ],
    resize_keyboard=True
)

reviews_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="⬅️ Назад")]
    ],
    resize_keyboard=True
)


# =========================================================
# ВРЕМЕННЫЕ ДАННЫЕ
# =========================================================

user_dates = {}
user_programs = {}


# =========================================================
# ВИДЕО
# =========================================================

BASIC_VIDEO_ID = (
    "BAACAgIAAxkBAAICAAFqwRoh3xaYzVVuIAOQqjRXklVO9gACVKkAAg_mCEpLy3o6FIo3XT0E"
)

EXTENDED_VIDEO_ID = (
    "BAACAgIAAxkBAAICAmrBGl4eqAWB1G9HxtXUJS2xHE0KAAJZqQACD-YISu1xywOAsDQWPQQ"
)


# =========================================================
# ОТЗЫВЫ
# =========================================================

REVIEW_PHOTOS = [
    "AgACAgIAAxkBAAPkarkPtzE-1hAfeK54AicygyObHdkAAsEkaxu6xslJgtxTQaSwSqQBAAMCAAN4AAM9BA",
    "AgACAgIAAxkBAAPyarkSN5OA_hCJc0e5q0jc9G22u04AAgolaxu6xslJe6hManT9vEkBAAMCAAN4AAM9BA",
    "AgACAgIAAxkBAAP0arkSVvd837EVClZNSM_IHYD4spkAAgslaxu6xslJCYO0xpO7rnEBAAMCAAN4AAM9BA",
    "AgACAgIAAxkBAAP2arkSc-zpF9xNWgfnye2fg2vNNQYAAg0laxu6xslJ0ldj7f1Qu_EBAAMCAAN4AAM9BA",
    "AgACAgIAAxkBAAP4arkSln87uecbNTfnQkE7dnX9nUgAAg8laxu6xslJnvODR2fvw9YBAAMCAAN5AAM9BA",
    "AgACAgIAAxkBAAP6arkSxFZikxIe3J3KwrHRm7uOONUAAhAlaxu6xslJH5jEHormt3EBAAMCAAN5AAM9BA",
    "AgACAgIAAxkBAAP8arkS2bUMQ-DeGVnJpkbYxwiZZYAAAhElaxu6xslJJczvHWLLrdcBAAMCAAN4AAM9BA",
    "AgACAgIAAxkBAAP-arkS6tju-U0vmDsYYTIjZW_UfhQAAhIlaxu6xslJdOLTJI0gfu4BAAMCAAN5AAM9BA",
    "AgACAgIAAxkBAAIBAAFquRMF7lU7QEYWZvU05mi_7TeFWQACEyVrG7rGyUn-915APGHdSwEAAwIAA3kAAz0E",
    "AgACAgIAAxkBAAIBAmq5ExOdptL3WNzWCow1XiL5SFm4AAIUJWsbusbJSXNCH0tB9FIEAQADAgADeQADPQQ"
]


# =========================================================
# РАСЧЁТ ПРОГРАММЫ
# =========================================================

def calculate_program(date_text: str) -> int:

    date = datetime.strptime(
        date_text,
        "%d.%m.%Y"
    )

    result = date.day + date.month
    result += 11

    while result > 9:
        result = sum(
            int(digit)
            for digit in str(result)
        )

    return result


# =========================================================
# ТАРИФЫ
# =========================================================

async def show_tariffs(message: types.Message):

    await message.answer(
        "<b>Базовый расчёт — 600 ₽</b>\n\n"
        "✅ Личный прогноз на 2027 и 2028 год + рекомендации\n"
        "✅ Расчёты по месяцам на 2 года для благоприятного "
        "и возможного зачатия\n"
        "✅ 9 основных рекомендаций на проработку\n\n"

        "<b>Расширенный расчёт — 1200 ₽</b>\n\n"
        "✅ Личный прогноз на 2027, 2028, 2029 + рекомендации\n"
        "✅ Расчёты по месяцам на 3 года\n"
        "✅ 16 рекомендаций главных энергий, отвечающих "
        "за женское начало и беременность\n"
        "✅ Пример аскезы — как её писать\n"
        "✅ Готовые аффирмации — как они действуют и через какой срок\n"
        "✅ Признаки заблокированной 1 и 2 чакры\n"
        "✅ Рекомендации для проработки 1 и 2 чакры\n"
        "✅ Энергетические акценты месяца — когда и что практиковать",
        parse_mode="HTML"
    )

    await message.answer(
        "💬 <b>Помогу выбрать тебе расчёт.</b>\n\n"
        "Посмотри короткие видео ниже 👇",
        parse_mode="HTML"
    )

    await message.answer_video(
        video=BASIC_VIDEO_ID,
        caption="<b>💳 Базовый расчёт — 600 ₽</b>",
        parse_mode="HTML"
    )

    await message.answer_video(
        video=EXTENDED_VIDEO_ID,
        caption="<b>💳 Расширенный расчёт — 1200 ₽</b>",
        parse_mode="HTML"
    )

    await message.answer(
        "<b>Перед выбором подходящего для Вас расчёта, "
        "обязательно ознакомьтесь с «Правилами работы и оплат».</b>\n\n"
        "Выбери подходящий вариант:",
        parse_mode="HTML",
        reply_markup=choice_keyboard
    )


# =========================================================
# ЭКРАН СНГ
# =========================================================

async def show_cis_payment(message: types.Message):

    await message.answer(
        "🇷🇺 <b>Оплата для СНГ</b>\n\n"
        "Выбери подходящий расчёт:",
        parse_mode="HTML",
        reply_markup=cis_keyboard
    )


# =========================================================
# МЕЖДУНАРОДНАЯ ОПЛАТА
# =========================================================

async def show_international_payment(message: types.Message):

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🌍 Перейти к оплате",
                    url=INTERNATIONAL_PAYMENT_URL
                )
            ]
        ]
    )

    await message.answer(
        "🌍 <b>Оплата для других стран</b>\n\n"
        "Для оплаты перейдите по кнопке ниже 👇",
        parse_mode="HTML",
        reply_markup=keyboard
    )

    await message.answer(
        "После оплаты ознакомьтесь с правилами работы "
        "и отправьте необходимые данные.",
        reply_markup=international_keyboard
    )


# =========================================================
# ПРАВИЛА
# =========================================================

async def show_rules(message: types.Message):

    await message.answer(
        "<b>💳 Оплата</b>\n\n"
        "• Россия и страны СНГ: выбирайте любой из доступных "
        "способов оплаты.\n"
        "• Другие страны: действует отдельная система оплаты, "
        "выбирайте нужный вариант.\n\n"

        "<b>📩 Что нужно для расчёта</b>\n\n"
        "Пришлите в личные сообщения по ссылке:\n"
        f"{PERSONAL_MESSAGES_URL}\n\n"
        "такие данные:\n"
        "1. Имя и дата рождения.\n"
        "2. Скриншот чека/подтверждения оплаты.\n\n"

        "<b>⏰ Сроки готовности</b>\n\n"
        "Срок зависит от времени поступления оплаты (МСК):\n\n"
        "• До 20:00 — расчёт будет готов в тот же день до 23:00.\n"
        "• После 20:00 — расчёт будет готов на следующий день до 23:00.",
        parse_mode="HTML",
        reply_markup=rules_keyboard
    )


# =========================================================
# УВЕДОМЛЕНИЕ КАТЕ
# =========================================================

async def notify_katya(
    message: types.Message,
    tariff_name: str,
    amount: str
):

    if not KATYA_CHAT_ID:
        print("KATYA_CHAT_ID не задан.")
        return

    username = (
        f"@{message.from_user.username}"
        if message.from_user.username
        else "не указан"
    )

    date_text = datetime.now().strftime(
        "%d.%m.%Y %H:%M:%S"
    )

    try:

        await bot.send_message(
            chat_id=KATYA_CHAT_ID,
            text=(
                "💰 <b>Новая оплата</b>\n\n"
                f"Тариф: <b>{tariff_name}</b>\n"
                f"Сумма: <b>{amount} ₽</b>\n"
                f"Пользователь: {username}\n"
                f"Telegram ID: <code>{message.from_user.id}</code>\n"
                f"Дата: {date_text}"
            ),
            parse_mode="HTML"
        )

        print("Уведомление Кате отправлено.")

    except Exception as e:

        print(
            f"Ошибка отправки уведомления Кате: {e}"
        )


# =========================================================
# ПРОВЕРКА ПЛАТЕЖА
# =========================================================

async def monitor_yookassa_payment(
    payment_id: str,
    message: types.Message,
    tariff_name: str,
    amount: str
):

    print(
        f"Начата проверка платежа: "
        f"{payment_id} | {tariff_name} | {amount} ₽"
    )

    try:

        for _ in range(180):

            await asyncio.sleep(5)

            try:

                payment = await asyncio.wait_for(
                    asyncio.to_thread(
                        Payment.find_one,
                        payment_id
                    ),
                    timeout=30
                )

                status = payment.status

                print(
                    f"Платёж {payment_id}: {status}"
                )

                if status == "succeeded":

                    await message.answer(
                        "🎉 <b>Оплата прошла успешно!</b>\n\n"
                        "Спасибо за покупку ❤️\n\n"
                        f"<b>{tariff_name}</b> оплачен.\n\n"
                        "Теперь отправь Кате в личные сообщения:\n"
                        "1. Имя\n"
                        "2. Дату рождения\n\n"
                        "И обязательно сохрани подтверждение оплаты.",
                        parse_mode="HTML",
                        reply_markup=InlineKeyboardMarkup(
                            inline_keyboard=[
                                [
                                    InlineKeyboardButton(
                                        text="📩 Написать Кате",
                                        url=PERSONAL_MESSAGES_URL
                                    )
                                ]
                            ]
                        )
                    )

                    await notify_katya(
                        message=message,
                        tariff_name=tariff_name,
                        amount=amount
                    )

                    print(
                        f"Платёж успешно завершён: {payment_id}"
                    )

                    return

                if status in (
                    "canceled",
                    "cancelled"
                ):

                    await message.answer(
                        "❌ Платёж не был завершён.\n\n"
                        "Если хочешь попробовать ещё раз, "
                        "выбери тариф повторно."
                    )

                    return

            except Exception as e:

                print(
                    f"Ошибка проверки платежа "
                    f"{payment_id}: {e}"
                )

    finally:

        payment_in_progress.discard(
            message.from_user.id
        )


# =========================================================
# СОЗДАНИЕ ПЛАТЕЖА ЮKASSA
# =========================================================

async def create_yookassa_payment(
    message: types.Message,
    amount: str,
    description: str,
    tariff_name: str
):

    user_id = message.from_user.id

    if user_id in payment_in_progress:

        await message.answer(
            "⏳ Платёж уже создаётся.\n\n"
            "Подожди несколько секунд."
        )

        return

    payment_in_progress.add(user_id)

    print(
        f">>> Начинаем создание платежа: "
        f"{tariff_name} | {amount} ₽ | user={user_id}"
    )

    try:

        payment_data = {
            "amount": {
                "value": amount,
                "currency": "RUB"
            },

            "capture": True,

            "confirmation": {
                "type": "redirect",
                "return_url": "https://t.me/Karizskaya_k_bot"
            },

            "description": description,

            "metadata": {
                "telegram_user_id": str(user_id),
                "telegram_username": (
                    message.from_user.username or ""
                ),
                "tariff": tariff_name
            }
        }

        print(">>> Отправляем запрос в YooKassa...")

        payment = await asyncio.wait_for(
            asyncio.to_thread(
                Payment.create,
                payment_data,
                str(uuid.uuid4())
            ),
            timeout=30
        )

        print(
            f">>> YooKassa ответила. "
            f"payment_id={payment.id}"
        )

        confirmation = payment.confirmation

        if not confirmation:
            raise RuntimeError(
                "YooKassa не вернула confirmation"
            )

        confirmation_url = (
            confirmation.confirmation_url
        )

        if not confirmation_url:
            raise RuntimeError(
                "YooKassa не вернула confirmation_url"
            )

        payment_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=f"💳 Оплатить {amount} ₽",
                        url=confirmation_url
                    )
                ]
            ]
        )

        await message.answer(
            f"💳 <b>{tariff_name}</b>\n\n"
            f"Сумма: <b>{amount} ₽</b>\n\n"
            "Нажми кнопку ниже для перехода к оплате 👇\n\n"
            "На странице ЮKassa выбери удобный "
            "способ оплаты.",
            parse_mode="HTML",
            reply_markup=payment_keyboard
        )

        print(
            f">>> Платёж создан: "
            f"{payment.id} | {tariff_name} | {amount} ₽"
        )

        asyncio.create_task(
            monitor_yookassa_payment(
                payment_id=payment.id,
                message=message,
                tariff_name=tariff_name,
                amount=amount
            )
        )

        payment_in_progress.discard(user_id)

    except asyncio.TimeoutError:

        payment_in_progress.discard(user_id)

        print(
            "!!! YooKassa не ответила за 30 секунд"
        )

        await message.answer(
            "❌ YooKassa не ответила вовремя.\n\n"
            "Попробуй ещё раз через несколько секунд."
        )

    except Exception as e:

        payment_in_progress.discard(user_id)

        print(
            f"!!! Ошибка создания платежа YooKassa: "
            f"{type(e).__name__}: {e}"
        )

        await message.answer(
            "❌ Не удалось создать платёж.\n\n"
            "Попробуй ещё раз через несколько секунд."
        )


# =========================================================
# /START
# =========================================================

@dp.message(CommandStart())
async def start_handler(message: types.Message):

    print(
        f"CHAT_ID: {message.chat.id}"
    )

    # Отправляем приветственную картинку
    image_path = os.path.join(
        os.path.dirname(__file__),
        "images",
        "welcome.png"
    )

    await message.answer_photo(
        photo=types.FSInputFile(image_path)
    )

    # Отправляем приветствие
    await message.answer(
        "Привет! ❤️\n\n"
        "Я помогу тебе получить персональную перспективу "
        "беременности на 2027 год 🤰🏻\n\n"
        "Чтобы получить информацию, укажи свою дату рождения.\n\n"
        "Напиши её строго в формате: ДД.ММ.ГГГГ\n\n"
        "Например: 12.11.1992"
    )


# =========================================================
# ИЗМЕНИТЬ ДАТУ
# =========================================================

@dp.message(F.text == "✏️ Изменить дату")
async def edit_date_handler(message: types.Message):

    await message.answer(
        "Хорошо 🌸\n\n"
        "Напиши дату рождения ещё раз.\n\n"
        "Формат: ДД.ММ.ГГГГ\n"
        "Например: 22.04.1996"
    )


# =========================================================
# ПОДТВЕРЖДЕНИЕ ДАТЫ
# =========================================================

@dp.message(F.text == "✅ Да, всё верно")
async def confirm_date_handler(message: types.Message):

    user_id = message.from_user.id

    if user_id not in user_dates:

        await message.answer(
            "Давай начнём сначала 🌸\n\n"
            "Напиши свою дату рождения "
            "в формате ДД.ММ.ГГГГ."
        )

        return

    date_text = user_dates[user_id]

    program = calculate_program(
        date_text
    )

    user_programs[user_id] = program

    await message.answer(
        f"<b>Твоя программа — № {program}</b>\n\n"
        f"{PROGRAMS[program]}",
        parse_mode="HTML"
    )

    await message.answer(
        "🌸 <b>Если тебе интересно узнать более подробно "
        "о расчёте —\n"
        "нажимай кнопку ниже. 👇</b> 🌸",
        parse_mode="HTML",
        reply_markup=interest_keyboard
    )


# =========================================================
# ТЕСТ УВЕДОМЛЕНИЙ КАТЕ
# =========================================================

@dp.message(F.text == "/test_katya")
async def test_katya_handler(message: types.Message):

    print(
        f"KATYA_CHAT_ID = {KATYA_CHAT_ID}"
    )

    try:

        await bot.send_message(
            chat_id=KATYA_CHAT_ID,
            text=(
                "🧪 <b>Тестовое сообщение</b>\n\n"
                "Бот успешно подключил уведомления "
                "для Кати ❤️"
            ),
            parse_mode="HTML"
        )

        await message.answer(
            "✅ Тестовое сообщение отправлено Кате."
        )

    except Exception as e:

        print(
            f"Ошибка отправки сообщения Кате: {e}"
        )

        await message.answer(
            "❌ Не удалось отправить сообщение Кате.\n\n"
            "Подробность ошибки смотри в CMD."
        )


# =========================================================
# КНОПКА «МНЕ ИНТЕРЕСНО»
# =========================================================

@dp.message(F.text == "Мне интересно")
async def interest_handler(message: types.Message):

    print("Нажата кнопка: Мне интересно")

    await show_tariffs(message)


# =========================================================
# КНОПКА «ДЛЯ СНГ»
# =========================================================

@dp.message(F.text == "🇷🇺 Для СНГ")
async def cis_handler(message: types.Message):

    print("Нажата кнопка: Для СНГ")

    await show_cis_payment(message)


# =========================================================
# КНОПКА «ДРУГИЕ СТРАНЫ»
# =========================================================

@dp.message(F.text == "🌍 Для других стран")
async def international_handler(message: types.Message):

    print("Нажата кнопка: Для других стран")

    await show_international_payment(message)


# =========================================================
# КНОПКА «ПРАВИЛА»
# =========================================================

@dp.message(F.text == "📋 Правила работы и оплат")
async def rules_handler(message: types.Message):

    print("Нажата кнопка: Правила")

    await show_rules(message)


# =========================================================
# КНОПКА «ОТЗЫВЫ»
# =========================================================

@dp.message(F.text == "💬 Отзывы")
async def reviews_handler(message: types.Message):

    print("Нажата кнопка: Отзывы")

    await message.answer(
        "❤️ <b>Отзывы девушек</b>\n\n"
        "Спасибо каждой, кто поделился своими "
        "впечатлениями 🌸",
        parse_mode="HTML",
        reply_markup=reviews_keyboard
    )

    for photo_id in REVIEW_PHOTOS:

        await message.answer_photo(
            photo=photo_id
        )


# =========================================================
# КНОПКА «НАЗАД»
# =========================================================

@dp.message(F.text == "⬅️ Назад")
async def back_handler(message: types.Message):

    print("Нажата кнопка: Назад")

    await show_tariffs(message)


# =========================================================
# БАЗОВЫЙ ТАРИФ
# =========================================================

@dp.message(F.text == "💰 Базовый расчёт — 600 ₽")
async def basic_payment_handler(message: types.Message):

    print(
        ">>> Нажата кнопка: "
        "Базовый расчёт — 600 ₽"
    )

    await create_yookassa_payment(
        message=message,
        amount="600.00",
        description=(
            "Персональный расчёт "
            "на 2027 и 2028 год"
        ),
        tariff_name="Базовый расчёт"
    )


# =========================================================
# РАСШИРЕННЫЙ ТАРИФ
# =========================================================

@dp.message(F.text == "💎 Расширенный расчёт — 1200 ₽")
async def extended_payment_handler(
    message: types.Message
):

    print(
        ">>> Нажата кнопка: "
        "Расширенный расчёт — 1200 ₽"
    )

    await create_yookassa_payment(
        message=message,
        amount="1200.00",
        description=(
            "Расширенный персональный расчёт "
            "на 2027, 2028 и 2029 год"
        ),
        tariff_name="Расширенный расчёт"
    )


# =========================================================
# ОСНОВНОЙ ОБРАБОТЧИК
# =========================================================

@dp.message()
async def message_handler(message: types.Message):

    if not message.text:
        return

    user_id = message.from_user.id

    if is_rate_limited(user_id):

        await message.answer(
            "⏳ Слишком много сообщений подряд.\n\n"
            "Подожди несколько секунд и продолжи 🌸"
        )

        return

    text = message.text.strip()

    print(
        f"Получен текст: {repr(text)}"
    )

    try:

        datetime.strptime(
            text,
            "%d.%m.%Y"
        )

    except ValueError:

        await message.answer(
            "Не совсем понял дату 🌸\n\n"
            "Пожалуйста, введи её в формате:\n"
            "ДД.ММ.ГГГГ\n\n"
            "Например: 22.04.1996"
        )

        return

    user_dates[user_id] = text

    await message.answer(
        f"Ты указала дату рождения:\n\n"
        f"🎂 {text}\n\n"
        f"Всё верно?",
        reply_markup=confirm_keyboard
    )


# =========================================================
# ЗАПУСК
# =========================================================

async def main():

    print("=" * 50)
    print("БОТ ЗАПУСКАЕТСЯ")
    print("=" * 50)
    print(
        f"YooKassa Shop ID: "
        f"{YOOKASSA_SHOP_ID}"
    )
    print(
        f"Katya Chat ID: "
        f"{KATYA_CHAT_ID}"
    )
    print("Бот запущен...")
    print("=" * 50)

    await dp.start_polling(bot)


if __name__ == "__main__":

    asyncio.run(main())
