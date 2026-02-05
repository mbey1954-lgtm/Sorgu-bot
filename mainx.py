import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# === AYARLAR ===
BOT_TOKEN = "8500441874:AAGvjXGC0zqH6si8et1yBYkb_PV8mHmmnok"  # BOT TOKENINIZ
ADMIN_ID =8444268448
ADMIN_USERNAME = "zordodestek"
MAX_FILES = 5
DATA_FOLDER = "user_files"
PENDING_FOLDER = "pending_files"
RUNNING_FOLDER = "running_scripts"
LOG_FILE = "usage_logs.txt"

os.makedirs(DATA_FOLDER, exist_ok=True)
os.makedirs(PENDING_FOLDER, exist_ok=True)
os.makedirs(RUNNING_FOLDER, exist_ok=True)

# Kullanıcı verileri
user_data = {}  # {user_id: {'lang': 'tr', 'approved': False, 'files': [], 'pending': [], 'banned': False, 'username': ''}}

# === ÇOK DİLLİ METİNLER ===
LANGUAGES = {
    'tr': {
        'choose_lang': "🌍 Lütfen dilinizi seçin:",
        'welcome': "🚀 *Merhaba {name}!*\n\nBen *ZORDO-SANAL-VDS* 🤖\nÜcretsiz sanal VDS! Python scriptini yükle, admin onaylasın → otomatik çalışsın 🔥",
        'rules': "📌 Sadece `.py` dosyası\n⏳ Admin onayı zorunlu\n📊 Maksimum 5 dosya",
        'upload_btn': "📤 Dosya Yükle",
        'myfiles_btn': "📂 Dosyalarım",
        'help_btn': "ℹ️ Yardım",
        'admin_btn': "👤 Admin",
        'change_lang_btn': "🌍 Dil Değiştir",
        'back_btn': "🔙 Ana Menü",
        'upload_prompt': "📤 Gönder bakalım `.py` dosyanı! Admin onayı sonrası çalışacak 🚀",
        'file_uploaded': "📤 {file} yüklendi!\n⏳ Admin onayı bekleniyor...",
        'file_approved': "✅ {file} onaylandı ve çalıştırılıyor! 🚀",
        'file_rejected': "❌ {file} dosyası reddedildi.",
        'max_files': "⚠️ Maksimum 5 dosya hakkın var! Önce birini sil.",
        'only_py': "❌ Sadece `.py` dosyası kabul ediyorum!",
        'permission_req': "Merhaba @{username}!\n\n🚀 Botu kullanabilmek için admin onayı gerekiyor.\n\nTalebin @{admin}'a gönderildi. Beklemede kal! ⏳",
        'permission_approved': "✅ Tebrikler! Artık ZORDO-SANAL-VDS'i tam olarak kullanabilirsin! 🚀",
        'permission_rejected': "❌ Üzgünüm, talebin reddedildi.",
        'banned_msg': "🚫 Bu botu kullanman yasaklandı. Admin ile iletişime geç.",
        'help_text': "ℹ️ ZORDİ-SANAL-VDS*\n\n📤 .py dosyası yükle → admin onaylasın → otomatik çalışsın\n📊 Maksimum 5 dosya\n🗑 Dosyalarını sil\n👤 Admin: @{admin}",
        'pending': "⏳ Onay Bekliyor",
        'running': "✅ Çalışıyor",
        'approved': "✅ Onaylı",
    },
    'en': {
        'choose_lang': "🌍 Please select your language:",
        'welcome': "🚀 *Hello {name}!*\n\nI am *ZORDO-SANAL-VDS* 🤖\nFree virtual VDS! Upload Python script → admin approves → runs automatically 🔥",
        'rules': "📌 Only `.py` files\n⏳ Admin approval required\n📊 Maximum 5 files",
        'upload_btn': "📤 Upload File",
        'myfiles_btn': "📂 My Files",
        'help_btn': "ℹ️ Help",
        'admin_btn': "👤 Admin",
        'change_lang_btn': "🌍 Change Language",
        'back_btn': "🔙 Main Menu",
        'upload_prompt': "📤 Send your `.py` file! It will run after admin approval 🚀",
        'file_uploaded': "📤 {file} uploaded!\n⏳ Waiting for admin approval...",
        'file_approved': "✅ {file} approved and running! 🚀",
        'file_rejected': "❌ {file} has been rejected.",
        'max_files': "⚠️ You have reached the maximum of 5 files! Delete one first.",
        'only_py': "❌ Only `.py` files are accepted!",
        'permission_req': "Hello @{username}!\n\n🚀 Admin approval required to use the bot.\nYour request sent to @{admin}. Please wait! ⏳",
        'permission_approved': "✅ Congratulations! You can now fully use ZORDO-SANAL-VDS! 🚀",
        'permission_rejected': "❌ Sorry, your request was rejected.",
        'banned_msg': "🚫 You are banned from using this bot. Contact admin.",
        'help_text': "ℹ️ *ZORDO-SANAL-VDS*\n\n📤 Upload .py file → admin approves → runs automatically\n📊 Max 5 files\n🗑 Delete your files\n👤 Admin: @{admin}",
        'pending': "⏳ Pending Approval",
        'running': "✅ Running",
        'approved': "✅ Approved",
    },
    # 'ar' ve 'ru' dillerini istersen ekleyebilirsin
}

