import time
import os
import psutil  # We use the psutil library to check running processes

def is_bot_running(process_name):
    # Check if the process is running by looking for the process name
    for process in psutil.process_iter(attrs=['pid', 'name', 'cmdline']):
        try:
            # Check if the cmdline contains the name of the bot (p.py)
            if process.info['cmdline'] and 'pp.py' in process.info['cmdline']:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            # If the process is not accessible or dead, we skip it
            continue
    return False

def restart_bot():
    # Replace 'python3 pp.py' with the actual command to start your bot
    os.system("python3 pp.py &")  # Start your bot in the background

if __name__ == "__main__":
    bot_process_name = "pp.py"  # The name of your bot's script
    while True:
        if not is_bot_running(bot_process_name):
            print(f"Bot is OFF, checking again in 5 seconds.")
            time.sleep(5)  # Wait for 5 seconds before checking again
            print("Restarting the bot...")
            restart_bot()  # Command to restart your bot
        else:
            print(f"Bot is running, checking again in 1 minute.")
            time.sleep(60)  # Check every 1 minute if the bot is running
