def aitv(audio, png, output):
    
    import ffmpeg

    audio = ffmpeg.input(audio)
    png = ffmpeg.input(png)
    (
        ffmpeg
        .output(audio, png, output, format='mp4')
        .run()
    )