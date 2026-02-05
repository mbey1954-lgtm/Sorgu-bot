import subprocess
import tempfile
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8500441874:AAGvjXGC0zqH6si8et1yBYkb_PV8mHmmnok"
ALLOWED_USERS = [8444268448]  # İzin verilen kullanıcı ID'leri, boş bırakırsanız herkes kullanabilir

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Merhaba! Bana .py dosyası gönder, çalıştırayım.")

async def handle_py_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if ALLOWED_USERS and user_id not in ALLOWED_USERS:
        await update.message.reply_text("⛔ Yetkiniz yok!")
        return

    document = update.message.document
    if not document.file_name.endswith('.py'):
        return

    await update.message.reply_text("📥 Dosya alındı, işleniyor...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, document.file_name)
        
        file = await context.bot.get_file(document.file_id)
        await file.download_to_drive(file_path)
        
        await install_requirements(file_path, update)
        await run_python_file(file_path, update)

async def install_requirements(file_path, update):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        imports = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('import ') or line.startswith('from '):
                parts = line.split()
                if len(parts) > 1:
                    module = parts[1].split('.')[0]
                    if module not in imports and module != '__future__':
                        imports.append(module)
        
        if imports:
            await update.message.reply_text(f"🔧 Paketler kuruluyor: {', '.join(imports)}")
            for package in imports:
                try:
                    subprocess.check_call(['pip', 'install', package], 
                                         stdout=subprocess.DEVNULL, 
                                         stderr=subprocess.DEVNULL)
                except:
                    continue
        
    except Exception as e:
        print(f"Requirements error: {e}")

async def run_python_file(file_path, update):
    try:
        await update.message.reply_text("🚀 Kod çalıştırılıyor...")
        
        result = subprocess.run(['python', file_path], 
                              capture_output=True, 
                              text=True, 
                              timeout=30)
        
        output = result.stdout + result.stderr
        
        if len(output) > 4000:
            await update.message.reply_text("📤 Çıktı çok uzun, ilk 4000 karakter:")
            await update.message.reply_text(output[:4000])
        elif output:
            await update.message.reply_text(f"Çıktı:\n```\n{output}\n```", parse_mode='Markdown')
        else:
            await update.message.reply_text("✅ Kod çalıştı, çıktı yok.")
            
    except subprocess.TimeoutExpired:
        await update.message.reply_text("⏰ Zaman aşımı! Kod 30 saniyeden uzun sürdü.")
    except Exception as e:
        await update.message.reply_text(f"❌ Hata: {str(e)}")

def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_py_file))
    
    print("🤖 Bot çalışıyor...")
    app.run_polling()

if __name__ == "__main__":
    main()_menu())

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
