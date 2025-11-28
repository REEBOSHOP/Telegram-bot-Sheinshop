
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
import json, os, time, io

# --- CONFIG ---
TOKEN = "8519448454:AAFZYiLzHSHaoeRjRYLMgoAabAvuZ0-7mhA"
ADMIN_ID = 1922094509
DATA_FILE = "data.json"

PAYMENT_DETAILS = {
    "BINANCE": "Binance ID - 858331046",
    "TRC20": "USDT-TRC20 - TWGxHiP4mnZ8QvsQAWAVP4Eq8wqhmav7vu",
    "BEP20": "USDT-BEP20 - 0x2ac82470586eb7dff041b60ef80678ddc4650e0c",
}
PAYMENT_LABELS = {
    "BINANCE": "Binance",
    "TRC20": "USDT (TRC20)",
    "BEP20": "USDT (BEP20)",
}

TERMS_TEXT = (
    "⚠️ 𝙎𝙩𝙤𝙧𝙚 𝙍𝙪𝙡𝙚𝙨 – 𝙍𝙚𝙖𝙙 𝘽𝙚𝙛𝙤𝙧𝙚 𝘽𝙪𝙮𝙞𝙣𝙜! ⚠️\n"
    "1️⃣𝘓𝘰𝘨𝘪𝘯 𝘞𝘢𝘳𝘳𝘢𝘯𝘵𝘺 𝘗𝘳𝘰𝘷𝘪𝘥𝘦𝘥 – 𝘠𝘰𝘶 𝘨𝘦𝘵 𝘢 𝘸𝘰𝘳𝘬𝘪𝘯𝘨 𝘢𝘤𝘤𝘰𝘶𝘯𝘵 𝘢𝘵 𝘱𝘶𝘳𝘤𝘩𝘢𝘴𝘦. Checking time 10 minutes to 30 minutes after purchase.\n"
    "2️⃣𝘚𝘵𝘢𝘺 𝘚𝘢𝘧𝘦 – 𝘜𝘴𝘦 𝘱𝘳𝘰𝘹𝘪𝘦𝘴 & 𝘢 𝘨𝘰𝘰𝘥 𝘧𝘪𝘯𝘨𝘦𝘳𝘱𝘳𝘪𝘯𝘵 𝘣𝘳𝘰𝘸𝘴𝘦𝘳 𝘵𝘰 𝘢𝘷𝘰𝘪𝘥 𝘥𝘦𝘵𝘦𝘤𝘵𝘪𝘰𝘯.\n"
    "3️⃣𝘕𝘰𝘵 𝘙𝘦𝘴𝘱𝘰𝘯𝘴𝘪𝘣𝘭𝘦 – 𝘠𝘰𝘶𝘳 𝘢𝘤𝘵𝘪𝘰𝘯𝘴 𝘢𝘧𝘵𝘦𝘳 𝘱𝘶𝘳𝘤𝘩𝘢𝘴𝘦 𝘢𝘳𝘦 𝘺𝘰𝘶𝘳 𝘳𝘦𝘴𝘱𝘰𝘯𝘴𝘪𝘣𝘪𝘭𝘪𝘵𝘺\n"
    "💯 𝙁𝙤𝙡𝙡𝙤𝙬 𝙩𝙝𝙚 𝙧𝙪𝙡𝙚𝙨, 𝙨𝙩𝙖𝙮 𝙨𝙚𝙘𝙪𝙧𝙚, 𝙖𝙣𝙙 𝙚𝙣𝙟𝙤𝙮 𝙮𝙤𝙪𝙧 𝙥𝙪𝙧𝙘𝙝𝙖𝙨𝙚! 💯\n"
    "⚜️Any questions, problem solving, please contact us at the contact below.\n"
    "⚙️ @Brankplar (Telegram)\n"
)

def default_products():
    return [
        {"name": "GCP300 USA 🇺🇸", "price": "$16", "qty": 10},
        {"name": "GCP300 UK 🇬🇧", "price": "$15.5", "qty": 5},
        {"name": "Hetzner limit 40", "price": "$30", "qty": 3},
        {"name": "Gmail accounts", "price": "$0.25", "qty": 25},
        {"name": "Outlook mails", "price": "$0.15", "qty": 30},
        {"name": "Linode random IP", "price": "$8", "qty": 7},
        {"name": "Azure free trial", "price": "$7", "qty": 6},
        {"name": "AWS 32vCPU (AI SUPPORTED)", "price": "$13.5", "qty": 10},
        {"name": "AWS 8vCPU", "price": "$5", "qty": 8},
        {"name": "OPENAI $1,000 CREDITS", "price": "400$", "qty": 1},
        {"name": "OPENAI $2,500 CREDITS", "price": "1200$", "qty": 1},
    ]

