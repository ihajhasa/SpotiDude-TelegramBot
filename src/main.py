import telegram
from decouple import config
import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler,  MessageHandler, Filters

import spotifyfunc as spotify
import loadsave

BOT_TOKEN = config('BOT_TOKEN')
bot = telegram.Bot(token=BOT_TOKEN)


STATIC_MESSAGES = {
    'no_playlist': 'This chat does not have a playlist. Run /create_playlist <PLAYLIST_NAME> to create a playlist for this chat.',
    'deleted_playlist': 'This chat\'s playlist has been deleted.',
}

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


    group_id = update.effective_chat.id

    if group_id not in PLAYLISTS.keys():
        update.message.reply_text(STATIC_MESSAGES['no_playlist'])
        return

    try:
        playlist = PLAYLISTS[group_id]
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

    if args[0] != '@spotidudebot':
        return


    group_id = update.effective_chat.id

    if group_id not in PLAYLISTS.keys():
        update.message.reply_text(STATIC_MESSAGES['no_playlist'])
        return

    try:
        playlist = PLAYLISTS[group_id]
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

    playlist_name = ' '.join(context.args)

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

def get_playlist(update, context):
    group_id = update.effective_chat.id

    if group_id in PLAYLISTS.keys():
        update.message.reply_text('https://open.spotify.com/playlist/' + PLAYLISTS[group_id][1])
    else:
        update.message.reply_text(STATIC_MESSAGES['no_playlist'])

def delete_playlist(update, context):
    # spotify has no endpoint to delete playlists, so basically what this will do is clear the playlist data
    # stored for the group.

    # Todo: add an inline confirmation to make sure this isnt pressed accidentally.
    #   For now I wont list this command so it has to be fully typed by the user.

    query = update.callback_query
    query.answer()

    group_id = update.effective_chat.id

    if group_id not in PLAYLISTS.keys():
        update.message.reply_text(STATIC_MESSAGES['no_playlist'])
        return

    playlist_id = PLAYLISTS[group_id][1]
    sp.current_user_unfollow_playlist(playlist_id)
    del PLAYLISTS[group_id]

    with open('deleted_playlist_data.txt', 'a') as f:
        f.write(str(group_id) + '\t' + str(playlist_id) + '\n')

    loadsave.save_playlists(PLAYLISTFILENAME, PLAYLISTS)

    query.edit_message_text(
        text="Deleted Playlist!!!!!"
    )

def cancel_action(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(
        text="Canceled Action"
    )

def delete(update, context):
    keyboard = [
        [
            InlineKeyboardButton('YES', callback_data='delete_playlist.True'),
            InlineKeyboardButton('NO', callback_data='delete_playlist.False')
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(text="Confirm DELETING the group playlist", reply_markup=reply_markup)
    return

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("get_playlist", get_playlist))

    dispatcher.add_handler(CommandHandler("delete", delete))

    dispatcher.add_handler(CallbackQueryHandler(delete_playlist, pattern='delete_playlist.True'))
    dispatcher.add_handler(CallbackQueryHandler(cancel_action, pattern='[\w]+.False'))

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