# === ADMİN METİNLERİ ===
ADMIN_TEXTS = {
    'panel_title': "🔧 *ZORDO-SANAL-VDS Admin Paneli*\n\nNe yapmak istiyorsun?",
    'stats_btn': "📊 İstatistikler",
    'logs_btn': "📋 Logları Gönder (txt)",
    'running_btn': "▶️ Çalışan Scriptler",
    'users_btn': "👥 Onaylı Kullanıcılar",
    'stop_all_btn': "⏹ Tüm Scriptleri Durdur",
    'msg_user_btn': "✉️ Kullanıcıya Mesaj",
    'announce_btn': "📢 Toplu Duyuru",
    'back_admin': "🔙 Ana Menüye Dön",
    'no_logs': "📄 Henüz log yok.",
    'logs_caption': "📊 ZORDO-SANAL-VDS Kullanım Logları",
    'running_title': "✅ *Çalışan Scriptler*",
    'no_running': "Hiç çalışan script yok.",
    'users_title': "👥 *Onaylı Kullanıcılar*",
    'no_users': "Onaylı kullanıcı yok.",
    'announce_prompt': "📢 Duyuru mesajını yaz (tüm onaylı kullanıcılara gönderilecek):",
    'announce_sent': "📢 Duyurunuz tüm onaylı kullanıcılara gönderildi!",
    'msg_prompt': "✉️ Mesaj göndermek istediğin kullanıcı ID'sini yaz:",
    'msg_text_prompt': "✉️ Göndermek istediğin mesajı yaz (ID: {uid}):",
    'msg_sent': "✅ Mesaj gönderildi!",
    'ban_prompt': "🚫 Banlamak istediğin kullanıcı ID'sini yaz:",
    'unban_prompt': "✅ Ban kaldırmak istediğin kullanıcı ID'sini yaz:",
    'banned': "🚫 Kullanıcı banlandı!",
    'unbanned': "✅ Kullanıcının banı kaldırıldı!",
    'all_stopped': "🛑 {count} adet çalışan script durduruldu.",
    'nothing_to_stop': "⚠️ Zaten çalışan script yok.",
}

def get_lang(user_id):
    return user_data.get(user_id, {}).get('lang', 'tr')

def t(user_id, key, **kwargs):
    lang = get_lang(user_id)
    text = LANGUAGES.get(lang, LANGUAGES['tr']).get(key, LANGUAGES['tr'][key])
    return text.format(**kwargs, admin=ADMIN_USERNAME)

