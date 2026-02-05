import os
import subprocess
import sys
import importlib
from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, filters
from telegram.ext import Application

# === AYARLAR ===
TOKEN = "8500441874:AAGvjXGC0zqH6si8et1yBYkb_PV8mHmmnok"  # Bot tokeninizi buraya ekleyin
DATA_FOLDER = "user_files"
os.makedirs(DATA_FOLDER, exist_ok=True)

# Kullanıcı dosyalarını kaydedeceğimiz alan
user_data = {}

# === EXTERNAL PACKAGE CHECK ===
def check_and_install_package(package_name):
    """ Package'i kontrol et ve yoksa yükle """
    try:
        importlib.import_module(package_name)
    except ImportError:
        print(f"Yüklenmemiş {package_name} paketi. Yükleniyor...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])

# === DOSYA YÜKLEME İŞLEMLERİ ===
async def upload(update: Update, context):
    user_id = update.message.from_user.id
    file = update.message.document

    # Kullanıcıdan dosyayı al
    if file.mime_type != 'application/x-python':
        await update.message.reply_text("❌ Sadece `.py` dosyaları kabul ediyorum!")
        return

    # Dosya adını kaydet
    file_name = file.file_name
    file_path = os.path.join(DATA_FOLDER, f"{user_id}_{file_name}")

    # Dosyayı kaydet
    new_file = await file.get_file()
    await new_file.download(file_path)

    # Kullanıcıya yükleme tamamlandığını bildir
    await update.message.reply_text(f"📤 {file_name} yüklendi!\n⏳ Admin onayı bekleniyor...")

    # Kullanıcı verilerini güncelle
    user_data.setdefault(user_id, {'files': []})['files'].append(file_name)

# === DOSYAYI ÇALIŞTIRMA ===
async def run_script(update: Update, context):
    user_id = update.message.from_user.id

    # Onaylı kullanıcılardan sadece çalıştırma izni
    if not user_data.get(user_id, {}).get('approved', False):
        await update.message.reply_text("❌ Onaylı bir kullanıcı değilsiniz!")
        return

    # Kullanıcının yüklendiği dosyaları al
    files = user_data.get(user_id, {}).get('files', [])
    if not files:
        await update.message.reply_text("❌ Yüklü dosya yok!")
        return

    # Dosyayı çalıştırmadan önce paket kontrolü ve yükleme
    for file_name in files:
        file_path = os.path.join(DATA_FOLDER, f"{user_id}_{file_name}")
        
        # Dosyayı analiz et ve gereken paketleri yükle
        try:
            # Dosyadaki bağımlılıkları kontrol et (import komutlarını al)
            with open(file_path, 'r') as f:
                content = f.read()

            # Bağımlılıkları analiz et ve eksikleri yükle
            packages = []
            for line in content.splitlines():
                if line.startswith("import "):
                    package = line.split()[1]
                    packages.append(package)
            
            # Bağımlılıkları yükle
            for package in packages:
                check_and_install_package(package)

            # Dosyayı çalıştır
            result = subprocess.run(['python', file_path], capture_output=True, text=True)
            # Çıktıları kullanıcıya gönder
            if result.returncode == 0:
                await update.message.reply_text(f"✅ {file_name} başarıyla çalıştırıldı!")
            else:
                await update.message.reply_text(f"❌ {file_name} çalıştırılırken hata oluştu:\n{result.stderr}")
        except Exception as e:
            await update.message.reply_text(f"❌ Dosya çalıştırılamadı: {str(e)}")

# === Komutları Bağlama ===
def main():
    # Bot tokeni burada tanımlandı
    application = Application.builder().token(TOKEN).build()

    # Yükleme ve çalıştırma komutlarını ekleyelim
    upload_handler = MessageHandler(filters.Document.MIME_TYPE("application/x-python"), upload)
    application.add_handler(upload_handler)

    run_handler = CommandHandler("run", run_script)
    application.add_handler(run_handler)

    application.run_polling()

if __name__ == "__main__":
    main()boardButton("❌ Reddet/Banla", callback_data=f"perm_reject_{user_id}")]
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