def load_data():
    if not os.path.exists(DATA_FILE):
        data = {"products": default_products(), "users": [], "orders": []}
        save_data(data)
        return data
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(d):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)

data = load_data()
awaiting_support = set()

def add_user(user):
    uid = user.id
    uname = user.username or ""
    if not any(x["id"] == uid for x in data.get("users", [])):
        data["users"].append({"id": uid, "username": uname})
        save_data(data)

def find_product(name):
    for p in data["products"]:
        if p["name"].lower() == name.lower():
            return p
    return None

def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🛒 Buy", callback_data="menu_buy")],
        [InlineKeyboardButton("💬 Support", callback_data="menu_support")],
        [InlineKeyboardButton("📦 Availability", callback_data="menu_availability")],
        [InlineKeyboardButton("📜 Terms & Conditions", callback_data="menu_terms")],
    ])

def buy_menu_keyboard():
    rows = []
    for p in data["products"]:
        if p["qty"] > 0:
            label = f"{p['name']} — {p['price']} (Stock: {p['qty']})"
            rows.append([InlineKeyboardButton(label, callback_data=f"buy_{p['name']}")])
    rows.append([InlineKeyboardButton("⬅ Back", callback_data="menu_home")])
    return InlineKeyboardMarkup(rows)

def support_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💬 Chat on Telegram", url="https://t.me/brankplar")],
        [InlineKeyboardButton("📩 Contact Admin", callback_data="contact_admin")],
        [InlineKeyboardButton("⬅ Back", callback_data="menu_home")]
    ])

def payment_method_keyboard(product_name):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Binance", callback_data=f"pay_BINANCE_{product_name}")],
        [InlineKeyboardButton("USDT TRC20", callback_data=f"pay_TRC20_{product_name}")],
        [InlineKeyboardButton("USDT BEP20", callback_data=f"pay_BEP20_{product_name}")],
        [InlineKeyboardButton("⬅ Back", callback_data="menu_buy")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    add_user(update.effective_user)
    await update.message.reply_text("Welcome! What would you like to do?", reply_markup=main_menu_keyboard())

async def menu_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    add_user(query.from_user)
    data_choice = query.data

    if data_choice == "menu_buy":
        await query.edit_message_text("🛒 Choose a product:", reply_markup=buy_menu_keyboard())
    elif data_choice == "menu_support":
        await query.edit_message_text("Support options:", reply_markup=support_keyboard())
    elif data_choice == "menu_availability":
        lines = []
        for p in data["products"]:
            status = f"{p['price']} — Stock: {p['qty']}" if p["qty"] > 0 else "Out of stock"
            lines.append(f"• {p['name']} — {status}")
        text = "📦 Current Availability:\n" + "\n".join(lines)
        await query.edit_message_text(text, reply_markup=main_menu_keyboard())
    elif data_choice == "menu_terms":
        await query.edit_message_text(TERMS_TEXT, reply_markup=main_menu_keyboard())
    elif data_choice == "menu_home":
        await query.edit_message_text("Welcome! What would you like to do?", reply_markup=main_menu_keyboard())
    elif data_choice.startswith("buy_"):
        name = data_choice[4:]
        p = find_product(name)
        if not p:
            await query.edit_message_text("❌ Product not found.", reply_markup=buy_menu_keyboard())
            return
        if p["qty"] <= 0:
            await query.edit_message_text("❌ This product is currently out of stock.", reply_markup=buy_menu_keyboard())
            return
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Confirm Purchase (1 unit)", callback_data=f"confirm_{p['name']}")],
            [InlineKeyboardButton("⬅ Back", callback_data="menu_buy")]
        ])
        await query.edit_message_text(f"**{p['name']}**\nPrice: {p['price']}\nStock: {p['qty']}\n\nProceed to buy?",
                                      parse_mode="Markdown", reply_markup=kb)
    elif data_choice.startswith("confirm_"):
        name = data_choice[8:]
        p = find_product(name)
        if not p:
            await query.edit_message_text("❌ Product not found.", reply_markup=buy_menu_keyboard())
            return
        if p["qty"] <= 0:
            await query.edit_message_text("❌ This product just went out of stock.", reply_markup=buy_menu_keyboard())
            return
        # decrement stock
        p["qty"] -= 1
        save_data(data)

        # Ask for payment method
        await query.edit_message_text(
            f"📦 {p['name']}\n💵 {p['price']}\n\nSelect your payment method:",
            reply_markup=payment_method_keyboard(p['name'])
        )
    elif data_choice.startswith("pay_"):
        _, method, name = data_choice.split("_", 2)
        p = find_product(name)
        if not p:
            await query.edit_message_text("❌ Product not found.", reply_markup=buy_menu_keyboard())
            return

        detail = PAYMENT_DETAILS.get(method, "Payment method not recognized.")
        pay_text = f"{PAYMENT_LABELS.get(method, method)} Details:\n{detail}\n\nAfter payment, send proof to @stein_black"
        pay_kb = InlineKeyboardMarkup([[InlineKeyboardButton("💬 Contact Support", url="https://t.me/stein_black")],
                                       [InlineKeyboardButton("⬅ Back to Shop", callback_data="menu_buy")]])
        await query.edit_message_text(pay_text, reply_markup=pay_kb)

        # Log order
        user = query.from_user
        ts = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        order = {
            "timestamp": ts,
            "product": p["name"],
            "qty": 1,
            "buyer_id": user.id,
            "username": user.username or "",
            "method": PAYMENT_LABELS.get(method, method)
        }
        data.setdefault("orders", []).append(order)
        save_data(data)

        # Notify admin
        note = (f"🛒 New Order\nProduct: {p['name']}\nPrice: {p['price']}\n"
                f"Buyer: @{user.username or user.id} (ID: {user.id})\n"
                f"Method: {order['method']}\nTime (UTC): {ts}")
        await context.bot.send_message(chat_id=ADMIN_ID, text=note)

    elif data_choice == "contact_admin":
        awaiting_support.add(query.from_user.id)
        await query.edit_message_text("📩 Please type your message now. I will deliver it to the admin.", reply_markup=support_keyboard())

