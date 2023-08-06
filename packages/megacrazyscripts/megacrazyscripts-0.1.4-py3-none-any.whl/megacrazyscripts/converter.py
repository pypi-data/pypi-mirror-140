def converter(audio):

    prefix = '(Converter)'

    from pydub import AudioSegment

    audio_no_format = audio.split('.')

    # Convert audio to wav
    print(prefix, f'Converting {audio} to wav...')
    sound = AudioSegment.from_mp3(audio)
    sound.export(audio_no_format[0], format="wav")
    
    return print(prefix, 'Done')