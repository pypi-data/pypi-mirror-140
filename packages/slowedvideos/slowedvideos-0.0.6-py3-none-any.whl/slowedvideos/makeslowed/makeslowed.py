def makeslowed(audio, howslow, output):

    prefix = 'Make Slowed Reverb -'

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
    vst_path = resources.open_binary('slowedvideos.makeslowed', 'TAL-Reverb-4.vst3')
    print(prefix, f'Adding reverb using {vst_path} ...')
    vst = load_plugin(vst_path)

    (
        vst
        .size(60)
        .diffuse(100)
        .delay('0.0000 s')
        .modulation_rate(0)
        .modulation_depth(0)
        .low_cut(75)
        .high_cut(4000)
        .dry(80)
        .wet(35)
    )

    # Add effects
    effected = vst(audio, sample_rate)

    # Export audio
    print(prefix, f'Exporting audio as {output} ...')
    soundfile.write(output, effected, sample_rate)

    return print(prefix, 'Done')