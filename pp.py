import telebot
import subprocess
import time
import json

TOKEN = "7350883849:AAEHzmgpKQQWT8zfX53bgMnVcp0JpT3FfSA"
OWNER_ID = 948895728, 930577300 # Replace with the owner's Telegram ID

bot = telebot.TeleBot(TOKEN)

# Load user data from a JSON file
try:
    with open("users.json", "r") as f:
        users = json.load(f)
except FileNotFoundError:
    users = {"admins": {}, "keys": {}, "approved_users": []}

def save_data():
    with open("users.json", "w") as f:
        json.dump(users, f, indent=4)

# Generate a key with balance deduction
@bot.message_handler(commands=["genkey"])
def generate_key(message):
    user_id = message.from_user.id
    if user_id != OWNER_ID and user_id not in users["admins"]:
        bot.reply_to(message, "Only the owner and admins can generate keys.")
        return

    try:
        args = message.text.split()
        balance = int(args[1].replace("inr", ""))
        
        if user_id == OWNER_ID:  # Owner has unlimited balance
            pass
        elif users["admins"].get(user_id, 0) >= balance:
            users["admins"][user_id] -= balance  # Deduct balance from admin
        else:
            bot.reply_to(message, "Insufficient balance.")
            return

        key = f"IPxKINGYT{int(time.time())}"
        users["keys"][key] = {"balance": balance, "redeemed": False}
        save_data()
        bot.reply_to(message, f"Key Generated: `{key}`\nBalance: {balance} INR", parse_mode="Markdown")
    except Exception:
        bot.reply_to(message, "Usage: /genkey <amount>inr")

# Check account details
@bot.message_handler(commands=["myaccount"])
def my_account(message):
    user_id = message.from_user.id
    if user_id == OWNER_ID:
        bot.reply_to(message, "👑 You are the Owner. Unlimited Balance.")
    elif user_id in users["admins"]:
        balance = users["admins"][user_id]
        bot.reply_to(message, f"🔹 *Admin Account Details:*\n💰 Balance: {balance} INR", parse_mode="Markdown")
    else:
        bot.reply_to(message, "❌ You are not an admin.")

# Redeem a key
@bot.message_handler(commands=["redeem"])
def redeem_key(message):
    try:
        key = message.text.split()[1]
        if key in users["keys"] and not users["keys"][key]["redeemed"]:
            users["keys"][key]["redeemed"] = True
            users["approved_users"].append(message.from_user.id)
            save_data()
            bot.reply_to(message, "✅ Key redeemed successfully! You can now use /babu command.")
        else:
            bot.reply_to(message, "❌ Invalid or already redeemed key.")
    except Exception:
        bot.reply_to(message, "Usage: /redeem <key>")

# Disable a key
@bot.message_handler(commands=["disablekey"])
def disable_key(message):
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "Only the owner can disable keys.")
        return

    try:
        key = message.text.split()[1]
        if key in users["keys"]:
            del users["keys"][key]
            save_data()
            bot.reply_to(message, f"✅ Key `{key}` disabled.", parse_mode="Markdown")
        else:
            bot.reply_to(message, "❌ Key not found.")
    except Exception:
        bot.reply_to(message, "Usage: /disablekey <key>")

# Add an admin
@bot.message_handler(commands=["addadmin"])
def add_admin(message):
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "Only the owner can add admins.")
        return

    try:
        args = message.text.split()
        user_id = int(args[1])
        balance = int(args[2].replace("inr", ""))
        users["admins"][user_id] = balance
        save_data()
        bot.reply_to(message, f"✅ Admin {user_id} added with balance {balance} INR.")
    except Exception:
        bot.reply_to(message, "Usage: /addadmin <userid> <balance>inr")

# Delete an admin
@bot.message_handler(commands=["deladmin"])
def delete_admin(message):
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "Only the owner can remove admins.")
        return

    try:
        user_id = int(message.text.split()[1])
        if user_id in users["admins"]:
            del users["admins"][user_id]
            save_data()
            bot.reply_to(message, f"✅ Admin {user_id} removed.")
        else:
            bot.reply_to(message, "❌ Admin not found.")
    except Exception:
        bot.reply_to(message, "Usage: /deladmin <userid>")

# Broadcast message
@bot.message_handler(commands=["broadcast"])
def broadcast_message(message):
    if message.from_user.id not in users["admins"] and message.from_user.id != OWNER_ID:
        bot.reply_to(message, "Only admins and the owner can broadcast messages.")
        return

    try:
        msg = message.text.replace("/broadcast", "").strip()
        for user in users["approved_users"]:
            bot.send_message(user, f"📢 *Broadcast Message:*\n{msg}", parse_mode="Markdown")
        bot.reply_to(message, "✅ Message broadcasted successfully.")
    except Exception:
        bot.reply_to(message, "❌ Error broadcasting message.")

# Execute binary file
@bot.message_handler(commands=["babu"])
def execute_binary(message):
    if message.from_user.id not in users["approved_users"]:
        bot.reply_to(message, "❌ You need to redeem a valid key to use this command.")
        return

    try:
        args = message.text.split()
        ip, port, duration = args[1], args[2], args[3]
        subprocess.Popen(["./iiiipx", ip, port, duration])
        bot.reply_to(message, f"✅ Executing: `./iiiipx {ip} {port} {duration}`", parse_mode="Markdown")
    except Exception:
        bot.reply_to(message, "Usage: /babu <ip> <port> <time>")

# Check bot uptime
start_time = time.time()
@bot.message_handler(commands=["uptime"])
def uptime(message):
    elapsed = time.time() - start_time
    bot.reply_to(message, f"⏳ Bot has been running for {int(elapsed)} seconds.")

# Start command
@bot.message_handler(commands=["start"])
def welcome(message):
    bot.reply_to(message, "✨ Welcome to the Bot! Use /help for commands.")

# Help command
@bot.message_handler(commands=["help"])
def help_command(message):
    help_text = """
    📜 *Commands List:*
    /genkey <amount>inr - Generate a key (Owner/Admins)
    /redeem <key> - Redeem a key
    /disablekey <key> - Disable a key (Owner)
    /addadmin <id> <balance>inr - Add admin (Owner)
    /deladmin <id> - Remove admin (Owner)
    /broadcast <message> - Send a message to all approved users (Admins & Owner)
    /babu <ip> <port> <time> - Execute binary (Requires redeemed key)
    /uptime - Check bot runtime
    /myaccount - Check your balance and details (Admins only)
    """
    bot.reply_to(message, help_text, parse_mode="Markdown")

bot.polling(none_stop=True)
