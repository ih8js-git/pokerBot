import os

from PIL import Image


def combine_sprites() -> None:
    base_dir: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    deck_path: str = os.path.join(base_dir, "8BitDeck_opt2.png")
    enhancers_path: str = os.path.join(base_dir, "Enhancers.png")
    output_path: str = os.path.join(base_dir, "deck.png")

    deck_img: Image.Image = Image.open(deck_path).convert("RGBA")
    enhancers_img: Image.Image = Image.open(enhancers_path).convert("RGBA")

    CARD_WIDTH: int = 142
    CARD_HEIGHT: int = 190

    # The second background on the first row
    bg_box: tuple[int, int, int, int] = (CARD_WIDTH, 0, CARD_WIDTH * 2, CARD_HEIGHT)
    card_bg: Image.Image = enhancers_img.crop(bg_box)

    out_img: Image.Image = Image.new("RGBA", deck_img.size)

    COLS: int = 13
    ROWS: int = 4
    for r in range(ROWS):
        for c in range(COLS):
            x: int = c * CARD_WIDTH
            y: int = r * CARD_HEIGHT
            out_img.paste(card_bg, (x, y))

    # Paste the original deck over the backgrounds
    out_img.paste(deck_img, (0, 0), deck_img)

    out_img.save(output_path)
    print(f"Successfully created {output_path}")


if __name__ == "__main__":
    combine_sprites()