# === KLAVYELER ===
def get_language_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🇹🇷 Türkçe", callback_data="lang_tr")],
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")],
        # İstersen Arapça ve Rusça ekle
    ])

def get_main_menu(user_id):
    lang = get_lang(user_id)
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(LANGUAGES[lang]['upload_btn'], callback_data="upload")],
        [InlineKeyboardButton(LANGUAGES[lang]['myfiles_btn'], callback_data="myfiles")],
        [InlineKeyboardButton(LANGUAGES[lang]['help_btn'], callback_data="help")],
        [InlineKeyboardButton(LANGUAGES[lang]['admin_btn'] + f" @{ADMIN_USERNAME}", url=f"https://t.me/{ADMIN_USERNAME}")],
        [InlineKeyboardButton(LANGUAGES[lang]['change_lang_btn'], callback_data="change_lang")]
    ])

def get_admin_panel_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(ADMIN_TEXTS['stats_btn'], callback_data="admin_stats")],
        [InlineKeyboardButton(ADMIN_TEXTS['running_btn'], callback_data="admin_running")],
        [InlineKeyboardButton(ADMIN_TEXTS['stop_all_btn'], callback_data="admin_stop_all")],
        [InlineKeyboardButton(ADMIN_TEXTS['users_btn'], callback_data="admin_users")],
        [InlineKeyboardButton(ADMIN_TEXTS['msg_user_btn'], callback_data="admin_msg_user")],
        [InlineKeyboardButton(ADMIN_TEXTS['announce_btn'], callback_data="admin_announce")],
        [InlineKeyboardButton(ADMIN_TEXTS['logs_btn'], callback_data="admin_logs")],
        [InlineKeyboardButton("🚫 Ban At", callback_data="admin_ban"),
         InlineKeyboardButton("✅ Ban Kaldır", callback_data="admin_unban")],
        [InlineKeyboardButton(ADMIN_TEXTS['back_admin'], callback_data="back")]
    ])

# === BAN KONTROL ===
def is_banned(user_id):
    return user_data.get(user_id, {}).get('banned', False)

# === /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    username = user.username or user.first_name

    if is_banned(user_id):
        await update.message.reply_text(t(user_id, 'banned_msg'))
        return

    if user_id not in user_data:
        await update.message.reply_text(t(user_id, 'choose_lang'), reply_markup=get_language_keyboard())
        return

    if user_id != ADMIN_ID and not user_data[user_id].get('approved', False):
        await update.message.reply_text(t(user_id, 'permission_req', username=username))
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Onayla", callback_data=f"perm_approve_{user_id}"),
             InlineKeyboardButton("❌ Reddet/Banla", callback_data=f"perm_reject_{user_id}")]
        ])
        await context.bot.send_message(
            ADMIN_ID,
            f"🆕 Yeni kullanıcı izin istiyor!\n\n👤 @{username}\n🆔 ID: {user_id}",
            reply_markup=keyboard
        )
        return

    await update.message.reply_text(
        t(user_id, 'welcome', name=user.first_name) + "\n\n" + t(user_id, 'rules'),
        parse_mode='Markdown',
        reply_markup=get_main_menu(user_id)
    )

# === DİL SEÇİMİ ===
async def language_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    username = query.from_user.username or query.from_user.first_name

    if query.data.startswith("lang_"):
        lang_code = query.data.split("_")[1]
        user_data.setdefault(user_id, {})['lang'] = lang_code
        user_data[user_id].setdefault('files', [])
        user_data[user_id].setdefault('pending', [])
        user_data[user_id]['approved'] = (user_id == ADMIN_ID)
        user_data[user_id]['banned'] = False
        user_data[user_id]['username'] = username

        if user_id != ADMIN_ID and not user_data[user_id]['approved']:
            await query.edit_message_text(t(user_id, 'permission_req', username=username))
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Onayla", callback_data=f"perm_approve_{user_id}"),
                 InlineKeyboardButton("❌ Reddet/Banla", callback_data=f"perm_reject_{user_id}")]
            ])
            await context.bot.send_message(
                ADMIN_ID,
                f"🆕 Yeni kullanıcı dil seçti!\n\n👤 @{username}\n🆔 ID: {user_id}",
                reply_markup=keyboard
            )
        else:
            await query.edit_message_text(
                t(user_id, 'welcome', name=query.from_user.first_name) + "\n\n" + t(user_id, 'rules'),
                parse_mode='Markdown',
                reply_markup=get_main_menu(user_id)
            )

    elif query.data == "change_lang":
        await query.edit_message_text("🌍 Yeni dilinizi seçin:", reply_markup=get_language_keyboard())

