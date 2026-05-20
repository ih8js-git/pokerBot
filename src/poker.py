import discord
from discord.ext import commands

from database import (add_table, add_user_to_table, channel_is_table,
                      delete_table, get_table_name, get_user_data,
                      remove_user_from_table, user_is_in_table,
                      user_is_owner_of_table)

try:
    from poker_engine import generate_hand

    HAS_RUST = True
except ImportError:
    HAS_RUST = False


def setup_poker_commands(bot: commands.Bot) -> None:
    """Setup all poker commands for the bot"""

    # Table management
    @bot.tree.command(name="create", description="Create a poker table")
    async def create(
        interaction: discord.Interaction,
        temp_money: bool = False,
        min_bet: int = 5,
        max_bet: int = 0,
        table_name: str = "",
    ) -> None:
        discord_user: discord.User | discord.Member = interaction.user
        discord_user_id: int = discord_user.id
        discord_user_name: str = discord_user.display_name

        # Check if the user exists in the database
        if not get_user_data(discord_user_id):
            await interaction.response.send_message(
                "You don't exist in the database! Use `/init` to initialize your account."
            )
            return

        # In case of no max bet
        if max_bet == 0:
            max_bet = min_bet * 100

        # In case of no table name
        if table_name == "":
            table_name = f"{discord_user_name}'s Table"

        # Check if the channel supports creating threads
        if not isinstance(
            interaction.channel, (discord.TextChannel, discord.ForumChannel)
        ):
            await interaction.response.send_message(
                "This command can only be used in text channels or forum channels! NOT TABLES!"
            )
            return

        try:
            # Send initial response to acknowledge the command
            await interaction.response.send_message(
                f"Creating table `{table_name}`, Temp money: {temp_money}, Min bet: {min_bet}, Max bet: {max_bet}"
            )

            # Create thread with the table name
            # TODO: Clean up tables manually so that we can remove them from the database
            if isinstance(interaction.channel, discord.TextChannel):
                thread = await interaction.channel.create_thread(
                    name=table_name,
                    type=discord.ChannelType.public_thread,
                )
            else:
                await interaction.followup.send("❌ Unsupported channel type!")
                return

            # Create a message in the thread
            await thread.send(
                f"🎰 **Table {table_name}** created!\n"
                f"💸 Temp money: {temp_money}\n"
                f"💰 Min bet: {min_bet}\n"
                f"💎 Max bet: {max_bet}\n"
                f"👤 Created by: {discord_user.mention}\n"
                f"⏰ **Auto-delete:** This table will be automatically deleted after 5 minutes of inactivity"
            )

            add_table(
                thread.id,
                discord_user_id,
                table_name,
                temp_money,
                min_bet,
                max_bet,
            )

            add_user_to_table(discord_user_id, thread.id)

        except discord.Forbidden:
            await interaction.followup.send(
                "❌ I don't have permission to create threads in this channel!"
            )
        except Exception as e:
            await interaction.followup.send(f"❌ Failed to create table: {str(e)}")

    @bot.tree.command(name="join", description="Join's the current table")
    async def join(interaction: discord.Interaction) -> None:
        if interaction.channel is None:
            await interaction.response.send_message(
                "This command can only be used in a text channel with a table!"
            )
            return

        channel_id: int = interaction.channel.id
        discord_user: discord.User | discord.Member = interaction.user
        discord_user_id: int = discord_user.id

        if not channel_is_table(channel_id):
            await interaction.response.send_message(
                "This channel is not a table! Use `/create` to create a table."
            )
            return

        if user_is_in_table(discord_user_id):
            table_name: str = get_table_name(discord_user_id)
            await interaction.response.send_message(
                f"You are already in a table, {table_name}!",
                ephemeral=True,
            )
            return

        # Add the user to the table
        add_user_to_table(discord_user_id, channel_id)
        await interaction.response.send_message(
            f"{discord_user.display_name} joined the table!"
        )

    @bot.tree.command(name="delete", description="Deletes the current table")
    async def delete(interaction: discord.Interaction) -> None:
        if interaction.channel is None:
            await interaction.response.send_message(
                "This command can only be used in a text channel with a table!"
            )
            return

        channel_id: int = interaction.channel.id
        discord_user: discord.User | discord.Member = interaction.user
        discord_user_id: int = discord_user.id

        if not channel_is_table(channel_id):
            await interaction.response.send_message(
                "This channel is not a table! Use `/create` to create a table.",
                ephemeral=True,
            )
            return

        if not user_is_owner_of_table(discord_user_id, channel_id):
            await interaction.response.send_message(
                "You are not the owner of this table! Use `/create` to create a table.",
                ephemeral=True,
            )
            return
        # This check is useless because the channel_is_table function checks if the channel is a table
        # and all tables are threads, but it makes mypy happy, because else it might not have the .delete() method
        if not isinstance(interaction.channel, discord.Thread):
            await interaction.response.send_message(
                "This command can only be used in a thread with a table!"
            )
            return

        # Delete the table
        delete_table(channel_id)
        remove_user_from_table(discord_user_id)
        await interaction.response.send_message("Deleting table...", ephemeral=True)
        await interaction.channel.delete()

    @bot.tree.command(name="list", description="List's everyone in the current table")
    async def list(interaction: discord.Interaction) -> None:
        pass

    @bot.tree.command(name="leave", description="Leave's the current table")
    async def leave(interaction: discord.Interaction) -> None:
        pass

    @bot.tree.command(name="start", description="Start's the current table")
    async def start(interaction: discord.Interaction) -> None:
        pass

    # Rust test command
    @bot.tree.command(name="deal", description="Deal a hand using Rust engine")
    async def deal(interaction: discord.Interaction, cards: int = 5) -> None:
        if not HAS_RUST:
            await interaction.response.send_message(
                "Rust engine not loaded. Build it with `maturin develop` in poker-engine/"
            )
            return
        hand = generate_hand(cards)
        await interaction.response.send_message(f"🃏 Your hand: {' '.join(hand)}")

    # Actions
    @bot.tree.command(name="check", description="Check's the current table")
    async def check(interaction: discord.Interaction) -> None:
        pass

    @bot.tree.command(name="call", description="Call's the current table")
    async def call(interaction: discord.Interaction) -> None:
        pass

    @bot.tree.command(name="raise", description="Raise's the current table")
    async def raise_command(interaction: discord.Interaction, amount: int) -> None:
        pass

    @bot.tree.command(name="fold", description="Fold's the current table")
    async def fold(interaction: discord.Interaction) -> None:
        pass

    @bot.tree.command(name="all-in", description="All-in's the current table")
    async def all_in(interaction: discord.Interaction) -> None:
        pass

    pass
