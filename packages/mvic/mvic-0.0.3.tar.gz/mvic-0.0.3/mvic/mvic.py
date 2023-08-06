def thumbnail(cover, output):

    from PIL import Image, ImageEnhance, ImageFilter
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
    
def video(cover, song, artist, output):

    from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
    from math import trunc

    x, y = (2500, 2500) # Cover size
    X, Y = (7680, 4320) # Background size

    # Import cover
    bg = Image.open(cover)
    cv = Image.open(cover)

    # Resizing
    print('Resizing cover and background...')
    cv = cv.resize((x, y))
    bg = bg.resize((X, Y))
    # Add a shadow (Black square with blur)
    print('Creating the shadow...')
    square = Image.new(mode = "RGBA", size = (2500, 2500), color = (0, 0, 0))
    bg.paste(square, (trunc((X-x)/2), 659))
    # Blur and turn brightness down
    print('Adding blur to background...')
    bg = ImageEnhance.Brightness(bg).enhance(0.4)
    bg = bg.filter(ImageFilter.GaussianBlur(120))
    # Paste cover into the background
    print('Merging cover with background')
    bg.paste(cv, ( trunc((X-x)/2 ), 659))


    ### Text
    toptxt = '(Slowed + Reverb)'
    text = ImageDraw.Draw(bg)

    # [text, y-coordinates, font, font-size]
    toptxt = [toptxt, 300, 'Roboto-Black', 250]
    song = [song, 3240, 'Roboto-Bold', 279]
    artist = [artist, 3640, 'Roboto-Light', 186]

    # Generate the text
    for i in [toptxt, song, artist]:
        print('Writing:', i[0])
        font = ImageFont.truetype(i[2], i[3])
        x, y = text.textsize(i[0], font=font)
        text.text(((X-x)/2, i[1]), i[0], fill=(255, 255, 255), font=font, align='center')

    # Export final thing to a file
    print('Exporting...')
    bg.save(output)

    return print('Video image: Done')