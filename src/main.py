import os
import time
from typing import Optional

import discord
from discord.ext import commands
from dotenv import load_dotenv

from database import *
from database import channel_is_table, update_table_last_message_time
from helpers import setup_helper_commands
from poker import setup_poker_commands
from timer import setup_table_timer
from ui import setup_poker_ui

load_dotenv()

TOKEN: Optional[str] = os.getenv("TOKEN")

if TOKEN is None:
    raise ValueError(
        "TOKEN is not set. Set it in the .env file as TOKEN=your_token_here"
    )


bot: commands.Bot = commands.Bot(command_prefix="$", intents=discord.Intents.all())

start_time: float = time.time()


@bot.event
async def on_member_join(member: discord.Member) -> None:
    add_user(member.id)


@bot.event
async def on_ready() -> None:
    print(f"{bot.user} has connected to Discord!")

    create_tables()

    # Setup helper commands
    setup_helper_commands(bot)
    setup_poker_commands(bot)
    setup_poker_ui(bot)

    # Setup table timer
    setup_table_timer(bot)

    await bot.tree.sync()

    end_time: float = time.time()

    elapsed_time: float = end_time - start_time

    print("Time to start up", round(elapsed_time, 2), "seconds")


@bot.event
async def on_message(message: discord.Message) -> None:
    # Only process messages in table threads
    if isinstance(message.channel, discord.Thread) and channel_is_table(
        message.channel.id
    ):
        update_table_last_message_time(message.channel.id)

    # Let the bot process commands
    await bot.process_commands(message)


if __name__ == "__main__":
    bot.run(TOKEN)
