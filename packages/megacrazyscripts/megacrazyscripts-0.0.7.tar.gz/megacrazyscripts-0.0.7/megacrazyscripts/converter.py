def converter(audio):

    prefix = '(Converter)'

    import ffmpeg

    audio_no_format = audio.split('.')
    audio_no_format = audio_no_format[0] + '.wav'

    # Convert audio to wav
    print(prefix, f'Converting {audio} to wav...')
    (
        ffmpeg
        .input(audio)
        .output(audio_no_format)
        .run()
    )
    
    return print(prefix, 'Done')