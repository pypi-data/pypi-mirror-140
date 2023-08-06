def mix_audio_image(audio, png, output):
    
    prefix = '(mix_audio_image)'

    import ffmpeg

    # Import files
    print(prefix, f'Importing {audio}, {png} ...')
    audio = ffmpeg.input(audio)
    png = ffmpeg.input(png)
    
    # Mix into video
    print(prefix, 'Mixing audio and image into a video...')
    (
        ffmpeg
        .output(audio, png, output, format='mp4')
        .run()
    )

    return print(prefix, 'Done')