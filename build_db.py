import os
import sound
import hashlib
from db import Database
from mp import MatchingPursuit
from mdct import Mdct
import numpy as np

current_dir = os.path.dirname(os.path.abspath(__file__))
music_dir = current_dir + "/music"
music_list = []

# Selecting all mp3 in music directory
for file in os.listdir(music_dir):
    music_list.append(file)

print("%d tracks in database" % len(music_list))

# Creating an empty database
if os.path.isfile(current_dir + "/database.db"):
        os.remove(current_dir + "/database.db")
database = Database()
database.create()

# Processing each track

atoms_per_frame = 60
frame_duration = 3

mdct = Mdct([2048,8192,16384])
mp = MatchingPursuit(mdct, atoms_per_frame)
biggest_atom_size = mdct.sizes[-1]

for track in music_list:
    track_title = track[:-4]
    track_id = database.addTrack(track_title)
    print("=> Processing %s, id: %d" % (track_title, track_id))

    wavdata = sound.read(music_dir + "/" + track)
    Fe = wavdata.getframerate()
    frame_size = int(frame_duration*Fe/biggest_atom_size)*biggest_atom_size
    frame_number = int(wavdata.getnframes()/frame_size)

    print("%d frames to process for this track" % frame_number)
    
    progress = 0

    for i in range(frame_number):
        s = wavdata.readframes(frame_size)
        s = np.frombuffer(s, dtype='<i2') 
        y = mp.sparse(s)
        keys = mp.extractKeys(y)
        query = [(hash_key,track_id, int(i*frame_size+offset)) for (hash_key,offset) in keys]

        database.addFingerprint(query)

        if i*100/frame_number >= progress + 10:
            progress = i * 100/frame_number
            print("%d%%," % (progress,)),

    print("100%")











