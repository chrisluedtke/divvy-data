import datetime, io, random, os
from PIL import Image, ImageDraw, ImageFont


def process_images(source_dir, dest_dir, preview=False):
    if not os.path.exists(dest_dir):
        os.mkdir(dest_dir)

    image_files = os.listdir(source_dir)

    if preview:
        image_files = random.sample(image_files, 1)

    time_font = ImageFont.truetype("Roboto-Thin.ttf", 120)

    for png in image_files:
        image = Image.open(os.path.join(source_dir, png))
        draw = ImageDraw.ImageDraw(image)

        hour = int(png[1:3])
        minute = round(float(png[3:5]+png[-5]+png[-5])/10000*60)

        if hour == 24:
            time_fix = (datetime.datetime(2019, 1, 1, 0, minute) +
                        datetime.timedelta(minutes=15))
        else:
            time_fix = (datetime.datetime(2019, 1, 1, hour, minute) +
                        datetime.timedelta(minutes=15))

    #     draw.line((image.width-200, image.height, image.width-200, 0),
    #               fill=(38, 38, 38), width=350)

        draw.text((image.width-1150,image.height-900),
                  time_fix.strftime('%H'),
                  fill=(100, 100, 100),
                  font=time_font)

        intended_width = image.height-585
        side_crop = (image.width-intended_width)//2
        offset = 0
        image = image.crop((side_crop+offset,
                            0,
                            image.width-side_crop+offset,
                            image.height-26))
        if preview:
            return image.show()

        filename = os.path.join(dest_dir, (f"frame_{str(hour).zfill(2)}_"
                                           f"{str(minute).zfill(2)}.png"))
        image.save(filename, "PNG")
