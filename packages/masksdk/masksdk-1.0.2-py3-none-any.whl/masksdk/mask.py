from PIL import Image, ImageFilter, ImageDraw

leak_height = 0.167


def blurring(image, boxes, degree):
    for b in boxes:
        class_name = b['class_name']
        if class_name == "face":
            mask = Image.new("L", image.size)
            draw = ImageDraw.Draw(mask)
            ymin, ymax = b['y_min'], b['y_max']
            ymin2 = min((ymin + max((ymax - ymin), 0) * leak_height), ymax)
            draw.ellipse((b['x_min'], ymin2, b['x_max'], ymax), fill=255)  # (x0, y0, x1, y1)
            blurred = image.filter(ImageFilter.GaussianBlur(25 * float(degree)))
            image.paste(blurred, mask=mask)
        else:
            cropped_image = image.crop((b['x_min'], b['y_min'], b['x_max'], b['y_max']))
            blurred_image = cropped_image.filter(ImageFilter.GaussianBlur(25 * float(degree)))
            image.paste(blurred_image, (b['x_min'], b['y_min'], b['x_max'], b['y_max']))
    return image


def pixelating(image, boxes, degree):
    for b in boxes:
        cropped_image = image.crop((b['x_min'], b['y_min'], b['x_max'], b['y_max']))
        w, h = cropped_image.size
        small = cropped_image.resize((int(w / (float(degree) * w)), int(h / (float(degree) * h))), Image.BILINEAR)
        result = small.resize(cropped_image.size, Image.NEAREST)
        image.paste(result, (b['x_min'], b['y_min'], b['x_max'], b['y_max']))
    return image


def blackening(image, boxes, degree):
    for b in boxes:
        cropped = image.crop((b['x_min'], b['y_min'], b['x_max'], b['y_max']))
        h, w = cropped.size
        black = Image.new(image.mode, (h, w), 'black')
        result = Image.blend(cropped, black, float(degree))
        cropped.paste(result)
        image.paste(cropped, (b['x_min'], b['y_min'], b['x_max'], b['y_max']))
    return image
