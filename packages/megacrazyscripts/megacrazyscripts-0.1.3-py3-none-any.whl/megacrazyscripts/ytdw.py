def ytdw(url, output):

    prefix = '(ytdw)'
    
    from megacrazyscripts import converter
    from youtube_dl import YoutubeDL
    from os import remove
    import ffmpeg
    
    output_temp = output + '.mp3'

    # Download audio
    print(prefix, 'Downloading audio...')
    audio = YoutubeDL({'format':'bestaudio', 'outtmpl':output_temp})
    audio.extract_info(url)

    # Convert temporary file to wav
    print(prefix, f'Converting {output_temp} to wav...')
    converter(output_temp)

    # Remove first file
    print(prefix, 'Removing first file...')
    remove(output_temp)
    
    return print(prefix, 'Done')