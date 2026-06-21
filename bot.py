import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
import uuid
import time

(
    ASKING_AMOUNT,
    METHOD_SELECTION,
    CRYPTO_CHOICE,
    BLIK_WAIT_SCREEN,
    KRYPTO_WAIT_SCREEN,
    SETTING_PIN,
    CONFIRM_PIN,
    ADMIN_PHOTO_WAIT_ID,
    ADMIN_DESC_WAIT_TEXT,
) = range(9)

import os
DB_FILE = os.environ.get('DATABASE_PATH', 'bot_data.db')

ADMIN_ID = 8650119911

TEXTS = {
    "pl": {
        "start": (
            "Hej, <b>{name}</b>! 💎\n"
            "Widzę, że wjeżdżasz po konkretny temat i dobrą zabawę na wieczór! <b>Trafiłeś pod właściwy adres.</b>🪐\n\n"
            "<b>!! RODZAJE SKRYTEK !!</b>\n"
            "🧲 <b>- magnes</b> (skarb przyczepiony do metalowego elementu)\n"
            "🌆 <b>- miasto</b> (skarb na terenie miejskim)\n"
            "⛏️ <b>- wykop</b> (skarb zakopany pod ziemią)\n"
            "🌲 <b>- las</b> (skarb na terenie lasu lub terenu zielonego)\n\n"
            "🎁 <b>CASHBACK:</b> Za każdy zakup zgarniasz <b>bonus</b> na swoje wewnętrzne saldo!\n\n"
            "<b>🔥 Gotowy na zakupy?</b>\nMiasto -> Dzielnica -> Towar jest twój.\n👉 <i>Zaczynaj!</i>\n\n"
            "<b>Wybierz miasto i ładuj koszyk</b>👇"
        ),
        "btn_cities": "🏙MIASTA🏙",
        "btn_profile": "👤PROFIL👤",
        "btn_topup": "➕SALDO➕",
        "btn_help": "🛟POMOC🛟",
        "btn_settings": "⚙️USTAWIENIA⚙",
        "btn_back": "⬅️ Powrót",
        "cities_header": "🏙 <b>To co? Gdzie dziś działamy?</b>",
        "districts_header": "Wybierz dzielnicę:",
        "district_products": "<b>📍 {district} — {city}</b>\nWybierz interesujący Cię produkt:",
        "no_products": "🚫 Brak produktów w <b>{district}</b>.\nSprawdź ponownie później.",
        "profile": (
            "👤 <b>TWÓJ PROFIL:</b>\n\n"
            "💰 Saldo: <b>{balance:.2f} zł</b>\n"
            "🎁 Zniżka lojalnościowa: <b>{discount}%</b> ({invited}/5 osób)\n"
            "🛍 Ostatnie zakupy: <i>{history}</i>\n\n"
            "💸 <b>STATUS CASHBACK:</b> Aktywny"
        ),
        "btn_topup2": "💹 Doładuj saldo",
        "btn_invite": "👥 Zaproś znajomych (I zarabiaj!)",
        "btn_cashback": "💸 CASHBACK",
        "cashback_info": (
            "💎 <b>CASHBACK 5%</b>\n\n"
            "To proste: za każdy Twój udany zakup, automatycznie zwracamy Ci <b>5% wydanej kwoty</b> prosto na Twoje saldo w bocie.\n\n"
            "Przykład: Kupujesz skrytkę za 100 zł → 5 zł wraca na Twoje konto! 💸"
        ),
        "reflink": (
            "👥 <b>SYSTEM POLECEŃ</b>\n\n"
            "Zaproś znajomych, a Twoja zniżka wzrośnie o <b>2% za każdą osobę</b> (max 10% przy 5 osobach).\n\n"
            "Jak to działa?\n"
            "1. Kopiujesz swój link.\n"
            "2. Wysyłasz go znajomym.\n"
            "3. Gdy ktoś wejdzie z linku → zniżka rośnie automatycznie!\n\n"
            "Twój unikalny link:\n<code>{link}</code>"
        ),
        "product_view": (
            "🏷 <b>{name}</b>\n"
            "━━━━━━━━━━━━━━━━\n"
            "<i>{desc}</i>\n"
            "━━━━━━━━━━━━━━━━\n"
            "💵 <b>CENA:</b>  <code>{price:.2f} zł</code>\n\n"
        ),
        "no_desc": "Opis zostanie wkrótce dodany.",
        "btn_pay": "💳 OPŁAĆ TOWAR",
        "buy_success": (
            "🎉 <b>ZAKUP ZAKOŃCZONY SUKCESEM!</b>\n\n"
            "🛍 Towar: <b>{name}</b>\n"
            "💳 Pozostałe saldo: <b>{balance:.2f} zł</b>\n"
            "🎁 Cashback +{cashback:.2f} zł doliczony!\n\n"
            "🪐 <i>Skrytka aktywowana. Za chwilę otrzymasz szczegóły miejscówki!</i>"
        ),
        "btn_home": "⬅️ STRONA GŁÓWNA",
        "no_funds": "❌ Brak środków! Doładuj profil.",
        "buy_ok": "✅ Zakup udany!",
        "help_header": "🆘 <b>POTRZEBUJESZ POMOCY?</b>\nWybierz odpowiedni kanał kontaktu:",
        "settings_header": "⚙️ <b>USTAWIENIA</b>\nDostosuj bota pod siebie:",
        "btn_lang": "🌐 Zmiana języka",
        "btn_clear_history": "🧹 Wyczyść historię",
        "btn_notif_on": "🔔 Powiadomienia: WŁ",
        "btn_notif_off": "🔕 Powiadomienia: WYŁ",
        "btn_pin_set": "🔐 Ustaw PIN",
        "btn_pin_change": "🔑 Zmień PIN",
        "btn_pin_remove": "🔓 Usuń PIN",
        "pin_enter_new": "🔐 <b>Ustaw PIN do profilu</b>\n\nWpisz nowy PIN (4 cyfry):",
        "pin_confirm": "✅ Powtórz PIN aby potwierdzić:",
        "pin_mismatch": "❌ PINy się nie zgadzają! Zacznij od nowa.",
        "pin_set_ok": "✅ PIN ustawiony! Profil jest teraz chroniony.",
        "pin_removed": "🔓 PIN usunięty. Profil jest otwarty.",
        "pin_wrong": "❌ Błędny PIN! Spróbuj ponownie:",
        "pin_wrong_current": "❌ Błędny aktualny PIN!",
        "pin_enter_current": "🔐 Wpisz aktualny PIN aby go usunąć:",
        "pin_prompt": "🔐 <b>Podaj PIN do profilu:</b>",
        "pin_invalid": "❌ PIN musi mieć dokładnie 4 cyfry!",
        "lang_header": "🌐 <b>Wybierz język / Select language:</b>",
        "lang_changed_pl": "✅ Język zmieniony na: <b>Polski 🇵🇱</b>",
        "lang_changed_en": "✅ Language changed to: <b>English 🇬🇧</b>",
        "lang_changed_ua": "✅ Мову змінено на: <b>Українська 🇺🇦</b>",
        "lang_changed_ru": "✅ Язык изменён на: <b>Русский 🇷🇺</b>",
        "history_cleared": "⚙️ <b>USTAWIENIA</b>\n\n✨ <i>Historia zakupów wyczyszczona!</i>",
        "history_cleared_alert": "🧹 Historia wyczyszczona!",
        "notif_on": "🔔 Powiadomienia włączone!",
        "notif_off": "🔕 Powiadomienia wyłączone.",
        "fav_city_header": "📍 <b>Wybierz ulubione miasto:</b>\nBędziesz tam trafiać szybciej.",
        "fav_city_set": "📍 Ulubione miasto: <b>{city}</b>",
        "topup_amount": "💰 <b>DOŁADOWANIE SALDA</b>\n\nWpisz kwotę w złotówkach (np. <code>100</code>):",
        "topup_method": "Kwota: <b>{amount} PLN</b> ✅\n\nWybierz metodę płatności:",
        "btn_blik": "💳 BLIK (PRZELEW)",
        "btn_crypto": "🪙 KRYPTOWALUTY",
        "product_unavailable": "Produkt nie jest już dostępny.",
    },
    "en": {
        "start": (
            "Hey, <b>{name}</b>! 💎\n"
            "You came to the right place!🪐\n\n"
            "<b>!! DEADDROP TYPES !!</b>\n"
            "🧲 <b>- magnet</b> (attached to metal)\n"
            "🌆 <b>- city</b> (urban area)\n"
            "⛏️ <b>- dig</b> (buried underground)\n"
            "🌲 <b>- forest</b> (green area)\n\n"
            "🎁 <b>CASHBACK:</b> Earn bonus on every purchase!\n\n"
            "<b>🔥 Ready to shop?</b>\nCity -> District -> Fun night is yours.\n\n"
            "<b>Choose a city</b>👇"
        ),
        "btn_cities": "🏙CITIES🏙",
        "btn_profile": "👤PROFILE👤",
        "btn_topup": "➕BALANCE➕",
        "btn_help": "🛟HELP🛟",
        "btn_settings": "⚙️SETTINGS⚙",
        "btn_back": "⬅️ Back",
        "cities_header": "🏙 <b>What's our plan for today?</b>",
        "districts_header": "Choose a district:",
        "district_products": "<b>📍 {district} — {city}</b>\nChoose a product:",
        "no_products": "🚫 No products in <b>{district}</b>.\nCheck back later.",
        "profile": (
            "👤 <b>YOUR PROFILE:</b>\n\n"
            "💰 Balance: <b>{balance:.2f} PLN</b>\n"
            "🎁 Loyalty discount: <b>{discount}%</b> ({invited}/5 people)\n"
            "🛍 Recent purchases: <i>{history}</i>\n\n"
            "💸 <b>CASHBACK STATUS:</b> Active"
        ),
        "btn_topup2": "💹 Top up balance",
        "btn_invite": "👥 Invite friends (Earn!)",
        "btn_cashback": "💸 CASHBACK",
        "cashback_info": (
            "💎 <b>CASHBACK 5%</b>\n\n"
            "For every successful purchase, we return <b>5% of the amount</b> to your balance.\n\n"
            "Example: Buy for 100 PLN → 5 PLN back! 💸"
        ),
        "reflink": (
            "👥 <b>REFERRAL SYSTEM</b>\n\n"
            "Invite friends and your discount grows by <b>2% per person</b> (max 10%).\n\n"
            "Your unique link:\n<code>{link}</code>"
        ),
        "product_view": (
            "🏷 <b>{name}</b>\n"
            "━━━━━━━━━━━━━━━━\n"
            "<i>{desc}</i>\n"
            "━━━━━━━━━━━━━━━━\n"
            "💵 <b>PRICE:</b>  <code>{price:.2f} PLN</code>\n\n"
        ),
        "no_desc": "Description coming soon.",
        "btn_pay": "💳 PAY FOR ITEM",
        "buy_success": (
            "🎉 <b>PURCHASE SUCCESSFUL!</b>\n\n"
            "🛍 Item: <b>{name}</b>\n"
            "💳 Balance: <b>{balance:.2f} PLN</b>\n"
            "🎁 Cashback +{cashback:.2f} PLN!\n\n"
            "🪐 <i>Stash activated!</i>"
        ),
        "btn_home": "⬅️ HOME",
        "no_funds": "❌ Insufficient funds! Top up first.",
        "buy_ok": "✅ Purchase successful!",
        "help_header": "🆘 <b>NEED HELP?</b>\nChoose a contact channel:",
        "settings_header": "⚙️ <b>SETTINGS</b>\nCustomize the bot:",
        "btn_lang": "🌐 Change language",
        "btn_clear_history": "🧹 Clear history",
        "btn_notif_on": "🔔 Notifications: ON",
        "btn_notif_off": "🔕 Notifications: OFF",
        "btn_fav_city": "📍 Favorite city",
        "lang_header": "🌐 <b>Select language / Wybierz język:</b>",
        "lang_changed_pl": "✅ Język zmieniony na: <b>Polski 🇵🇱</b>",
        "lang_changed_en": "✅ Language changed to: <b>English 🇬🇧</b>",
        "lang_changed_ua": "✅ Мову змінено на: <b>Українська 🇺🇦</b>",
        "lang_changed_ru": "✅ Язык изменён на: <b>Русский 🇷🇺</b>",
        "history_cleared": "⚙️ <b>SETTINGS</b>\n\n✨ <i>History cleared!</i>",
        "history_cleared_alert": "🧹 History cleared!",
        "notif_on": "🔔 Notifications enabled!",
        "notif_off": "🔕 Notifications disabled.",
        "fav_city_header": "📍 <b>Choose your favorite city:</b>",
        "fav_city_set": "📍 Favorite city: <b>{city}</b>",
        "topup_amount": "💰 <b>TOP UP</b>\n\nEnter amount in PLN (e.g. <code>100</code>):",
        "topup_method": "Amount: <b>{amount} PLN</b> ✅\n\nChoose payment method:",
        "btn_blik": "💳 BLIK (TRANSFER)",
        "btn_crypto": "🪙 CRYPTOCURRENCY",
        "product_unavailable": "This product is no longer available.",
    },
    "ua": {
        "start": (
            "Привіт, <b>{name}</b>! 💎\n"
            "Ти потрапив куди треба!🪐\n\n"
            "<b>!! ТИПИ СХОВАНОК !!</b>\n"
            "🧲 <b>- магніт</b>\n🌆 <b>- місто</b>\n⛏️ <b>- розкопки</b>\n🌲 <b>- ліс</b>\n\n"
            "🎁 <b>КЕШБЕК:</b> Бонус за кожну покупку!\n\n"
            "<b>Обери місто:</b>👇"
        ),
        "btn_cities": "🏙 МІСТА",
        "btn_profile": "👤 ПРОФІЛЬ",
        "btn_topup": "➕ БАЛАНС",
        "btn_help": "🛟 ДОПОМОГА",
        "btn_settings": "⚙️ НАЛАШТУВАННЯ",
        "btn_back": "⬅️ Назад",
        "cities_header": "🏙 <b>Де сьогодні?</b>",
        "districts_header": "Оберіть район:",
        "district_products": "<b>📍 {district} — {city}</b>\nОберіть товар:",
        "no_products": "🚫 Немає товарів у <b>{district}</b>.",
        "profile": "👤 <b>ТВІЙ ПРОФІЛЬ:</b>\n\n💰 Баланс: <b>{balance:.2f} PLN</b>\n🎁 Знижка: <b>{discount}%</b> ({invited}/5)\n🛍 Останні покупки: <i>{history}</i>\n\n💸 <b>КЕШБЕК:</b> Активний",
        "btn_cashback": "💸 КЕШБЕК",
        "btn_invite": "👥 Запроси друзів!",
        "btn_topup2": "💹 Поповнити",
        "cashback_info": "💎 <b>КЕШБЕК 5%</b>\n\nЗа кожну покупку — 5% повертається на баланс! 💸",
        "reflink": "👥 <b>РЕФЕРАЛИ</b>\n\nЗапроси друзів — знижка +2% за кожного (макс 10%).\n\nТвоє посилання:\n<code>{link}</code>",
        "product_view": (
            "🏷 <b>{name}</b>\n"
            "━━━━━━━━━━━━━━━━\n"
            "📝 <b>ОПИС:</b>\n"
            "<i>{desc}</i>\n"
            "━━━━━━━━━━━━━━━━\n"
            "💵 <b>ЦІНА:</b>  <code>{price:.2f} PLN</code>\n\n"
            "🧲 <i>Тип схованки вказано в описі</i>"
        ),
        "no_desc": "Опис з'явиться незабаром.",
        "btn_pay": "💳 ОПЛАТИТИ",
        "buy_success": "🎉 <b>ПОКУПКУ ЗДІЙСНЕНО!</b>\n\n🛍 <b>{name}</b>\n💳 Баланс: <b>{balance:.2f} PLN</b>\n🎁 Кешбек +{cashback:.2f} PLN\n\n🪐 <i>Схованку активовано!</i>",
        "btn_home": "⬅️ ГОЛОВНА",
        "no_funds": "❌ Недостатньо коштів!",
        "buy_ok": "✅ Покупку здійснено!",
        "help_header": "🆘 <b>ДОПОМОГА</b>",
        "settings_header": "⚙️ <b>НАЛАШТУВАННЯ</b>",
        "btn_lang": "🌐 Мова",
        "btn_clear_history": "🧹 Очистити історію",
        "btn_notif_on": "🔔 Сповіщення: УВК",
        "btn_notif_off": "🔕 Сповіщення: ВИМК",
        "btn_fav_city": "📍 Улюблене місто",
        "lang_header": "🌐 <b>Оберіть мову:</b>",
        "lang_changed_pl": "✅ Język: <b>Polski 🇵🇱</b>",
        "lang_changed_en": "✅ Language: <b>English 🇬🇧</b>",
        "lang_changed_ua": "✅ Мова: <b>Українська 🇺🇦</b>",
        "lang_changed_ru": "✅ Язык: <b>Русский 🇷🇺</b>",
        "history_cleared": "⚙️ <b>НАЛАШТУВАННЯ</b>\n\n✨ <i>Історію очищено!</i>",
        "history_cleared_alert": "🧹 Історію очищено!",
        "notif_on": "🔔 Сповіщення увімкнено!",
        "notif_off": "🔕 Сповіщення вимкнено.",
        "fav_city_header": "📍 <b>Оберіть улюблене місто:</b>",
        "fav_city_set": "📍 Улюблене місто: <b>{city}</b>",
        "topup_amount": "💰 <b>ПОПОВНЕННЯ</b>\n\nВведіть суму в PLN:",
        "topup_method": "Сума: <b>{amount} PLN</b> ✅\n\nОберіть спосіб:",
        "btn_blik": "💳 BLIK",
        "btn_crypto": "🪙 КРИПТОВАЛЮТА",
        "product_unavailable": "Товар недоступний.",
    },
    "ru": {
        "start": (
            "Привет, <b>{name}</b>! 💎\n"
            "Ты попал по адресу!🪐\n\n"
            "<b>!! ТИПЫ СХРОНОВ !!</b>\n"
            "🧲 <b>- магнит</b>\n🌆 <b>- город</b>\n⛏️ <b>- раскопки</b>\n🌲 <b>- лес</b>\n\n"
            "🎁 <b>КЭШБЕК:</b> Бонус за каждую покупку!\n\n"
            "<b>Выбери город:</b>👇"
        ),
        "btn_cities": "🏙 ГОРОДА",
        "btn_profile": "👤 ПРОФИЛЬ",
        "btn_topup": "➕ БАЛАНС",
        "btn_help": "🛟 ПОМОЩЬ",
        "btn_settings": "⚙️ НАСТРОЙКИ",
        "btn_back": "⬅️ Назад",
        "cities_header": "🏙 <b>Где сегодня работаем?</b>",
        "districts_header": "Выберите район:",
        "district_products": "<b>📍 {district} — {city}</b>\nВыберите товар:",
        "no_products": "🚫 Нет товаров в <b>{district}</b>.",
        "profile": "👤 <b>ТВОЙ ПРОФИЛЬ:</b>\n\n💰 Баланс: <b>{balance:.2f} PLN</b>\n🎁 Скидка: <b>{discount}%</b> ({invited}/5)\n🛍 Последние покупки: <i>{history}</i>\n\n💸 <b>КЭШБЕК:</b> Активен",
        "btn_cashback": "💸 КЭШБЕК",
        "btn_invite": "👥 Пригласи друзей!",
        "btn_topup2": "💹 Пополнить",
        "cashback_info": "💎 <b>КЭШБЕК 5%</b>\n\nЗа каждую покупку — 5% возвращается на баланс! 💸",
        "reflink": "👥 <b>РЕФЕРАЛЫ</b>\n\nПриглашай друзей — скидка +2% за каждого (макс 10%).\n\nТвоя ссылка:\n<code>{link}</code>",
        "product_view": (
            "🏷 <b>{name}</b>\n"
            "━━━━━━━━━━━━━━━━\n"
            "📝 <b>ОПИСАНИЕ:</b>\n"
            "<i>{desc}</i>\n"
            "━━━━━━━━━━━━━━━━\n"
            "💵 <b>ЦЕНА:</b>  <code>{price:.2f} PLN</code>\n\n"
            "🧲 <i>Тип схрона указан в описании</i>"
        ),
        "no_desc": "Описание появится скоро.",
        "btn_pay": "💳 ОПЛАТИТЬ",
        "buy_success": "🎉 <b>ПОКУПКА УСПЕШНА!</b>\n\n🛍 <b>{name}</b>\n💳 Баланс: <b>{balance:.2f} PLN</b>\n🎁 Кэшбек +{cashback:.2f} PLN\n\n🪐 <i>Схрон активирован!</i>",
        "btn_home": "⬅️ ГЛАВНАЯ",
        "no_funds": "❌ Недостаточно средств!",
        "buy_ok": "✅ Покупка совершена!",
        "help_header": "🆘 <b>ПОМОЩЬ</b>",
        "settings_header": "⚙️ <b>НАСТРОЙКИ</b>",
        "btn_lang": "🌐 Язык",
        "btn_clear_history": "🧹 Очистить историю",
        "btn_notif_on": "🔔 Уведомления: ВКЛ",
        "btn_notif_off": "🔕 Уведомления: ВЫКЛ",
        "btn_fav_city": "📍 Любимый город",
        "lang_header": "🌐 <b>Выберите язык:</b>",
        "lang_changed_pl": "✅ Język: <b>Polski 🇵🇱</b>",
        "lang_changed_en": "✅ Language: <b>English 🇬🇧</b>",
        "lang_changed_ua": "✅ Мова: <b>Українська 🇺🇦</b>",
        "lang_changed_ru": "✅ Язык: <b>Русский 🇷🇺</b>",
        "history_cleared": "⚙️ <b>НАСТРОЙКИ</b>\n\n✨ <i>История очищена!</i>",
        "history_cleared_alert": "🧹 История очищена!",
        "notif_on": "🔔 Уведомления включены!",
        "notif_off": "🔕 Уведомления выключены.",
        "fav_city_header": "📍 <b>Выберите любимый город:</b>",
        "fav_city_set": "📍 Любимый город: <b>{city}</b>",
        "topup_amount": "💰 <b>ПОПОЛНЕНИЕ</b>\n\nВведите сумму в PLN:",
        "topup_method": "Сумма: <b>{amount} PLN</b> ✅\n\nВыберите способ:",
        "btn_blik": "💳 BLIK",
        "btn_crypto": "🪙 КРИПТОВАЛЮТА",
        "product_unavailable": "Товар недоступен.",
    },
}


