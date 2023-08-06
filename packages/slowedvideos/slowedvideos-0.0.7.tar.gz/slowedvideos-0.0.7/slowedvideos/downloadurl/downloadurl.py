def downloadurl(url, output):

    prefix = 'Download URL -'

    from youtube_dl import YoutubeDL

    output = output.split('.')

    # Set opts
    print(prefix, 'Setting opts...')
    ytdl_opts = { 'format': 'bestaudio/best', 'outtmpl':output[0], 'postprocessors':[{'key': 'FFmpegExtractAudio','preferredcodec': 'wav'}] }
    print(prefix, ytdl_opts)
    # Download video
    print(prefix, 'Downloading audio...')
    YoutubeDL(ytdl_opts).download([url])

    return print(prefix, 'Done')