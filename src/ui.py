import io
import os
import random

import discord
from discord.ext import commands
from PIL import Image


def generate_card_image(cards: list[tuple[str, str]], filename: str) -> discord.File:
    CARD_WIDTH: int = 142
    CARD_HEIGHT: int = 190
    SPACING = 10

    suits: list[str] = ["Hearts", "Clubs", "Diamonds", "Spades"]
    ranks: list[str] = [
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
        "10",
        "J",
        "Q",
        "K",
        "A",
    ]

    def get_offsets(rank: str, suit: str) -> tuple[int, int]:
        y_offset: int = suits.index(suit) * CARD_HEIGHT
        x_offset: int = ranks.index(rank) * CARD_WIDTH
        return x_offset, y_offset

    # I should really update this to be like resources/deck.png but I'll do that later
    base_dir: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    deck_path: str = os.path.join(base_dir, "deck.png")

    deck_img: Image.Image = Image.open(deck_path)

    num_cards: int = len(cards)
    combined_width = (
        CARD_WIDTH * num_cards + SPACING * (num_cards - 1)
        if num_cards > 0
        else CARD_WIDTH
    )
    combined_img = Image.new("RGBA", (combined_width, CARD_HEIGHT))

    for i, (rank, suit) in enumerate(cards):
        x_offset, y_offset = get_offsets(rank, suit)
        card_img = deck_img.crop(
            (x_offset, y_offset, x_offset + CARD_WIDTH, y_offset + CARD_HEIGHT)
        )
        combined_img.paste(card_img, (i * (CARD_WIDTH + SPACING), 0))

    buffer = io.BytesIO()
    combined_img.save(buffer, format="PNG")
    buffer.seek(0)

    return discord.File(fp=buffer, filename=filename)


def setup_poker_ui(bot: commands.Bot) -> None:
    """Setup all poker UI for the bot"""

    suits: list[str] = ["Hearts", "Clubs", "Diamonds", "Spades"]
    ranks: list[str] = [
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
        "10",
        "J",
        "Q",
        "K",
        "A",
    ]
    full_deck: list[tuple[str, str]] = [
        (rank, suit) for suit in suits for rank in ranks
    ]

    @bot.tree.command(name="hand", description="Show your hand")
    async def hand(interaction: discord.Interaction) -> None:
        hand_cards: list[tuple[str, str]] = random.sample(full_deck, 2)

        try:
            file: discord.File = generate_card_image(hand_cards, "hand.png")
            await interaction.response.send_message(file=file, ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(
                f"Error loading card: {e}", ephemeral=True
            )

    @bot.tree.command(name="community", description="Show the community cards")
    async def community(interaction: discord.Interaction) -> None:
        community_cards: list[tuple[str, str]] = random.sample(full_deck, 5)

        try:
            file: discord.File = generate_card_image(community_cards, "community.png")
            await interaction.response.send_message(file=file)
        except Exception as e:
            await interaction.response.send_message(
                f"Error loading community cards: {e}", ephemeral=True
            )
