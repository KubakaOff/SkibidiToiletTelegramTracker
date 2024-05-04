from pytube import YouTube, Playlist

p = Playlist("https://www.youtube.com/playlist?list=PL-ZXraMeHBPJHXBhrNowJaQslyqtUg-tZ")

f = open("playlist.txt", "w")

for v in p:
    y = YouTube(v)
    try:
        stream = y.streams.filter(res='720p').first()
        f.write(y.video_id + "\n")
        print("Added non restricted")
    except:
        print("Either something went wrong or restricted")
