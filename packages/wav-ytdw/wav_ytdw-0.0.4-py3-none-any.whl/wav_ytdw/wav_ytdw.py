def wav_ytdw(url, output):
    
    from youtube_dl import YoutubeDL
    from os import remove
    import ffmpeg
    
    # Download audio to a temporary file
    audio = YoutubeDL({'format':'bestaudio', 'outtmpl':'temp'})
    audio.extract_info(url)

    # Convert temporary file to wav
    (
        ffmpeg
        .input('temp')
        .output(output)
        .run()
    )
    
    # Remove the temporary file
    remove('temp')
wav_ytdw('https://soundcloud.com/therealdrymtman/chapter-8-gecgecgec', 'teste.wav')