# === ANA MENÜ BUTONLARI ===
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if is_banned(user_id):
        await query.edit_message_text(t(user_id, 'banned_msg'))
        return

    if user_id != ADMIN_ID and not user_data.get(user_id, {}).get('approved', False):
        await query.edit_message_text(t(user_id, 'permission_req', username=query.from_user.username or "user"))
        return

    data = query.data

    if data == "upload":
        total = len(user_data[user_id].get('files', [])) + len(user_data[user_id].get('pending', []))
        if total >= MAX_FILES:
            await query.edit_message_text(t(user_id, 'max_files'), reply_markup=get_main_menu(user_id))
            return
        await query.edit_message_text(t(user_id, 'upload_prompt'), reply_markup=get_main_menu(user_id))

    elif data == "myfiles":
        files = user_data[user_id].get('files', [])
        pending = user_data[user_id].get('pending', [])
        keyboard = []
        for f in pending:
            keyboard.append([InlineKeyboardButton(f"{t(user_id, 'pending')}: {f}", callback_data="none")])
        for f in files:
            pid_path = os.path.join(RUNNING_FOLDER, f"{user_id}_{f}.pid")
            status = t(user_id, 'running') if os.path.exists(pid_path) else t(user_id, 'approved')
            keyboard.append([InlineKeyboardButton(f"{status} {f}", callback_data="none")])
            keyboard.append([InlineKeyboardButton(f"🗑 Sil: {f}", callback_data=f"delete_{f}")])
        keyboard.append([InlineKeyboardButton(t(user_id, 'back_btn'), callback_data="back")])
        await query.edit_message_text(
            f"📂 Dosyaların ({len(files) + len(pending)}/5)",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data == "help":
        await query.edit_message_text(
            t(user_id, 'help_text'),
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(t(user_id, 'back_btn'), callback_data="back")]])
        )

    elif data == "back":
        await query.edit_message_text(
            t(user_id, 'welcome', name=query.from_user.first_name).split('\n\n')[0],
            reply_markup=get_main_menu(user_id)
        )

    elif data.startswith("delete_"):
        filename = data.split("_", 1)[1]
        for folder in [DATA_FOLDER, PENDING_FOLDER, RUNNING_FOLDER]:
            path = os.path.join(folder, f"{user_id}_{filename}")
            pid_path = path + ".pid"
            if os.path.exists(path):
                os.remove(path)
            if os.path.exists(pid_path):
                try:
                    with open(pid_path) as f:
                        os.kill(int(f.read().strip()), 9)
                except:
                    pass
                os.remove(pid_path)
        user_data[user_id]['files'] = [f for f in user_data[user_id].get('files', []) if f != filename]
        user_data[user_id]['pending'] = [f for f in user_data[user_id].get('pending', []) if f != filename]
        await query.edit_message_text(f"🗑 {filename} silindi!", reply_markup=get_main_menu(user_id))

# === ADMİN PANEL ===
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Bu komut sadece admin içindir!")
        return
    await update.message.reply_text(ADMIN_TEXTS['panel_title'], parse_mode='Markdown', reply_markup=get_admin_panel_menu())

