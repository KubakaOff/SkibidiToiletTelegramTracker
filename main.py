import logging
from configparser import ConfigParser
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
import pytube
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import secrets
import os
#import re

config = ConfigParser()
config.read("config.ini")
token = config.get("telegram", "token")
playlist_file = config.get("YouTube", "playlist_file")
cache_folder = config.get("YouTube", "cache_folder")
fb_private_key_path = config.get("firebase", "path_to_private_key")

if not os.path.exists(cache_folder):
    os.mkdir(cache_folder)

#playlist_base = "https://www.youtube.com/playlist?list="

#playlist_url = playlist_base + playlist_id

#print(playlist_url)

#playlist = pytube.Playlist(playlist_url)
#playlist._video_regex = re.compile(r"\"url\":\"(/watch\?v=[\w-]*)")

vids = open(playlist_file, "r").readlines()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

firebase_admin.initialize_app(credentials.Certificate(fb_private_key_path), {'databaseURL' : 'https://skibiditoiletrackertelegrambot-default-rtdb.firebaseio.com'})

def add_to_tracker(user_id, episode_id):
    ref = db.reference('users')
    user_ref = ref.child(str(user_id))
    if user_ref.get() is None:
        user_ref.set({
            'watched_episodes': [episode_id]
        })
    else:
        watched_episodes = user_ref.child('watched_episodes').get()
        watched_episodes.append(episode_id)
        user_ref.update({
            'watched_episodes': watched_episodes
        })

def get_watched_episodes(user_id):
    ref = db.reference('users')
    user_ref = ref.child(str(user_id))
    watched_episodes = user_ref.child('watched_episodes').get()
    return watched_episodes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Skibidi dop dop dop yes yes skibidi dabodi dobodi dib dib.\n\nUse /skibiditoilet to watch a random Skibidi Toilet episode.\n/tracker to see how many Skibidi Toilet episodes you've watched.")

async def random_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    watched_episodes = get_watched_episodes(user_id)
    if watched_episodes:
        if len(vids) == len(watched_episodes):
            await context.bot.send_message(chat_id=chat_id, text="You've watched all Skibidi Toilet episodes (for now)!\nYou are a true Skibidi Sigma!")
            return
    vid_id = secrets.choice(vids)
    if watched_episodes:
        while vid_id in watched_episodes:
            vid_id = secrets.choice(vids)
    yt = pytube.YouTube("https://www.youtube.com/watch?v=" + vid_id)
    vid_id = yt.video_id
    if os.path.exists(os.path.join(".", cache_folder, vid_id + ".mp4")):
        file = open(os.path.join(".", cache_folder, vid_id + ".mp4"), 'rb')
    else:
        stream = yt.streams.filter(res='720p').first()
        stream.download(filename=os.path.join(".", cache_folder, vid_id + ".mp4"))
        file = open(os.path.join(".", cache_folder, vid_id + ".mp4"), 'rb')
    add_to_tracker(user_id, vid_id)
    await context.bot.send_animation(chat_id=chat_id, animation=file)

async def check_tracker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    total = len(vids)
    watched_list = get_watched_episodes(update.effective_user.id)
    if not watched_list:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Please first use /skibiditoilet to watch a episode.")
    else:  
        watched = len(watched_list)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"You've watched {watched} out of {total} Skibidi Toilet episodes.")

if __name__ == '__main__':
    application = ApplicationBuilder().token(token).build()
    
    start_handler = CommandHandler('start', start)
    random_handler = CommandHandler('skibiditoilet', random_video)
    tracker_handler = CommandHandler('tracker', check_tracker)
    application.add_handler(start_handler)
    application.add_handler(random_handler)
    application.add_handler(tracker_handler)
    
    application.run_polling()