async def incoming_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user)
    if user.id in awaiting_support:
        msg = update.message.text
        awaiting_support.discard(user.id)
        header = f"📩 Support message from @{user.username or user.id} (ID: {user.id}):\n\n{msg}"
        await context.bot.send_message(chat_id=ADMIN_ID, text=header)
        await update.message.reply_text("✅ Sent to admin. You'll receive a reply here.")
    else:
        return

async def reply_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("🚫 Access denied.")
        return
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /reply <user_id> <message>")
        return
    try:
        target_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("User ID must be a number.")
        return
    message_text = " ".join(context.args[1:])
    try:
        await context.bot.send_message(chat_id=target_id, text=f"📬 Admin reply:\n{message_text}")
        await update.message.reply_text("✅ Sent.")
    except Exception as e:
        await update.message.reply_text(f"Failed to send: {e}")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("🚫 Access denied.")
        return
    if not context.args:
        await update.message.reply_text("Usage: /broadcast <message>")
        return
    msg = " ".join(context.args)
    sent = 0
    failed = 0
    for u in data.get("users", []):
        try:
            await context.bot.send_message(chat_id=u["id"], text=msg)
            sent += 1
        except Exception:
            failed += 1
    await update.message.reply_text(f"Broadcast done. Sent: {sent}, Failed: {failed}")

async def stock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("🚫 Access denied.")
        return
    lines = [f"• {p['name']} — {p['price']} — qty: {p['qty']}" for p in data["products"]]
    await update.message.reply_text("📦 Stock:\n" + "\n".join(lines))

def split_name_value(args):
    if len(args) < 2:
        return None, None
    value = args[-1]
    name = " ".join(args[:-1])
    return name, value

async def addstock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("🚫 Access denied.")
        return
    name, qty = split_name_value(context.args)
    if not name or not qty or not qty.isdigit():
        await update.message.reply_text("Usage: /addstock <ProductName> <Quantity>")
        return
    p = find_product(name)
    if not p:
        await update.message.reply_text("Product not found.")
        return
    p["qty"] += int(qty)
    save_data(data)
    await update.message.reply_text(f"✅ Added {qty} to '{p['name']}'. New qty: {p['qty']}")