# === ADMİN BUTONLARI ===
async def admin_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.from_user.id != ADMIN_ID:
        await query.answer("❌ Sadece admin!")
        return
    await query.answer()

    data = query.data

    if data == "admin_stats":
        total_users = len(user_data)
        approved = sum(1 for d in user_data.values() if d.get('approved') and not d.get('banned') and int(d.get('user_id', 0)) != ADMIN_ID)
        banned = sum(1 for d in user_data.values() if d.get('banned'))
        pending_files = sum(len(d.get('pending', [])) for d in user_data.values())
        running_count = len([f for f in os.listdir(RUNNING_FOLDER) if f.endswith(".pid")])
        total_files = sum(len(d.get('files', [])) + len(d.get('pending', [])) for d in user_data.values())

        text = (
            "📊 *Bot İstatistikleri*\n\n"
            f"👥 Toplam kullanıcı: {total_users}\n"
            f"✅ Onaylı kullanıcı: {approved}\n"
            f"🚫 Banlı kullanıcı: {banned}\n"
            f"⏳ Bekleyen dosya: {pending_files}\n"
            f"▶️ Çalışan script: {running_count}\n"
            f"📁 Toplam dosya: {total_files}"
        )
        await query.edit_message_text(text, parse_mode='Markdown', reply_markup=get_admin_panel_menu())

    elif data == "admin_logs":
        if not os.path.exists(LOG_FILE) or os.path.getsize(LOG_FILE) == 0:
            await query.edit_message_text(ADMIN_TEXTS['no_logs'], reply_markup=get_admin_panel_menu())
            return
        with open(LOG_FILE, "rb") as f:
            await context.bot.send_document(ADMIN_ID, f, caption=ADMIN_TEXTS['logs_caption'])
        await query.edit_message_text("📊 Loglar gönderildi!", reply_markup=get_admin_panel_menu())

    elif data == "admin_running":
        running_files = []
        for pid_file in os.listdir(RUNNING_FOLDER):
            if pid_file.endswith(".pid"):
                parts = pid_file[:-4].split("_", 1)
                uid = parts[0]
                filename = parts[1] if len(parts) > 1 else "Bilinmeyen"
                username = user_data.get(int(uid), {}).get('username', 'Bilinmeyen')
                running_files.append(f"👤 @{username} (ID: {uid}) | 📄 {filename}")
        text = f"{ADMIN_TEXTS['running_title']}:\n\n" + ("\n".join(running_files) if running_files else ADMIN_TEXTS['no_running'])
        await query.edit_message_text(text, parse_mode='Markdown', reply_markup=get_admin_panel_menu())

    elif data == "admin_stop_all":
        stopped = 0
        for fname in os.listdir(RUNNING_FOLDER):
            if not fname.endswith(".pid"):
                continue
            path = os.path.join(RUNNING_FOLDER, fname)
            try:
                with open(path) as f:
                    pid = int(f.read().strip())
                os.kill(pid, 9)
            except:
                pass
            os.remove(path)
            stopped += 1
        msg = ADMIN_TEXTS['all_stopped'].format(count=stopped) if stopped > 0 else ADMIN_TEXTS['nothing_to_stop']
        await query.edit_message_text(msg, reply_markup=get_admin_panel_menu())

    elif data == "admin_users":
        approved = [uid for uid, d in user_data.items() if d.get('approved') and not d.get('banned') and uid != ADMIN_ID]
        lines = [f"👤 @{d.get('username', 'Bilinmeyen')} | ID: {uid}" for uid, d in user_data.items() if uid in approved]
        text = f"{ADMIN_TEXTS['users_title']} ({len(lines)}):\n\n" + ("\n".join(lines) if lines else ADMIN_TEXTS['no_users'])
        await query.edit_message_text(text, parse_mode='Markdown', reply_markup=get_admin_panel_menu())

    elif data in ("admin_msg_user", "admin_announce", "admin_ban", "admin_unban"):
        prompts = {
            "admin_msg_user": ADMIN_TEXTS['msg_prompt'],
            "admin_announce": ADMIN_TEXTS['announce_prompt'],
            "admin_ban": ADMIN_TEXTS['ban_prompt'],
            "admin_unban": ADMIN_TEXTS['unban_prompt'],
        }
        context.user_data[f"awaiting_{data.split('_')[1]}"] = True
        await query.edit_message_text(prompts[data])

