def ytdw(url, output):

    prefix = '(ytdw)'
    
    from youtube_dl import YoutubeDL
    from jcow_utils import converter
    from os import remove
    import ffmpeg
    
    output_temp = output + '.mp3'

    # Download audio
    print(prefix, 'Downloading audio...')
    audio = YoutubeDL({'format':'bestaudio', 'outtmpl':output_temp})
    audio.extract_info(url)

    # Convert temporary file to wav
    print(prefix, 'Converting audio to wav...')
    converter(output_temp)

    # Remove first file
    print(prefix, 'Removing first file...')
    remove(output_temp)
    
    return print(prefix, 'Done')