async def removestock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("🚫 Access denied.")
        return
    name, qty = split_name_value(context.args)
    if not name or not qty or not qty.isdigit():
        await update.message.reply_text("Usage: /removestock <ProductName> <Quantity>")
        return
    p = find_product(name)
    if not p:
        await update.message.reply_text("Product not found.")
        return
    p["qty"] = max(0, p["qty"] - int(qty))
    save_data(data)
    await update.message.reply_text(f"✅ Removed {qty} from '{p['name']}'. New qty: {p['qty']}")

async def setprice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("🚫 Access denied.")
        return
    name, price = split_name_value(context.args)
    if not name or not price:
        await update.message.reply_text("Usage: /setprice <ProductName> <$Price>   e.g. /setprice Gmail accounts $0.25")
        return
    p = find_product(name)
    if not p:
        await update.message.reply_text("Product not found.")
        return
    if not price.startswith("$"):
        price = "$" + price
    p["price"] = price
    save_data(data)
    await update.message.reply_text(f"✅ New price for '{p['name']}': {p['price']}")

async def addproduct(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("🚫 Access denied.")
        return
    if len(context.args) < 3:
        await update.message.reply_text("Usage: /addproduct <Name> <$Price> <Qty>")
        return
    *name_parts, price, qty = context.args
    name = " ".join(name_parts)
    if not qty.isdigit():
        await update.message.reply_text("Quantity must be a number.")
        return
    if not price.startswith("$"):
        price = "$" + price
    if find_product(name):
        await update.message.reply_text("Product already exists.")
        return
    data["products"].append({"name": name, "price": price, "qty": int(qty)})
    save_data(data)
    await update.message.reply_text(f"✅ Added product: {name} — {price} — qty {qty}")

async def deleteproduct(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("🚫 Access denied.")
        return
    name = " ".join(context.args)
    if not name:
        await update.message.reply_text("Usage: /deleteproduct <ProductName>")
        return
    p = find_product(name)
    if not p:
        await update.message.reply_text("Product not found.")
        return
    data["products"] = [x for x in data["products"] if x["name"].lower() != name.lower()]
    save_data(data)
    await update.message.reply_text(f"🗑 Deleted product '{name}'.")

async def orders_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("🚫 Access denied.")
        return
    orders = data.get("orders", [])
    if not orders:
        await update.message.reply_text("🧾 No orders recorded yet.")
        return
    lines = []
    for o in reversed(orders):
        uname = ("@" + o["username"]) if o.get("username") else "N/A"
        lines.append(f"{o['timestamp']} | {o['product']} | {o['qty']} pcs | User ID: {o['buyer_id']} | Username: {uname} | Method: {o.get('method','-')}")
    text = "🛒 Orders List:\n" + "\n".join(lines)
    if len(text) > 3500:
        # send as file
        buf = io.StringIO("\n".join(lines))
        buf.seek(0)
        await context.bot.send_document(chat_id=ADMIN_ID, document=buf, filename="orders.txt", caption="🛒 Orders List")
    else:
        await update.message.reply_text(text)

async def clearorders_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("🚫 Access denied.")
        return
    data["orders"] = []
    save_data(data)
    await update.message.reply_text("🧹 Orders cleared.")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("Commands: /start")
        return
    txt = (
        "👑 Admin Commands:\n"
        "/stock — show all products\n"
        "/addstock <Name> <Qty>\n"
        "/removestock <Name> <Qty>\n"
        "/setprice <Name> <$Price>\n"
        "/addproduct <Name> <$Price> <Qty>\n"
        "/deleteproduct <Name>\n"
        "/orders — show all orders (file if too long)\n"
        "/clearorders — wipe order history\n"
        "/broadcast <message>\n"
        "/reply <user_id> <message>"
    )
    await update.message.reply_text(txt)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CallbackQueryHandler(menu_router))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, incoming_text))
    # Admin
    app.add_handler(CommandHandler("stock", stock))
    app.add_handler(CommandHandler("addstock", addstock))
    app.add_handler(CommandHandler("removestock", removestock))
    app.add_handler(CommandHandler("setprice", setprice))
    app.add_handler(CommandHandler("addproduct", addproduct))
    app.add_handler(CommandHandler("deleteproduct", deleteproduct))
    app.add_handler(CommandHandler("orders", orders_cmd))
    app.add_handler(CommandHandler("clearorders", clearorders_cmd))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("reply", reply_cmd))
    app.run_polling()

if __name__ == "__main__":
    main()
