import json

def load_groupsongs(playlist_id):
    with open(playlist_id + '.txt', 'r') as json_file:
        data = json.load(json_file)

    return data

def load_playlists(FILENAME, PLAYLIST):
    with open(FILENAME, 'r') as json_file:
        data = json.load(json_file)
        for k in data:
            if k != 'null':
                PLAYLIST[int(k)] = data[k]
            else:
                PLAYLIST[k] = data[k]

    return data

def save_playlists(FILENAME, PLAYLIST):
    with open(FILENAME, 'w') as outfile:
        outfile.truncate(0)
        json.dump(PLAYLIST, outfile)
        outfile.close()