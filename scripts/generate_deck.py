from PIL import Image
import os

def combine_sprites():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    deck_path = os.path.join(base_dir, "8BitDeck_opt2.png")
    enhancers_path = os.path.join(base_dir, "Enhancers.png")
    output_path = os.path.join(base_dir, "deck.png")

    deck_img = Image.open(deck_path).convert("RGBA")
    enhancers_img = Image.open(enhancers_path).convert("RGBA")

    card_width = 142
    card_height = 190

    # The second background on the first row
    bg_box = (card_width, 0, card_width * 2, card_height)
    card_bg = enhancers_img.crop(bg_box)

    out_img = Image.new("RGBA", deck_img.size)

    cols = 13
    rows = 4
    for r in range(rows):
        for c in range(cols):
            x = c * card_width
            y = r * card_height
            out_img.paste(card_bg, (x, y))

    # Paste the original deck over the backgrounds
    out_img.paste(deck_img, (0, 0), deck_img)

    out_img.save(output_path)
    print(f"Successfully created {output_path}")

if __name__ == "__main__":
    combine_sprites()