# === ADMİN METİN İŞLEMLERİ ===
async def handle_admin_actions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    text = update.message.text.strip()

    if context.user_data.get('awaiting_msg_user'):
        try:
            uid = int(text)
            context.user_data['msg_target'] = uid
            context.user_data['awaiting_msg_user'] = False
            context.user_data['awaiting_msg_text'] = True
            await update.message.reply_text(ADMIN_TEXTS['msg_text_prompt'].format(uid=uid))
        except:
            await update.message.reply_text("❌ Geçersiz ID!")

    elif context.user_data.get('awaiting_msg_text'):
        target = context.user_data.pop('msg_target', None)
        context.user_data['awaiting_msg_text'] = False
        try:
            await context.bot.send_message(target, f"✉️ *Admin'den mesaj:*\n\n{text}", parse_mode='Markdown')
            await update.message.reply_text(ADMIN_TEXTS['msg_sent'], reply_markup=get_admin_panel_menu())
        except:
            await update.message.reply_text("❌ Gönderilemedi (kullanıcı botu engellemiş olabilir).", reply_markup=get_admin_panel_menu())

    elif context.user_data.get('awaiting_announce'):
        approved = [uid for uid, d in user_data.items() if d.get('approved') and not d.get('banned') and uid != ADMIN_ID]
        count = 0
        for uid in approved:
            try:
                await context.bot.send_message(uid, f"📢 *DUYURU*\n\n{text}", parse_mode='Markdown')
                count += 1
            except:
                pass
        await update.message.reply_text(f"{ADMIN_TEXTS['announce_sent']} ({count} kullanıcıya)", reply_markup=get_admin_panel_menu())
        context.user_data['awaiting_announce'] = False

    elif context.user_data.get('awaiting_ban'):
        try:
            uid = int(text)
            user_data.setdefault(uid, {})['banned'] = True
            user_data[uid]['approved'] = False
            await context.bot.send_message(uid, "🚫 Bot tarafından banlandın.")
            await update.message.reply_text(ADMIN_TEXTS['banned'], reply_markup=get_admin_panel_menu())
        except:
            await update.message.reply_text("❌ Geçersiz ID!")
        context.user_data['awaiting_ban'] = False

    elif context.user_data.get('awaiting_unban'):
        try:
            uid = int(text)
            if uid in user_data:
                user_data[uid]['banned'] = False
                user_data[uid]['approved'] = True
            await context.bot.send_message(uid, "✅ Banın kaldırıldı! /start ile devam edebilirsin.")
            await update.message.reply_text(ADMIN_TEXTS['unbanned'], reply_markup=get_admin_panel_menu())
        except:
            await update.message.reply_text("❌ Geçersiz ID!")
        context.user_data['awaiting_unban'] = False

# === DOSYA YÜKLEME ===
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name

    if is_banned(user_id):
        await update.message.reply_text(t(user_id, 'banned_msg'))
        return

    if user_id != ADMIN_ID and not user_data.get(user_id, {}).get('approved', False):
        await update.message.reply_text(t(user_id, 'permission_req', username=username))
        return

    doc = update.message.document
    if not doc.file_name.lower().endswith('.py'):
        await update.message.reply_text(t(user_id, 'only_py'))
        return

    total = len(user_data[user_id].get('files', [])) + len(user_data[user_id].get('pending', []))
    if total >= MAX_FILES:
        await update.message.reply_text(t(user_id, 'max_files'))
        return

    file = await doc.get_file()
    safe_name = f"{user_id}_{doc.file_name}"
    pending_path = os.path.join(PENDING_FOLDER, safe_name)
    await file.download_to_drive(pending_path)

    user_data[user_id].setdefault('pending', []).append(doc.file_name)

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Onayla & Çalıştır", callback_data=f"approve_file_{user_id}_{doc.file_name}"),
         InlineKeyboardButton("❌ Reddet", callback_data=f"reject_file_{user_id}_{doc.file_name}")]
    ])
    await context.bot.send_document(
        ADMIN_ID,
        doc,
        caption=f"🆕 Yeni dosya!\n👤 @{username}  ID: {user_id}\n📄 {doc.file_name}\nToplam: {total + 1}/5",
        reply_markup=keyboard
    )

    await update.message.reply_text(t(user_id, 'file_uploaded', file=doc.file_name), reply_markup=get_main_menu(user_id))

