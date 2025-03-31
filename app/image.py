from PIL import Image, ImageDraw, ImageFont

def make_image_from_list(tasks, output_path):
    width = 576
    line_height = 40
    padding = 20
    height = padding * 2 + line_height * (len(tasks) + 1)

    image = Image.new("1", (width, height), 1)  # 1-bit image, white background
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 28)
    except:
        font = ImageFont.load_default()

    draw.text((padding, padding), "Today's Tasks", font=font, fill=0)
    for i, task in enumerate(tasks):
        draw.text((padding, padding + (i + 1) * line_height), f"[ ] {task}", font=font, fill=0)

    image.save(output_path)