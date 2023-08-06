def video_img(cover, song, artist, toptext, output):

    prefix = '(Video)'

    from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter 
    from math import trunc

    x, y = (2500, 2500) # Cover size
    X, Y = (7680, 4320) # Background size

    # Import cover
    print(prefix, f'Importing {cover} ...')
    bg = Image.open(cover)
    cv = Image.open(cover)

    # Resizing
    print(prefix, 'Resizing cover and background...')
    cv = cv.resize((x, y))
    bg = bg.resize((X, Y))

    # Add a shadow (Black square with blur)
    print(prefix, 'Creating the shadow...')
    square = Image.new(mode = "RGBA", size = (2500, 2500), color = (0, 0, 0))
    bg.paste(square, (trunc((X-x)/2), 659))

    # Blur and turn brightness down
    print(prefix, 'Adding blur to background...')
    bg = ImageEnhance.Brightness(bg).enhance(0.4)
    bg = bg.filter(ImageFilter.GaussianBlur(120))

    # Paste cover into the background
    print(prefix, 'Merging cover with background')
    bg.paste(cv, ( trunc((X-x)/2 ), 659))


    ### Text
    text = ImageDraw.Draw(bg)

    # Layout is [text, y-coordinates (from top), font, font-size]
    toptext = [toptext, 300, 'Roboto-Black', 250]
    song = [song, 3240, 'Roboto-Bold', 279]
    artist = [artist, 3640, 'Roboto-Light', 186]

    # Generate the text
    for i in [toptext, song, artist]:
        print(prefix, f'Writing "{i[0]}" with "{i[2]}" font')
        font = ImageFont.truetype(i[2], i[3])
        x, y = text.textsize(i[0], font=font)
        text.text(((X-x)/2, i[1]), i[0], fill=(255, 255, 255), font=font, align='center')

    # Export final thing to a file
    print(prefix, f'Exporting file as {output} ...')
    bg.save(output)

    return print(prefix, 'Done')