# === DOSYA ONAY/RED ===
async def file_approval_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.from_user.id != ADMIN_ID:
        return
    await query.answer()

    if query.data.startswith("approve_file_"):
        _, _, uid_str, filename = query.data.split("_", 3)
        uid = int(uid_str)
        pending_path = os.path.join(PENDING_FOLDER, f"{uid}_{filename}")
        final_path = os.path.join(DATA_FOLDER, f"{uid}_{filename}")

        if os.path.exists(pending_path):
            os.rename(pending_path, final_path)

        if filename in user_data[uid].get('pending', []):
            user_data[uid]['pending'].remove(filename)
        user_data[uid].setdefault('files', []).append(filename)

        process = await asyncio.create_subprocess_exec('python3', final_path)
        pid_path = os.path.join(RUNNING_FOLDER, f"{uid}_{filename}.pid")
        with open(pid_path, 'w') as f:
            f.write(str(process.pid))

        await context.bot.send_message(uid, t(uid, 'file_approved', file=filename))
        await query.edit_message_caption(caption=query.message.caption + "\n\n✅ Onaylandı ve çalıştırıldı!")

    elif query.data.startswith("reject_file_"):
        _, _, uid_str, filename = query.data.split("_", 3)
        uid = int(uid_str)
        path = os.path.join(PENDING_FOLDER, f"{uid}_{filename}")
        if os.path.exists(path):
            os.remove(path)
        if filename in user_data[uid].get('pending', []):
            user_data[uid]['pending'].remove(filename)
        await context.bot.send_message(uid, t(uid, 'file_rejected', file=filename))
        await query.edit_message_caption(caption=query.message.caption + "\n\n❌ Reddedildi!")

# === İZİN ONAY/RED ===
async def permission_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.from_user.id != ADMIN_ID:
        return
    await query.answer()

    if query.data.startswith("perm_approve_"):
        uid = int(query.data.split("_")[2])
        user_data.setdefault(uid, {})['approved'] = True
        user_data[uid]['banned'] = False
        await context.bot.send_message(uid, t(uid, 'permission_approved'))
        await query.edit_message_text(query.message.text + "\n\n✅ Onaylandı!")

    elif query.data.startswith("perm_reject_"):
        uid = int(query.data.split("_")[2])
        user_data.setdefault(uid, {})['banned'] = True
        user_data[uid]['approved'] = False
        await context.bot.send_message(uid, t(uid, 'permission_rejected'))
        await query.edit_message_text(query.message.text + "\n\n❌ Reddedildi ve banlandı!")

# === ANA FONKSİYON ===
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_panel))

    app.add_handler(CallbackQueryHandler(language_handler, pattern="^(lang_|change_lang)"))
    app.add_handler(CallbackQueryHandler(button_handler, pattern="^(upload|myfiles|help|back|delete_)"))
    app.add_handler(CallbackQueryHandler(admin_button_handler, pattern="^admin_"))
    app.add_handler(CallbackQueryHandler(permission_handler, pattern="^perm_"))
    app.add_handler(CallbackQueryHandler(file_approval_handler, pattern="^(approve_file_|reject_file_)"))

    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_admin_actions))

    print("🤖 ZORDO -SANAL-VDS Botu Başlatıldı! 🚀")
    app.run_polling()

if __name__ == '__main__':
    main()