def thumbnail(cover, output):

    from PIL import Image, ImageDraw, ImageEnhance, ImageFilter 
    from math import trunc

    # Import
    tb = Image.open(cover)
    cv = Image.open(cover)

    # Cover
    x, y = (626, 626)
    cv = cv.resize((x, y), resample=0, box=None)
    
    # Thumb Resize
    X, Y = (1920, 1080)
    tb = tb.resize((X, Y), resample=0, box=None)
    
    # Blur and brightness
    tb = ImageEnhance.Brightness(tb).enhance(0.3)
    tb = tb.filter(ImageFilter.GaussianBlur(60))
    tb = tb.copy()

    # Mix into file
    center = (trunc((X-x)/2), trunc((Y-y)/2))
    tb.paste(cv, center)
    tb.save(output)
    
    return print('Thumbnail image: Done')
    