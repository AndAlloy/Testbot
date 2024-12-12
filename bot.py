import asyncio
import json
import sys
from datetime import datetime
from aiogram import Bot, Dispatcher, Router
from aiogram.types import Message
from aiogram.filters import Command

# File to store messages
DB_FILE = 'messages.json'

# Get API token from command-line argument
if len(sys.argv) < 2 or not sys.argv[1].startswith("-token="):
    print("Usage: python script.py -token=<YOUR_TELEGRAM_BOT_TOKEN>")
    sys.exit(1)

API_TOKEN = sys.argv[1].split("=", 1)[1]

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
router = Router()
dp = Dispatcher()
dp.include_router(router)

# Load saved messages
try:
    with open(DB_FILE, 'r') as f:
        messages_db = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    messages_db = {}

@router.message(Command("start"))
async def start_command(message: Message):
    """Handles the /start command."""
    await message.answer("Welcome! Use /save <message> to save your messages.")

@router.message(Command("save"))
async def save_message(message: Message):
    """Handles the /save command to save messages."""
    user_id = str(message.from_user.id)
    text = message.text.split(" ", 1)

    if len(text) < 2:
        await message.answer("Please provide a message to save. Example: /save My important note.")
        return

    saved_message = text[1]
    
    # Save message to the database
    if user_id not in messages_db:
        messages_db[user_id] = []

    messages_db[user_id].append({
        "message": saved_message,
        "timestamp": datetime.now().isoformat()
    })

    # Write to file
    with open(DB_FILE, 'w') as f:
        json.dump(messages_db, f, indent=4)

    await message.answer("Your message has been saved!")

@router.message(Command("list"))
async def list_messages(message: Message):
    """Handles the /list command to list saved messages."""
    user_id = str(message.from_user.id)

    if user_id not in messages_db or not messages_db[user_id]:
        await message.answer("You have no saved messages.")
        return

    response = "Here are your saved messages:\n"
    for i, entry in enumerate(messages_db[user_id], start=1):
        response += f"{i}. {entry['message']} (saved on {entry['timestamp']})\n"

    await message.answer(response)

async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=API_TOKEN)

    # And the run events dispatching
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