def T(lang, key, **kwargs):
    text = TEXTS.get(lang, TEXTS["pl"]).get(key) or TEXTS["pl"].get(key, "")
    if kwargs:
        try:
            text = text.format(**kwargs)
        except Exception:
            pass
    return text


def get_config(key, default=""):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT value FROM config WHERE key=?", (key,))
        row = cursor.fetchone()
    except Exception:
        row = None
    conn.close()
    return row[0] if row else default


def set_config(key, value):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)", (key, value)
    )
    conn.commit()
    conn.close()


def get_all_config():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT key, value FROM config ORDER BY key")
        rows = cursor.fetchall()
    except Exception:
        rows = []
    conn.close()
    return rows


def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY, username TEXT, balance REAL DEFAULT 0.0,
        discount INTEGER DEFAULT 0, history TEXT DEFAULT '', friends_invited INTEGER DEFAULT 0,
        language TEXT DEFAULT 'pl', notifications INTEGER DEFAULT 1, fav_city TEXT DEFAULT NULL
    )""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, price REAL,
        city TEXT, district TEXT, description TEXT DEFAULT '', is_global INTEGER DEFAULT 0,
        photo_id TEXT DEFAULT NULL
    )""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS config (
        key TEXT PRIMARY KEY, value TEXT
    )""")
    for col, defn, tbl in [
        ("is_global", "INTEGER DEFAULT 0", "products"),
        ("photo_id", "TEXT DEFAULT NULL", "products"),
        ("friends_invited", "INTEGER DEFAULT 0", "users"),
        ("language", "TEXT DEFAULT 'pl'", "users"),
        ("notifications", "INTEGER DEFAULT 1", "users"),
        ("fav_city", "TEXT DEFAULT NULL", "users"),
    ]:
        try:
            cursor.execute(f"ALTER TABLE {tbl} ADD COLUMN {col} {defn}")
        except Exception:
            pass
    conn.commit()
    conn.close()


def add_user_if_not_exists(user_id, username):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,))
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO users (user_id, username, balance, discount, history, friends_invited, language, notifications) VALUES (?, ?, 0.0, 0, '', 0, 'pl', 1)",
            (user_id, username),
        )
        conn.commit()
    conn.close()


def get_user_data(user_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT balance, discount, history, friends_invited FROM users WHERE user_id = ?",
        (user_id,),
    )
    row = cursor.fetchone()
    conn.close()
    return row


def get_user_lang(user_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT language FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row and row[0] in TEXTS else "pl"


def set_user_lang(user_id, lang):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET language = ? WHERE user_id = ?", (lang, user_id))
    conn.commit()
    conn.close()


def get_user_notifications(user_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT notifications FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else 1


def toggle_notifications(user_id):
    current = get_user_notifications(user_id)
    new_val = 0 if current else 1
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET notifications = ? WHERE user_id = ?", (new_val, user_id)
    )
    conn.commit()
    conn.close()
    return new_val


def set_fav_city(user_id, city):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET fav_city = ? WHERE user_id = ?", (city, user_id))
    conn.commit()
    conn.close()


def get_user_pin(user_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT pin FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
    except Exception:
        row = None
    conn.close()
    return row[0] if row else None


def set_user_pin(user_id, pin):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET pin = ?, pin_attempts = 0 WHERE user_id = ?", (pin, user_id)
    )
    conn.commit()
    conn.close()


def remove_user_pin(user_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET pin = NULL, pin_attempts = 0 WHERE user_id = ?", (user_id,)
    )
    conn.commit()
    conn.close()


def get_all_user_ids():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users")
    rows = cursor.fetchall()
    conn.close()
    return [r[0] for r in rows]


def get_main_menu_keyboard(lang="pl"):
    return [
        [InlineKeyboardButton(T(lang, "btn_cities"), callback_data="miasta")],
        [
            InlineKeyboardButton(T(lang, "btn_profile"), callback_data="profil"),
            InlineKeyboardButton(T(lang, "btn_topup"), callback_data="doladuj"),
        ],
        [
            InlineKeyboardButton(T(lang, "btn_help"), callback_data="pomoc"),
            InlineKeyboardButton(T(lang, "btn_settings"), callback_data="ustawienia"),
        ],
    ]


async def edit_or_send(query, text, reply_markup, parse_mode="HTML"):
    try:
        if query.message.photo or query.message.document:
            await query.message.delete()
            await query.message.chat.send_message(
                text, reply_markup=reply_markup, parse_mode=parse_mode
            )
        else:
            await query.edit_message_text(
                text, reply_markup=reply_markup, parse_mode=parse_mode
            )
    except Exception as e:
        err = str(e).lower()
        if (
            "message to edit not found" in err
            or "message can't be edited" in err
            or "bad request" in err
        ):
            try:
                await query.message.chat.send_message(
                    text, reply_markup=reply_markup, parse_mode=parse_mode
                )
            except Exception:
                pass
        else:
            raise


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user_if_not_exists(user.id, user.username)
    lang = get_user_lang(user.id)
    text = T(lang, "start", name=user.first_name)
    kb = InlineKeyboardMarkup(get_main_menu_keyboard(lang))
    if update.message:
        await update.message.reply_text(text, reply_markup=kb, parse_mode="HTML")
    elif update.callback_query:
        await edit_or_send(update.callback_query, text, kb)


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    user = update.effective_user
    lang = get_user_lang(user.id)

    print(f"DEBUG: {data}")

    payment_callbacks = [
        "doladuj",
        "pay_blik",
        "pay_krypto",
        "back_to_amount",
        "check_blik_status",
        "cancel_order",
        "check_status",
        "back_to_methods",
    ]
    if data in payment_callbacks or data.startswith("krypto_"):
        return

    try:
        if data == "start":
            await query.answer()
            add_user_if_not_exists(user.id, user.username)
            lang = get_user_lang(user.id)
            text = T(lang, "start", name=user.first_name)
            await edit_or_send(
                query, text, InlineKeyboardMarkup(get_main_menu_keyboard(lang))
            )

        elif data == "profil":
            await query.answer()
            user_pin = get_user_pin(user.id)
            if user_pin and not context.user_data.get("pin_verified"):
                context.user_data["awaiting_pin"] = True
                context.user_data["pin_target"] = "profil"
                kb = [
                    [InlineKeyboardButton(T(lang, "btn_back"), callback_data="start")]
                ]
                await edit_or_send(
                    query, T(lang, "pin_prompt"), InlineKeyboardMarkup(kb)
                )
                return
            db_data = get_user_data(user.id)
            if db_data:
                saldo, znizka, historia, zaproszeni = db_data
            else:
                saldo, znizka, historia, zaproszeni = 0.0, 0, "—", 0
                add_user_if_not_exists(user.id, user.username)
            znizka = min(zaproszeni * 2, 10)
            if not historia:
                historia = "—"
            text = T(
                lang,
                "profile",
                balance=saldo,
                discount=znizka,
                invited=zaproszeni,
                history=historia,
            )
            kb = [
                [
                    InlineKeyboardButton(
                        T(lang, "btn_cashback"), callback_data="info_cashback"
                    )
                ],
                [InlineKeyboardButton(T(lang, "btn_invite"), callback_data="reflink")],
                [InlineKeyboardButton(T(lang, "btn_topup2"), callback_data="doladuj")],
                [InlineKeyboardButton(T(lang, "btn_back"), callback_data="start")],
            ]
            await edit_or_send(query, text, InlineKeyboardMarkup(kb))

        elif data == "info_cashback":
            await query.answer()
            kb = [[InlineKeyboardButton(T(lang, "btn_back"), callback_data="profil")]]
            await edit_or_send(
                query, T(lang, "cashback_info"), InlineKeyboardMarkup(kb)
            )

        elif data == "reflink":
            await query.answer()
            link = f"https://t.me/{context.bot.username}?start={user.id}"
            kb = [[InlineKeyboardButton(T(lang, "btn_back"), callback_data="profil")]]
            await edit_or_send(
                query, T(lang, "reflink", link=link), InlineKeyboardMarkup(kb)
            )

        elif data == "miasta":
            await query.answer()
            kb = [
                [InlineKeyboardButton("🦁 Gdańsk", callback_data="city_gdansk")],
                [InlineKeyboardButton("🎶 Sopot", callback_data="city_sopot")],
                [InlineKeyboardButton("⚓️ Gdynia", callback_data="city_gdynia")],
                [InlineKeyboardButton(T(lang, "btn_back"), callback_data="start")],
            ]
            await edit_or_send(
                query, T(lang, "cities_header"), InlineKeyboardMarkup(kb)
            )

        elif data == "city_gdansk":
            await query.answer()
            kb = [
                [
                    InlineKeyboardButton(
                        "🌇 Śródmieście", callback_data="dist_gdansk_śródmieście"
                    ),
                    InlineKeyboardButton(
                        "🪽 Aniołki", callback_data="dist_gdansk_aniołki"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "🫀 Siedlce", callback_data="dist_gdansk_siedlce"
                    ),
                    InlineKeyboardButton("🪖 Chełm", callback_data="dist_gdansk_chelm"),
                ],
                [
                    InlineKeyboardButton(
                        "🧱 Wrzeszcz", callback_data="dist_gdansk_wrzeszcz"
                    ),
                    InlineKeyboardButton(
                        "✨ Migowo", callback_data="dist_gdansk_migowo"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "🌊 Przymorze", callback_data="dist_gdansk_przymorze"
                    ),
                    InlineKeyboardButton("🫒 Oliwa", callback_data="dist_gdansk_oliwa"),
                ],
                [
                    InlineKeyboardButton(
                        "⚓️ Brzeźno", callback_data="dist_gdansk_brzeźno"
                    ),
                    InlineKeyboardButton("🌳 Stogi", callback_data="dist_gdansk_stogi"),
                ],
                [
                    InlineKeyboardButton(
                        "🚊 Łostowice", callback_data="dist_gdansk_łostowice"
                    ),
                    InlineKeyboardButton(
                        "🐗 Orunia", callback_data="dist_gdansk_orunia"
                    ),
                ],
                [InlineKeyboardButton(T(lang, "btn_back"), callback_data="miasta")],
            ]
            await edit_or_send(
                query, T(lang, "districts_header"), InlineKeyboardMarkup(kb)
            )

        elif data == "city_sopot":
            await query.answer()
            kb = [
                [
                    InlineKeyboardButton(
                        "💎 Dolny Sopot", callback_data="dist_sopot_dolny sopot"
                    ),
                    InlineKeyboardButton(
                        "🎈 Górny Sopot", callback_data="dist_sopot_górny sopot"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "☀️ Karlikowo", callback_data="dist_sopot_karlikowo"
                    ),
                    InlineKeyboardButton(
                        "🎡 Brodwino", callback_data="dist_sopot_brodwino"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "🪨 Kamienny Potok", callback_data="dist_sopot_kamienny potok"
                    ),
                    InlineKeyboardButton(
                        "🍏 Świemirowo", callback_data="dist_sopot_świemirowo"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "🦊 Przylesie", callback_data="dist_sopot_przylesie"
                    ),
                    InlineKeyboardButton(
                        "🏛 Centrum", callback_data="dist_sopot_centrum"
                    ),
                ],
                [InlineKeyboardButton(T(lang, "btn_back"), callback_data="miasta")],
            ]
            await edit_or_send(
                query, T(lang, "districts_header"), InlineKeyboardMarkup(kb)
            )

        elif data == "city_gdynia":
            await query.answer()
            kb = [
                [
                    InlineKeyboardButton(
                        "🏢 Śródmieście", callback_data="dist_gdynia_śródmieście"
                    ),
                    InlineKeyboardButton("🚢 Port", callback_data="dist_gdynia_port"),
                ],
                [
                    InlineKeyboardButton(
                        "⛱ Orłowo", callback_data="dist_gdynia_orłowo"
                    ),
                    InlineKeyboardButton(
                        "🌳 Redłowo", callback_data="dist_gdynia_redłowo"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "🎓 Witomino", callback_data="dist_gdynia_witomino"
                    ),
                    InlineKeyboardButton(
                        "⚡️ Chylonia", callback_data="dist_gdynia_chylonia"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "🔭 Wzgórze Św. M.",
                        callback_data="dist_gdynia_wzgórze św. maksymiliana",
                    ),
                    InlineKeyboardButton(
                        "🍓 Dąbrowa", callback_data="dist_gdynia_dąbrowa"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "🛫 Babie Doły", callback_data="dist_gdynia_babie doły"
                    ),
                    InlineKeyboardButton(
                        "🚧 Leszczynki", callback_data="dist_gdynia_leszczynki"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "🚲 Karwiny", callback_data="dist_gdynia_karwiny"
                    ),
                    InlineKeyboardButton(
                        "🎖 Oksywie", callback_data="dist_gdynia_oksywie"
                    ),
                ],
                [InlineKeyboardButton(T(lang, "btn_back"), callback_data="miasta")],
            ]
            await edit_or_send(
                query, T(lang, "districts_header"), InlineKeyboardMarkup(kb)
            )

        elif data.startswith("dist_"):
            await query.answer()
            parts = data.split("_", 2)
            miasto = parts[1]
            tekst_dzielnicy = parts[2]

            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, name, price FROM products WHERE is_global=1 "
                "UNION ALL "
                "SELECT id, name, price FROM products WHERE is_global=0 AND city=? AND district=?",
                (miasto, tekst_dzielnicy),
            )
            produkty = cursor.fetchall()
            conn.close()

            if not produkty:
                kb = [
                    [
                        InlineKeyboardButton(
                            T(lang, "btn_back"), callback_data=f"city_{miasto}"
                        )
                    ]
                ]
                await edit_or_send(
                    query,
                    T(lang, "no_products", district=tekst_dzielnicy),
                    InlineKeyboardMarkup(kb),
                )
                return

            kb = [
                [
                    InlineKeyboardButton(
                        f"{p[1]} — {p[2]:.0f} zł", callback_data=f"view_prod_{p[0]}"
                    )
                ]
                for p in produkty
            ]
            kb.append(
                [
                    InlineKeyboardButton(
                        T(lang, "btn_back"), callback_data=f"city_{miasto}"
                    )
                ]
            )
            await edit_or_send(
                query,
                T(
                    lang,
                    "district_products",
                    district=tekst_dzielnicy.upper(),
                    city=miasto.upper(),
                ),
                InlineKeyboardMarkup(kb),
            )

        elif data.startswith("view_prod_"):
            await query.answer()
            product_id = data.split("_")[2]

            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            product_name, price, description, city_val, district_val, photo_id = (
                None,
                0.0,
                "",
                None,
                None,
                None,
            )
            try:
                cursor.execute(
                    "SELECT name, price, description, city, district, photo_id FROM products WHERE id=?",
                    (product_id,),
                )
                row = cursor.fetchone()
                if row:
                    (
                        product_name,
                        price,
                        description,
                        city_val,
                        district_val,
                        photo_id,
                    ) = row
            except sqlite3.OperationalError:
                cursor.execute(
                    "SELECT name, price FROM products WHERE id=?", (product_id,)
                )
                row = cursor.fetchone()
                if row:
                    product_name, price = row
            conn.close()

            if product_name:
                if not description:
                    description = T(lang, "no_desc")
                caption = T(
                    lang,
                    "product_view",
                    name=product_name,
                    desc=description,
                    price=price,
                )
                back_target = (
                    f"dist_{city_val}_{district_val}"
                    if (city_val and district_val)
                    else "miasta"
                )
                kb = InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                T(lang, "btn_pay"),
                                callback_data=f"pay_prod_{product_id}",
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                T(lang, "btn_back"), callback_data=back_target
                            )
                        ],
                    ]
                )

                if photo_id:
                    if query.message.photo:
                        await query.edit_message_media(
                            InputMediaPhoto(
                                photo_id, caption=caption, parse_mode="HTML"
                            ),
                            reply_markup=kb,
                        )
                    else:
                        await query.message.delete()
                        await query.message.chat.send_photo(
                            photo_id,
                            caption=caption,
                            reply_markup=kb,
                            parse_mode="HTML",
                        )
                else:
                    await edit_or_send(query, caption, kb)
            else:
                await query.answer(T(lang, "product_unavailable"), show_alert=True)

        elif data.startswith("pay_prod_"):
            product_id = data.split("_")[2]
            user_id = query.from_user.id

            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "SELECT name, price FROM products WHERE id=?", (product_id,)
                )
                product = cursor.fetchone()
                cursor.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
                db_user = cursor.fetchone()
            except sqlite3.OperationalError:
                await query.answer("DB error!", show_alert=True)
                conn.close()
                return

            if product and db_user:
                product_name, price = product
                current_balance = db_user[0]
                if current_balance >= price:
                    cashback = round(price * 0.05, 2)
                    new_balance = round(current_balance - price + cashback, 2)
                    cursor.execute(
                        "UPDATE users SET balance=?, history=? WHERE user_id=?",
                        (new_balance, product_name, user_id),
                    )
                    conn.commit()
                    await query.answer(T(lang, "buy_ok"), show_alert=True)
                    text = T(
                        lang,
                        "buy_success",
                        name=product_name,
                        balance=new_balance,
                        cashback=cashback,
                    )
                    kb = [
                        [
                            InlineKeyboardButton(
                                T(lang, "btn_home"), callback_data="start"
                            )
                        ]
                    ]
                    await edit_or_send(query, text, InlineKeyboardMarkup(kb))
                else:
                    await query.answer(T(lang, "no_funds"), show_alert=True)
            else:
                await query.answer("Error: data not found.", show_alert=True)
            conn.close()

        elif data == "pomoc":
            await query.answer()
            kb = [
                [
                    InlineKeyboardButton(
                        "💬 OPERATOR",
                        url=get_config("operator_url", "https://t.me/palkerson999"),
                    )
                ],
                [
                    InlineKeyboardButton(
                        "🔧 SUPPORT",
                        url=get_config("support_url", "https://t.me/dkxusnwk"),
                    )
                ],
                [InlineKeyboardButton(T(lang, "btn_back"), callback_data="start")],
            ]
            await edit_or_send(query, T(lang, "help_header"), InlineKeyboardMarkup(kb))

        elif data == "ustawienia":
            await query.answer()
            notif = get_user_notifications(user.id)
            notif_btn = T(lang, "btn_notif_on") if notif else T(lang, "btn_notif_off")
            has_pin = bool(get_user_pin(user.id))
            pin_btn = T(lang, "btn_pin_change") if has_pin else T(lang, "btn_pin_set")
            kb = [
                [
                    InlineKeyboardButton(
                        T(lang, "btn_lang"), callback_data="change_lang"
                    )
                ],
                [InlineKeyboardButton(notif_btn, callback_data="toggle_notif")],
                [InlineKeyboardButton(pin_btn, callback_data="set_pin")],
            ]
            if has_pin:
                kb.append(
                    [
                        InlineKeyboardButton(
                            T(lang, "btn_pin_remove"), callback_data="remove_pin"
                        )
                    ]
                )
            kb.append(
                [
                    InlineKeyboardButton(
                        T(lang, "btn_clear_history"), callback_data="clear_history"
                    )
                ]
            )
            kb.append(
                [InlineKeyboardButton(T(lang, "btn_back"), callback_data="start")]
            )
            await edit_or_send(
                query, T(lang, "settings_header"), InlineKeyboardMarkup(kb)
            )

        elif data == "toggle_notif":
            new_val = toggle_notifications(user.id)
            await query.answer(
                T(lang, "notif_on") if new_val else T(lang, "notif_off"),
                show_alert=True,
            )
            notif_btn = T(lang, "btn_notif_on") if new_val else T(lang, "btn_notif_off")
            has_pin = bool(get_user_pin(user.id))
            pin_btn = T(lang, "btn_pin_change") if has_pin else T(lang, "btn_pin_set")
            kb = [
                [
                    InlineKeyboardButton(
                        T(lang, "btn_lang"), callback_data="change_lang"
                    )
                ],
                [InlineKeyboardButton(notif_btn, callback_data="toggle_notif")],
                [InlineKeyboardButton(pin_btn, callback_data="set_pin")],
            ]
            if has_pin:
                kb.append(
                    [
                        InlineKeyboardButton(
                            T(lang, "btn_pin_remove"), callback_data="remove_pin"
                        )
                    ]
                )
            kb.append(
                [
                    InlineKeyboardButton(
                        T(lang, "btn_clear_history"), callback_data="clear_history"
                    )
                ]
            )
            kb.append(
                [InlineKeyboardButton(T(lang, "btn_back"), callback_data="start")]
            )
            await edit_or_send(
                query, T(lang, "settings_header"), InlineKeyboardMarkup(kb)
            )

        elif data == "change_lang":
            await query.answer()
            kb = [
                [
                    InlineKeyboardButton("🇵🇱 Polski", callback_data="set_lang_pl"),
                    InlineKeyboardButton("🇬🇧 English", callback_data="set_lang_en"),
                ],
                [
                    InlineKeyboardButton("🇺🇦 Українська", callback_data="set_lang_ua"),
                    InlineKeyboardButton("🇷🇺 Русский", callback_data="set_lang_ru"),
                ],
                [InlineKeyboardButton(T(lang, "btn_back"), callback_data="ustawienia")],
            ]
            await edit_or_send(query, T(lang, "lang_header"), InlineKeyboardMarkup(kb))

        elif data.startswith("set_lang_"):
            new_lang = data.split("_")[2]
            if new_lang not in TEXTS:
                new_lang = "pl"
            set_user_lang(user.id, new_lang)
            await query.answer()
            kb = [
                [
                    InlineKeyboardButton(
                        T(new_lang, "btn_back"), callback_data="ustawienia"
                    )
                ]
            ]
            await edit_or_send(
                query, T(new_lang, f"lang_changed_{new_lang}"), InlineKeyboardMarkup(kb)
            )

        elif data == "remove_pin":
            await query.answer()
            kb = [
                [InlineKeyboardButton(T(lang, "btn_back"), callback_data="ustawienia")]
            ]
            context.user_data["removing_pin"] = True
            await edit_or_send(
                query, T(lang, "pin_enter_current"), InlineKeyboardMarkup(kb)
            )

        elif data == "clear_history":
            user_id = query.from_user.id
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "UPDATE users SET history='' WHERE user_id=?", (user_id,)
                )
                conn.commit()
                await query.answer(T(lang, "history_cleared_alert"), show_alert=True)
            except sqlite3.OperationalError as e:
                await query.answer(f"❌ DB error: {e}", show_alert=True)
            conn.close()
            notif = get_user_notifications(user.id)
            notif_btn = T(lang, "btn_notif_on") if notif else T(lang, "btn_notif_off")
            has_pin = bool(get_user_pin(user.id))
            pin_btn = T(lang, "btn_pin_change") if has_pin else T(lang, "btn_pin_set")
            kb = [
                [
                    InlineKeyboardButton(
                        T(lang, "btn_lang"), callback_data="change_lang"
                    )
                ],
                [InlineKeyboardButton(notif_btn, callback_data="toggle_notif")],
                [InlineKeyboardButton(pin_btn, callback_data="set_pin")],
                [
                    InlineKeyboardButton(
                        T(lang, "btn_clear_history"), callback_data="clear_history"
                    )
                ],
                [InlineKeyboardButton(T(lang, "btn_back"), callback_data="start")],
            ]
            await edit_or_send(
                query, T(lang, "history_cleared"), InlineKeyboardMarkup(kb)
            )

    except Exception as e:
        print(f"BŁĄD W BUTTON_HANDLER: {e}")
        try:
            await query.message.reply_text("System error! Check logs.")
        except:
            pass

    return ConversationHandler.END


async def ask_amount(update, context):
    query = update.callback_query
    await query.answer()
    lang = get_user_lang(query.from_user.id)
    kb = [[InlineKeyboardButton(T(lang, "btn_back"), callback_data="cancel_topup")]]
    await edit_or_send(query, T(lang, "topup_amount"), InlineKeyboardMarkup(kb))
    return ASKING_AMOUNT


async def cancel_topup(update, context):
    query = update.callback_query
    await query.answer()
    context.user_data.clear()
    lang = get_user_lang(query.from_user.id)
    text = T(lang, "start", name=query.from_user.first_name)
    await edit_or_send(query, text, InlineKeyboardMarkup(get_main_menu_keyboard(lang)))
    return ConversationHandler.END


async def get_amount(update, context):
    context.user_data["amount"] = update.message.text
    lang = get_user_lang(update.effective_user.id)
    kb = [
        [InlineKeyboardButton(T(lang, "btn_blik"), callback_data="pay_blik")],
        [InlineKeyboardButton(T(lang, "btn_crypto"), callback_data="pay_krypto")],
        [InlineKeyboardButton(T(lang, "btn_back"), callback_data="back_to_amount")],
    ]
    await update.message.reply_text(
        T(lang, "topup_method", amount=update.message.text),
        reply_markup=InlineKeyboardMarkup(kb),
    )
    return METHOD_SELECTION


async def process_blik(update, context):
    query = update.callback_query
    await query.answer()
    order_id = str(uuid.uuid4().int)[:7]
    amount = context.user_data.get("amount", 0)
    text = (
        f"<b>Płatność przez BLIK / Przelew bankowy</b>\n\n"
        f"▪️ Numer zgłoszenia: <code>{order_id}</code>\n"
        f"▪️ Nr telefonu do przelewu: <code>{get_config('blik_phone', '+48 690 758 807')}</code>\n"
        f"▪️ Kwota: <b>{amount} PLN</b>\n\n"
        f"🔴 <b>WAŻNE PRZEZ 14 MINUT</b>\n"
        f"🔴 Płatność w JEDNEJ TRANSAKCJI\n"
        f"🔴 Tytuł: <code>{order_id}</code>\n\n"
        f"Po przelewie wyślij screenshot potwierdzenia jako zdjęcie."
    )
    kb = [
        [InlineKeyboardButton("🔄 Sprawdź status", callback_data="check_blik_status")],
        [InlineKeyboardButton("❌ Anuluj", callback_data="cancel_order")],
    ]
    await query.edit_message_text(
        text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="HTML"
    )
    return BLIK_WAIT_SCREEN


async def check_blik_status(update, context):
    query = update.callback_query
    await query.answer(
        "Weryfikuję... Jeśli wysłałeś potwierdzenie, czekaj na admina.", show_alert=True
    )


async def show_crypto_menu(update, context):
    query = update.callback_query
    await query.answer()
    kb = [
        [InlineKeyboardButton("💵 USDT (TRC20)", callback_data="krypto_usdt")],
        [InlineKeyboardButton("₿ BTC", callback_data="krypto_btc")],
        [InlineKeyboardButton("💎 TON", callback_data="krypto_ton")],
        [InlineKeyboardButton("⚡ LTC", callback_data="krypto_ltc")],
        [InlineKeyboardButton("⬅️ Powrót", callback_data="back_to_methods")],
    ]
    await query.edit_message_text(
        "Wybierz kryptowalutę:", reply_markup=InlineKeyboardMarkup(kb)
    )
    return CRYPTO_CHOICE


async def generate_crypto_order(update, context):
    query = update.callback_query
    await query.answer()
    crypto_type = query.data.split("_")[1]
    try:
        amount_pln = float(context.user_data.get("amount", 0))
    except ValueError:
        amount_pln = 0.0
    rates = {"btc": 238000.0, "usdt": 3.8, "ton": 6.2, "ltc": 164.0}
    amount_crypto = amount_pln / rates.get(crypto_type, 1)
    wallets = {
        "btc": "15GLxW8Adp1kB3EimnxBievbPJMBqEhJU5",
        "usdt": "TGv7e7c7b1T1KnP1SrqsGKGk9PrA4nQYFb",
        "ton": "UQAcj9zyg24HusMZWuymohJDNqSWsG1FXbucqnSWClF9zgo5",
        "ltc": "LUpyy4zegbeJwSDZAm7PV95i214w2MCERV",
    }
    wallet = wallets.get(crypto_type)
    order_id = str(uuid.uuid4())[:8]
    context.user_data["start_time"] = time.time()
    text = (
        f"<b>Płatność w {crypto_type.upper()}</b>\n\n"
        f"▪️ Portfel: <code>{wallet}</code>\n"
        f"▪️ ID zamówienia: <code>{order_id}</code>\n"
        f"▪️ Kwota: <b>{amount_crypto:.8f} {crypto_type.upper()}</b>\n\n"
        f"🔴 WAŻNE PRZEZ 29 MINUT\n"
        f"🔴 Wyślij odrobinę więcej (kurs się zmienia)\n"
        f"🔴 JEDNORAZOWO\n\n"
        f"Po wysłaniu — podeślij screenshot potwierdzenia."
    )
    kb = [
        [InlineKeyboardButton("⏳ Sprawdź status", callback_data="check_status")],
        [InlineKeyboardButton("❌ Anuluj", callback_data="cancel_order")],
    ]
    await query.edit_message_text(
        text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="HTML"
    )
    return KRYPTO_WAIT_SCREEN


async def check_payment_status(update, context):
    query = update.callback_query
    start_time = context.user_data.get("start_time")
    if not start_time:
        await query.answer("Wygeneruj zamówienie ponownie.", show_alert=True)
        return
    remaining = 29 * 60 - (time.time() - start_time)
    if remaining <= 0:
        await query.edit_message_text("❌ CZAS MINĄŁ! Zamówienie wygasło.")
    else:
        await query.answer(
            f"⏳ Pozostało: {int(remaining // 60)}m {int(remaining % 60)}s",
            show_alert=True,
        )


async def handle_payment_proof(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        await update.message.reply_text("Wyślij screenshot jako ZDJĘCIE.")
        return BLIK_WAIT_SCREEN
    photo_file = update.message.photo[-1].file_id
    user = update.effective_user
    amount_declared = context.user_data.get("amount", "Nieznana")
    caption = (
        f"🔔 <b>Nowe potwierdzenie wpłaty!</b>\n\n"
        f"👤 @{user.username}\n"
        f"🆔 <code>{user.id}</code>\n"
        f"💰 Kwota: <b>{amount_declared} PLN</b>\n\n"
        f"<code>/set_saldo {user.id} [kwota]</code>"
    )
    await context.bot.send_photo(
        chat_id=ADMIN_ID, photo=photo_file, caption=caption, parse_mode="HTML"
    )
    await update.message.reply_text("✅ Potwierdzenie wysłane. Czekaj na doładowanie.")
    return ConversationHandler.END


async def back_to_methods(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    kb = [
        [InlineKeyboardButton("💳 BLIK", callback_data="pay_blik")],
        [InlineKeyboardButton("🪙 KRYPTO", callback_data="pay_krypto")],
        [InlineKeyboardButton("⬅️ Powrót", callback_data="back_to_amount")],
    ]
    await query.edit_message_text(
        "Wybierz metodę płatności:", reply_markup=InlineKeyboardMarkup(kb)
    )
    return METHOD_SELECTION


async def cancel_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("Anulowano.", show_alert=True)
    context.user_data.clear()
    await start(update, context)
    return ConversationHandler.END


async def set_saldo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Brak uprawnień.")
        return
    if len(context.args) < 2:
        await update.message.reply_text(
            "⚠️ Użycie: <code>/set_saldo [ID] [KWOTA]</code>", parse_mode="HTML"
        )
        return
    try:
        target_id = int(context.args[0])
        new_balance = float(context.args[1])
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM users WHERE user_id = ?", (target_id,))
        row = cursor.fetchone()
        if not row:
            await update.message.reply_text(
                "❌ Użytkownik nie istnieje (musi kliknąć /start)."
            )
            conn.close()
            return
        cursor.execute(
            "UPDATE users SET balance = ? WHERE user_id = ?", (new_balance, target_id)
        )
        conn.commit()
        conn.close()
        await update.message.reply_text(
            f"✅ Saldo @{row[0]} → <b>{new_balance:.2f} zł</b>", parse_mode="HTML"
        )
        try:
            await context.bot.send_message(
                chat_id=target_id,
                text=f"🔔 <b>Saldo zaktualizowane!</b>\n💰 Stan konta: <b>{new_balance:.2f} zł</b>",
                parse_mode="HTML",
            )
        except Exception:
            pass
    except ValueError:
        await update.message.reply_text("❌ Podaj poprawne ID i kwotę.")


async def admin_list_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, price, is_global, city, district, photo_id FROM products ORDER BY id"
    )
    rows = cursor.fetchall()
    conn.close()
    if not rows:
        await update.message.reply_text("📭 Baza produktów jest pusta.")
        return
    lines = ["📦 <b>LISTA PRODUKTÓW:</b>\n"]
    for pid, name, price, is_global, city, district, photo_id in rows:
        scope = "🌍 Global" if is_global else f"📍 {city}/{district}"
        foto = "🖼" if photo_id else "📄"
        lines.append(
            f"{foto} <code>ID:{pid}</code> | {name} | <b>{price:.0f} zł</b> | {scope}"
        )
    await update.message.reply_text("\n".join(lines), parse_mode="HTML")


async def admin_add_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    usage = (
        "⚠️ <b>Użycie:</b>\n"
        "<code>/addproduct nazwa | cena | opis</code> — globalny\n"
        "<code>/addproduct nazwa | cena | opis | miasto | dzielnica</code> — lokalny\n\n"
        "Potem: <code>/setphoto [ID]</code> (odpowiadając na zdjęcie)"
    )
    if not context.args:
        await update.message.reply_text(usage, parse_mode="HTML")
        return
    raw = " ".join(context.args)
    parts = [p.strip() for p in raw.split("|")]
    if len(parts) < 2:
        await update.message.reply_text(usage, parse_mode="HTML")
        return
    name = parts[0]
    try:
        price = float(parts[1])
    except ValueError:
        await update.message.reply_text("❌ Cena musi być liczbą.")
        return
    description = parts[2] if len(parts) > 2 else ""
    if len(parts) >= 5:
        city, district, is_global = parts[3].lower(), parts[4].lower(), 0
    else:
        city, district, is_global = "", "", 1
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO products (name, price, city, district, description, is_global) VALUES (?, ?, ?, ?, ?, ?)",
        (name, price, city, district, description, is_global),
    )
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    scope = "🌍 Globalny" if is_global else f"📍 {city}/{district}"
    await update.message.reply_text(
        f"✅ Dodano <code>ID:{new_id}</code> | <b>{name}</b> | {price:.0f} zł | {scope}\n\n"
        f"Aby dodać zdjęcie: wyślij foto i odpowiedz na nie: <code>/setphoto {new_id}</code>",
        parse_mode="HTML",
    )


async def admin_del_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if not context.args:
        await update.message.reply_text(
            "⚠️ Użycie: <code>/delproduct [ID]</code>", parse_mode="HTML"
        )
        return
    try:
        product_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ ID musi być liczbą.")
        return
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM products WHERE id=?", (product_id,))
    row = cursor.fetchone()
    if not row:
        await update.message.reply_text(f"❌ Produkt ID:{product_id} nie istnieje.")
        conn.close()
        return
    cursor.execute("DELETE FROM products WHERE id=?", (product_id,))
    conn.commit()
    conn.close()
    await update.message.reply_text(
        f"🗑 Usunięto: <b>{row[0]}</b> (ID:{product_id})", parse_mode="HTML"
    )


async def admin_set_desc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if len(context.args) < 2:
        await update.message.reply_text(
            "⚠️ <b>Użycie:</b>\n<code>/setdesc [ID] Twój opis produktu tutaj</code>",
            parse_mode="HTML",
        )
        return
    try:
        product_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ ID musi być liczbą.")
        return
    description = " ".join(context.args[1:])
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM products WHERE id=?", (product_id,))
    row = cursor.fetchone()
    if not row:
        await update.message.reply_text(f"❌ Produkt ID:{product_id} nie istnieje.")
        conn.close()
        return
    cursor.execute(
        "UPDATE products SET description=? WHERE id=?", (description, product_id)
    )
    conn.commit()
    conn.close()
    preview = description[:80] + ("..." if len(description) > 80 else "")
    await update.message.reply_text(
        f"✅ Opis ustawiony dla <b>{row[0]}</b> (ID:{product_id})\n\n📝 <i>{preview}</i>",
        parse_mode="HTML",
    )


async def admin_photo_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return ConversationHandler.END
    context.user_data["pending_photo_id"] = update.message.photo[-1].file_id
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM products ORDER BY id")
    rows = cursor.fetchall()
    conn.close()
    lista = (
        "\n".join([f"  <code>{r[0]}</code> — {r[1]}" for r in rows])
        if rows
        else "  (brak produktów)"
    )
    await update.message.reply_text(
        f"🖼 <b>Zdjęcie odebrane!</b>\n\n"
        f"Wpisz <b>ID produktu</b> do którego chcesz przypisać zdjęcie:\n\n"
        f"<b>Lista produktów:</b>\n{lista}\n\n"
        f"Wpisz samo ID (np. <code>3</code>) lub /anuluj aby przerwać:",
        parse_mode="HTML",
    )
    return ADMIN_PHOTO_WAIT_ID


async def admin_photo_got_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_id = context.user_data.get("pending_photo_id")
    if not photo_id:
        await update.message.reply_text(
            "❌ Coś poszło nie tak. Wyślij zdjęcie ponownie."
        )
        return ConversationHandler.END
    try:
        product_id = int(update.message.text.strip())
    except ValueError:
        await update.message.reply_text(
            "❌ Podaj samo ID (liczba), np. <code>3</code>", parse_mode="HTML"
        )
        return ADMIN_PHOTO_WAIT_ID
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM products WHERE id=?", (product_id,))
    row = cursor.fetchone()
    if not row:
        await update.message.reply_text(
            f"❌ Produkt ID:{product_id} nie istnieje. Spróbuj ponownie:"
        )
        conn.close()
        return ADMIN_PHOTO_WAIT_ID
    cursor.execute("UPDATE products SET photo_id=? WHERE id=?", (photo_id, product_id))
    conn.commit()
    conn.close()
    context.user_data.pop("pending_photo_id", None)
    await update.message.reply_text(
        f"✅ Zdjęcie przypisane do <b>{row[0]}</b> (ID:{product_id})!\n\n"
        f"📸 Wyślij kolejne zdjęcie lub wróć do bota.",
        parse_mode="HTML",
    )
    return ConversationHandler.END


async def admin_desc_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return ConversationHandler.END
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, description FROM products ORDER BY id")
    rows = cursor.fetchall()
    conn.close()
    lines = []
    for r in rows:
        has_desc = "✅" if r[2] else "❌"
        lines.append(f"  {has_desc} <code>{r[0]}</code> — {r[1]}")
    lista = "\n".join(lines) if lines else "  (brak produktów)"
    await update.message.reply_text(
        f"📝 <b>TRYB DODAWANIA OPISÓW</b>\n\n"
        f"<b>Produkty:</b>\n{lista}\n\n"
        f"Wpisz ID produktu do którego chcesz dodać opis:",
        parse_mode="HTML",
    )
    return ADMIN_DESC_WAIT_TEXT


async def admin_desc_got_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    try:
        product_id = int(text)
    except ValueError:
        await update.message.reply_text(
            "❌ Podaj samo ID (liczba), np. <code>3</code>", parse_mode="HTML"
        )
        return ADMIN_DESC_WAIT_TEXT
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT name, description FROM products WHERE id=?", (product_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        await update.message.reply_text(
            f"❌ Produkt ID:{product_id} nie istnieje. Spróbuj ponownie:"
        )
        return ADMIN_DESC_WAIT_TEXT
    context.user_data["desc_product_id"] = product_id
    context.user_data["desc_product_name"] = row[0]
    current = (
        f"\n\n<i>Aktualny opis:</i>\n<blockquote>{row[1]}</blockquote>"
        if row[1]
        else ""
    )
    await update.message.reply_text(
        f"📝 Wpisujesz opis dla: <b>{row[0]}</b>{current}\n\n"
        f"Wklej nowy opis (może być długi, wieloliniowy):",
        parse_mode="HTML",
    )
    context.user_data["desc_awaiting_text"] = True
    return ADMIN_DESC_WAIT_TEXT


async def admin_desc_got_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("desc_awaiting_text"):
        return await admin_desc_got_product(update, context)
    product_id = context.user_data.get("desc_product_id")
    product_name = context.user_data.get("desc_product_name", "")
    description = update.message.text.strip()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE products SET description=? WHERE id=?", (description, product_id)
    )
    conn.commit()
    conn.close()
    context.user_data.pop("desc_awaiting_text", None)
    context.user_data.pop("desc_product_id", None)
    preview = description[:100] + ("..." if len(description) > 100 else "")
    await update.message.reply_text(
        f"✅ Opis zapisany dla <b>{product_name}</b>!\n\n"
        f"📝 <i>{preview}</i>\n\n"
        f"Podaj kolejne ID produktu lub /anuluj:",
        parse_mode="HTML",
    )
    context.user_data.pop("desc_product_name", None)
    return ADMIN_DESC_WAIT_TEXT


async def admin_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("❌ Anulowano.")
    return ConversationHandler.END


async def handle_pin_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    lang = get_user_lang(user.id)
    text = update.message.text.strip()

    if context.user_data.get("removing_pin"):
        correct_pin = get_user_pin(user.id)
        if text == correct_pin:
            remove_user_pin(user.id)
            context.user_data.pop("removing_pin", None)
            await update.message.reply_text(T(lang, "pin_removed"))
        else:
            await update.message.reply_text(T(lang, "pin_wrong_current"))
            kb = [
                [InlineKeyboardButton(T(lang, "btn_back"), callback_data="ustawienia")]
            ]
            await update.message.reply_text(
                T(lang, "pin_enter_current"), reply_markup=InlineKeyboardMarkup(kb)
            )
        return

    if context.user_data.get("awaiting_pin"):
        correct_pin = get_user_pin(user.id)
        if text == correct_pin:
            context.user_data["pin_verified"] = True
            context.user_data.pop("awaiting_pin", None)
            db_data = get_user_data(user.id)
            if db_data:
                saldo, znizka, historia, zaproszeni = db_data
            else:
                saldo, znizka, historia, zaproszeni = 0.0, 0, "—", 0
            znizka = min(zaproszeni * 2, 10)
            if not historia:
                historia = "—"
            profile_text = T(
                lang,
                "profile",
                balance=saldo,
                discount=znizka,
                invited=zaproszeni,
                history=historia,
            )
            kb = [
                [
                    InlineKeyboardButton(
                        T(lang, "btn_cashback"), callback_data="info_cashback"
                    )
                ],
                [InlineKeyboardButton(T(lang, "btn_invite"), callback_data="reflink")],
                [InlineKeyboardButton(T(lang, "btn_topup2"), callback_data="doladuj")],
                [InlineKeyboardButton(T(lang, "btn_back"), callback_data="start")],
            ]
            await update.message.reply_text(
                profile_text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="HTML"
            )
        else:
            await update.message.reply_text(T(lang, "pin_wrong"))
            kb = [[InlineKeyboardButton(T(lang, "btn_back"), callback_data="start")]]
            await update.message.reply_text(
                T(lang, "pin_prompt"), reply_markup=InlineKeyboardMarkup(kb)
            )
        return


async def start_set_pin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = get_user_lang(query.from_user.id)
    kb = [[InlineKeyboardButton(T(lang, "btn_back"), callback_data="ustawienia")]]
    await edit_or_send(query, T(lang, "pin_enter_new"), InlineKeyboardMarkup(kb))
    return SETTING_PIN


async def get_new_pin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_user_lang(update.effective_user.id)
    pin = update.message.text.strip()
    if not pin.isdigit() or len(pin) != 4:
        await update.message.reply_text(T(lang, "pin_invalid"))
        return SETTING_PIN
    context.user_data["new_pin"] = pin
    kb = [[InlineKeyboardButton(T(lang, "btn_back"), callback_data="ustawienia")]]
    await update.message.reply_text(
        T(lang, "pin_confirm"), reply_markup=InlineKeyboardMarkup(kb)
    )
    return CONFIRM_PIN


async def confirm_new_pin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_user_lang(update.effective_user.id)
    pin = update.message.text.strip()
    new_pin = context.user_data.get("new_pin")
    if pin != new_pin:
        await update.message.reply_text(T(lang, "pin_mismatch"))
        return SETTING_PIN
    set_user_pin(update.effective_user.id, pin)
    context.user_data.pop("new_pin", None)
    context.user_data["pin_verified"] = True
    await update.message.reply_text(T(lang, "pin_set_ok"))
    return ConversationHandler.END


async def cancel_pin_setup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        await query.answer()
        context.user_data.pop("new_pin", None)
    return ConversationHandler.END


async def admin_set_config(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    CONFIG_KEYS = {
        "blik_phone": "numer telefonu do BLIK (np. +48 123 456 789)",
        "operator_url": "link do operatora (np. https://t.me/username)",
        "support_url": "link do supportu (np. https://t.me/username)",
        "blik_name": "imię/nick do przelewu BLIK",
    }
    if len(context.args) < 2:
        keys_info = "\n".join(
            [f"  <code>{k}</code> — {v}" for k, v in CONFIG_KEYS.items()]
        )
        await update.message.reply_text(
            f"⚙️ <b>EDYTOR USTAWIEŃ</b>\n\n"
            f"Użycie: <code>/setconfig [klucz] [wartość]</code>\n\n"
            f"<b>Dostępne klucze:</b>\n{keys_info}",
            parse_mode="HTML",
        )
        return
    key = context.args[0].lower()
    value = " ".join(context.args[1:])
    set_config(key, value)
    await update.message.reply_text(
        f"✅ Zapisano:\n<code>{key}</code> = <b>{value}</b>", parse_mode="HTML"
    )


async def admin_get_config(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    rows = get_all_config()
    DEFAULTS = {
        "blik_phone": "+48 690 758 807",
        "operator_url": "https://t.me/palkerson999",
        "support_url": "https://t.me/dkxusnwk",
        "blik_name": "—",
    }
    lines = ["⚙️ <b>AKTUALNA KONFIGURACJA:</b>\n"]
    for k, default in DEFAULTS.items():
        current_row = next((r for r in rows if r[0] == k), None)
        val = current_row[1] if current_row else f"<i>(domyślne: {default})</i>"
        lines.append(f"<code>{k}</code>: {val}")
    if rows:
        saved_keys = {r[0] for r in rows}
        for k, v in rows:
            if k not in DEFAULTS:
                lines.append(f"<code>{k}</code>: {v}")
    await update.message.reply_text("\n".join(lines), parse_mode="HTML")


async def admin_edit_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if not context.args:
        await update.message.reply_text(
            "⚠️ <b>Użycie:</b>\n"
            "<code>/editproduct [ID] nowa nazwa | nowa cena</code>\n\n"
            "Możesz podać samo imię, samą cenę lub oba:\n"
            "<code>/editproduct 3 Alpha-PVP 2g Premium | 200</code>\n"
            "<code>/editproduct 3 | 180</code>  — tylko cena\n"
            "<code>/editproduct 3 Nowa nazwa</code>  — tylko nazwa",
            parse_mode="HTML",
        )
        return
    try:
        product_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ ID musi być liczbą.")
        return
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT name, price FROM products WHERE id=?", (product_id,))
    row = cursor.fetchone()
    if not row:
        await update.message.reply_text(f"❌ Produkt ID:{product_id} nie istnieje.")
        conn.close()
        return
    old_name, old_price = row
    raw = " ".join(context.args[1:])
    parts = [p.strip() for p in raw.split("|")]
    new_name = parts[0] if parts[0] else old_name
    new_price = old_price
    if len(parts) >= 2:
        try:
            new_price = float(parts[1])
        except ValueError:
            await update.message.reply_text("❌ Cena musi być liczbą.")
            conn.close()
            return
    cursor.execute(
        "UPDATE products SET name=?, price=? WHERE id=?",
        (new_name, new_price, product_id),
    )
    conn.commit()
    conn.close()
    await update.message.reply_text(
        f"✅ <b>Zaktualizowano produkt ID:{product_id}</b>\n\n"
        f"Nazwa: <b>{old_name}</b> → <b>{new_name}</b>\n"
        f"Cena: <b>{old_price:.0f} zł</b> → <b>{new_price:.0f} zł</b>",
        parse_mode="HTML",
    )


async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    cursor.execute("SELECT SUM(balance) FROM users")
    total_balance = cursor.fetchone()[0] or 0.0
    cursor.execute("SELECT COUNT(*) FROM products")
    total_products = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM products WHERE photo_id IS NOT NULL")
    products_with_photo = cursor.fetchone()[0]
    cursor.execute(
        "SELECT COUNT(*) FROM products WHERE description != '' AND description IS NOT NULL"
    )
    products_with_desc = cursor.fetchone()[0]
    cursor.execute(
        "SELECT history FROM users WHERE history != '' AND history IS NOT NULL"
    )
    histories = [r[0] for r in cursor.fetchall()]
    conn.close()
    from collections import Counter

    top = Counter(histories).most_common(5)
    top_lines = (
        "\n".join([f"  {i + 1}. {name} — {cnt}x" for i, (name, cnt) in enumerate(top)])
        if top
        else "  brak danych"
    )
    await update.message.reply_text(
        f"📊 <b>STATYSTYKI BOTA</b>\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"👥 Użytkownicy: <b>{total_users}</b>\n"
        f"💰 Łączne saldo w obiegu: <b>{total_balance:.2f} zł</b>\n\n"
        f"📦 Produkty: <b>{total_products}</b>\n"
        f"  🖼 Ze zdjęciem: <b>{products_with_photo}</b>\n"
        f"  📝 Z opisem: <b>{products_with_desc}</b>\n\n"
        f"🏆 <b>TOP 5 kupowanych:</b>\n{top_lines}",
        parse_mode="HTML",
    )


async def admin_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if not context.args:
        await update.message.reply_text(
            "⚠️ <b>Użycie:</b>\n<code>/broadcast Twoja wiadomość tutaj</code>",
            parse_mode="HTML",
        )
        return
    msg = " ".join(context.args)
    all_ids = get_all_user_ids()
    ok, fail = 0, 0
    for uid in all_ids:
        try:
            await context.bot.send_message(
                chat_id=uid, text=f"📢 <b>OGŁOSZENIE:</b>\n\n{msg}", parse_mode="HTML"
            )
            ok += 1
        except Exception:
            fail += 1
    await update.message.reply_text(
        f"✅ Broadcast zakończony!\n📨 Wysłano: <b>{ok}</b>\n❌ Błędy: <b>{fail}</b>",
        parse_mode="HTML",
    )


async def admin_set_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if not context.args:
        await update.message.reply_text(
            "⚠️ Użycie: Odpowiedz na zdjęcie komendą <code>/setphoto [ID]</code>",
            parse_mode="HTML",
        )
        return
    try:
        product_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ ID musi być liczbą.")
        return

    photo_id = None
    if update.message.reply_to_message and update.message.reply_to_message.photo:
        photo_id = update.message.reply_to_message.photo[-1].file_id
    elif update.message.photo:
        photo_id = update.message.photo[-1].file_id

    if not photo_id:
        await update.message.reply_text(
            "❌ Odpowiedz na wiadomość ze zdjęciem lub wyślij zdjęcie z tą komendą jako podpisem."
        )
        return

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM products WHERE id=?", (product_id,))
    row = cursor.fetchone()
    if not row:
        await update.message.reply_text(f"❌ Produkt ID:{product_id} nie istnieje.")
        conn.close()
        return
    cursor.execute("UPDATE products SET photo_id=? WHERE id=?", (photo_id, product_id))
    conn.commit()
    conn.close()
    await update.message.reply_text(
        f"🖼 Zdjęcie dodane do produktu <b>{row[0]}</b> (ID:{product_id})",
        parse_mode="HTML",
    )


if __name__ == "__main__":
    init_db()
    app = (
        ApplicationBuilder()
        .token("7979725165:AAEe23Oxc2NHlM5Oi4G5oe8mXz_RcCaGEWk")
        .build()
    )

    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(ask_amount, pattern="^doladuj$")],
        states={
            ASKING_AMOUNT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_amount),
                CallbackQueryHandler(cancel_topup, pattern="^cancel_topup$"),
            ],
            METHOD_SELECTION: [
                CallbackQueryHandler(process_blik, pattern="^pay_blik$"),
                CallbackQueryHandler(show_crypto_menu, pattern="^pay_krypto$"),
                CallbackQueryHandler(ask_amount, pattern="^back_to_amount$"),
            ],
            CRYPTO_CHOICE: [
                CallbackQueryHandler(
                    generate_crypto_order, pattern="^krypto_(usdt|btc|ton|ltc)$"
                ),
                CallbackQueryHandler(back_to_methods, pattern="^back_to_methods$"),
            ],
            KRYPTO_WAIT_SCREEN: [
                CallbackQueryHandler(check_payment_status, pattern="^check_status$"),
                CallbackQueryHandler(cancel_order, pattern="^cancel_order$"),
                MessageHandler(filters.PHOTO, handle_payment_proof),
            ],
            BLIK_WAIT_SCREEN: [
                CallbackQueryHandler(check_blik_status, pattern="^check_blik_status$"),
                CallbackQueryHandler(cancel_order, pattern="^cancel_order$"),
                MessageHandler(filters.PHOTO, handle_payment_proof),
            ],
        },
        fallbacks=[
            CommandHandler("start", start),
            CallbackQueryHandler(cancel_order, pattern="^cancel_order$"),
            CallbackQueryHandler(button_handler),
        ],
        per_message=False,
    )

    pin_conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_set_pin, pattern="^set_pin$")],
        states={
            SETTING_PIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_new_pin)],
            CONFIRM_PIN: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_new_pin)
            ],
        },
        fallbacks=[
            CallbackQueryHandler(cancel_pin_setup, pattern="^ustawienia$"),
            CommandHandler("start", start),
        ],
        per_message=False,
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("set_saldo", set_saldo))
    app.add_handler(CommandHandler("listproducts", admin_list_products))
    app.add_handler(CommandHandler("addproduct", admin_add_product))
    app.add_handler(CommandHandler("delproduct", admin_del_product))
    app.add_handler(CommandHandler("setphoto", admin_set_photo))
    app.add_handler(CommandHandler("setdesc", admin_set_desc))
    app.add_handler(CommandHandler("stats", admin_stats))
    app.add_handler(CommandHandler("setconfig", admin_set_config))
    app.add_handler(CommandHandler("getconfig", admin_get_config))
    app.add_handler(CommandHandler("editproduct", admin_edit_product))
    app.add_handler(CommandHandler("broadcast", admin_broadcast))
    admin_photo_conv = ConversationHandler(
        entry_points=[
            MessageHandler(filters.PHOTO & filters.User(ADMIN_ID), admin_photo_received)
        ],
        states={
            ADMIN_PHOTO_WAIT_ID: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, admin_photo_got_id)
            ],
        },
        fallbacks=[CommandHandler("anuluj", admin_cancel)],
        per_message=False,
    )

    admin_desc_conv = ConversationHandler(
        entry_points=[CommandHandler("addopisy", admin_desc_start)],
        states={
            ADMIN_DESC_WAIT_TEXT: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    lambda u, c: (
                        admin_desc_got_text(u, c)
                        if c.user_data.get("desc_awaiting_text")
                        else admin_desc_got_product(u, c)
                    ),
                )
            ],
        },
        fallbacks=[CommandHandler("anuluj", admin_cancel)],
        per_message=False,
    )

    app.add_handler(admin_photo_conv)
    app.add_handler(admin_desc_conv)
    app.add_handler(pin_conv_handler)
    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("anuluj", admin_cancel))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_pin_entry))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Bot się uruchomił i czeka na wiadomości...")
    app.run_polling()
