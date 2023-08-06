def slowedreverb(audio, howslow, output):

    prefix = '(Slowed + Reverb)'

    from pedalboard import Pedalboard, load_plugin
    from importlib import resources
    from math import trunc
    from os import remove
    import soundfile
    import io

    # Import audio file
    print(prefix, f'Importing {audio} ...')
    audio, sample_rate = soundfile.read(audio)

    # Slow audio
    print(prefix, 'Slowing audio...')
    sample_rate -= trunc(sample_rate*(howslow/100))

    # Add reverb
    with resources.open_binary('megacrazyscripts', 'vst/TAL-Reverb-4.vst3') as vst_path:
        print(prefix, f'Adding reverb using {vst_path} ...')
        vst = load_plugin(vst_path)
        vst.size = 40
        vst.diffuse = 100
        vst.delay = '0.0000 s'
        vst.modulation_rate = 0
        vst.modulation_depth = 0
        vst.low_cut = 75
        vst.high_cut = 4000
        vst.dry = 80
        vst.wet = 20

    # Add effects
    effected = vst(audio, sample_rate)

    # Export audio
    print(prefix, f'Exporting audio as {output} ...')
    soundfile.write(output, effected, sample_rate)

    return print(prefix, 'Done')