import telegram
from decouple import config
import logging

from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

import spotifyfunc as spotify
import loadsave

BOT_TOKEN = config('BOT_TOKEN')
bot = telegram.Bot(token=BOT_TOKEN)

# DEFAULT_PLAYLIST = config('DEFAULT_PLAYLIST')

CLIENT_ID = config('CLIENT_ID')
CLIENT_SECRET = config('CLIENT_SECRET')

USERNAME = config('USERNAME')

sp = spotify.create_auth(USERNAME, CLIENT_ID, CLIENT_SECRET)
# PLAYLISTS[group_id] = playlist_spotify_url
PLAYLISTS = {}
PLAYLISTFILENAME = 'playlist_data.txt'

GROUPSONGSPATH = 'GROUPSONGS/'

# -----------------------------------------------------------------------------
# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)
# -----------------------------------------------------------------------------

def start(update, context):
    if update == None or update.message == None:
        return
    update.message.reply_text('That\'s just like, your opinion, man')


def add_song(update, context):

    if len(context.args) == 0:
        update.message.reply_text('Please pass song')
        return

    if update.effective_chat.id == None:
        update.effective_chat.id = 'null'

    try:
        playlist = PLAYLISTS[update.effective_chat.id]
        playlist_id = playlist[1]
    except:
        update.message.reply_text('ERROR ADDING SONG PLEASE NOTIFY ME')
        return


    song = context.args[0].split('/')[4]
    song = [song.split('?')[0]]

    groupsongs = loadsave.load_groupsongs(GROUPSONGSPATH + str(playlist_id))

    if song[0] in groupsongs:
        update.message.reply_text('Song already exists in playlist')
        return

    groupsongs.append(song[0])

    spotify.add_song_to_playlist(sp,
                                 USERNAME,
                                 playlist_id,
                                 song)

    loadsave.save_playlists(GROUPSONGSPATH + str(playlist_id) + '.txt', groupsongs)
    update.message.reply_text('Added song to playlist: ' + playlist[0])



def add_song_inline(update, context):
    args = (update.message.text).split(' ')

    if len(args) < 2:
        return

    if len(args) > 2:
        return

    if args[0] != '@spotidude':
        return

    try:
        playlist = PLAYLISTS[update.effective_chat.id]
        playlist_id = playlist[1]
    except:
        update.message.reply_text('ERROR ADDING SONG PLEASE NOTIFY ME')
        return

    song = args[1]
    song = song.split('/')[4]
    song = [song.split('?')[0]]

    groupsongs = loadsave.load_groupsongs(GROUPSONGSPATH + str(playlist_id))

    if song[0] in groupsongs:
        update.message.reply_text('Song already exists in playlist')
        return

    groupsongs.append(song[0])

    spotify.add_song_to_playlist(sp,
                                 USERNAME,
                                 playlist_id,
                                 song)

    loadsave.save_playlists(GROUPSONGSPATH + str(playlist_id) + '.txt', groupsongs)
    update.message.reply_text('Added song to playlist: ' + playlist[0])


def create_playlist(update, context):
    if len(context.args) == 0:
        update.message.reply_text('Please pass playlist name')
        return

    if update.effective_chat.id == None:
        update.effective_chat.id = 'null'

    playlist_name = context.args[0]

    if(update.effective_chat.id in PLAYLISTS.keys()):
        update.message.reply_text('This group already has a playlist')
        return

    ret = spotify.create_playlist(sp,
                                  playlist_name)


    id = ret['id']
    PLAYLISTS[update.effective_chat.id] = (playlist_name, id)

    loadsave.save_playlists(PLAYLISTFILENAME, PLAYLISTS)
    loadsave.save_playlists(GROUPSONGSPATH + str(id) + '.txt', [])

    update.message.reply_text('Created new playlist with the name:\t' +  playlist_name)


def get_playlists():
    playlists = sp.user_playlists(username)

    for playlist in playlists['items']:
        print(playlist['name'])


def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))

    dispatcher.add_handler(CommandHandler("add_song", add_song, pass_args=True, pass_chat_data=True))

    dispatcher.add_handler(CommandHandler("create_playlist", create_playlist, pass_args=True, pass_chat_data=True, pass_user_data=True))

    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, add_song_inline))

    updater.start_polling()
    updater.idle()

def init():
    loadsave.load_playlists(PLAYLISTFILENAME, PLAYLISTS)

if __name__ == '__main__':
    init()
    main()