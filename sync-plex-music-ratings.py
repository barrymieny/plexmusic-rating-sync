# USE AT YOUR OWN RISK!!!!
#
# Requires eyed3 and plexapi libraries, written & tested in python 3.9

from plexapi.myplex import MyPlexAccount
import mutagen
import mutagen.id3
import os
import io
from mutagen import id3
from mutagen.id3 import ID3,  COMR, Frames, Frames_2_2, ID3Warning, ID3JunkFrameError, ID3NoHeaderError

LIB = os.getenv('PLEXLIB')
PLEXREPLACEFROM = os.getenv('PLEXREPLACEFROM')
PLEXREPLACETO = os.getenv('PLEXREPLACETO')
UPDATEPLEX = os.getenv('UPDATEPLEX') == "true"
UPDATEFILE = os.getenv('UPDATEFILE') == "true"
DEBUGRESOURCES = os.getenv('DEBUGRESOURCES') == "true"
DEBUGSONG = os.getenv('DEBUGSONG') == "true"
DEBUGALBUM = os.getenv('DEBUGALBUM') == "true"
LOGNOID3ERROR = os.getenv('LOGNOID3ERROR') == "true"
LOGALLRATINGS = os.getenv('LOGALLRATINGS') == "true"
SHOWPROGRESS = os.getenv('SHOWPROGRESS') == "true"
RATINGPOPMEMAIL = os.getenv('RATINGPOPMEMAIL')
RATINGID3TAG="POPM:" + RATINGPOPMEMAIL
# Counters
insync = 0
justsynced = 0
notag = 0
error = 0

def makeRemoteString(str):
    if (PLEXREPLACEFROM is None or PLEXREPLACEFROM==""):
        return str
    else:
        return str.replace(PLEXREPLACEFROM, PLEXREPLACETO)

def getRatingValueFromFile(file):
    return file.tag.popularities.get(b'MusicBee')

def convertRatingsFromId3ToPlex(n):
    return float(float(n/255) * float(10))

def convertRatingsFromPlexToId3(n):
    return int(float(n/10) * float(255))

def convertRatingsToMusicBee(n):
    return int(n * 255 / 10)

def print_to_string(*args, **kwargs):
    output = io.StringIO()
    print(*args, file=output, **kwargs)
    contents = output.getvalue()
    output.close()
    return contents

def getAllPOPM(localfile):
    file = ID3(localfile)
    if LOGALLRATINGS:
        popms = [i for i in file if i.startswith('POPM')]
        for rating in popms:
            popm = file[rating]
            print("found rating for " + rating + "=", popm)
    if RATINGID3TAG in file:
        return file[RATINGID3TAG]
    return None

def updateID3Rating(localfile, rating):
    file = ID3(localfile)
    if RATINGID3TAG in file:
        tag = file[RATINGID3TAG]
        tag.rating=rating
    else:
        frame= mutagen.id3.POPM(email=RATINGPOPMEMAIL, rating= rating)
        file.add(frame)
    
    file.save()



#plex ratings 0 - 10
#musicBee ratings 0 - 255
#ID3 ratings 0-255

print("start. connecting to plex user=" + os.getenv('PLEXUSER'))
if (UPDATEFILE):
    print("Will update files if existing rating in plex")
else:
    print("Will **NOT** update files if existing rating in plex")

if (UPDATEPLEX):
    print("Will update plex if existing rating in files")
else:
    print("Will **NOT** update plex if existing rating in files")


account = MyPlexAccount(os.getenv('PLEXUSER'), os.getenv('PLEXPW'))
if (DEBUGRESOURCES):
    resources = account.resources()
    print("Found the following resources:")
    for res in resources:
        print(res)

plex = account.resource(LIB).connect()
print('connected')
curalbum = 0
albums = plex.library.section('Music').albums()
albumcount = len(albums)
for album in albums:
    if DEBUGALBUM:
        print('Album: ' + str(album))
    tracks = album.tracks()
    curalbum += 1
    if (SHOWPROGRESS and ((curalbum % 100) == 0)):
        print("Album " + str(curalbum) + "/" + str(albumcount))

    for track in tracks:
        trackmsg = ""
        localfile = makeRemoteString(track.locations[0])

        # Iterates across all tracks
        try:
            if isinstance(track.userRating, float): 
                # Checks to see if the Plex userRating exists, var type will be float if track is rated, it will be nonetype if not.
                
                trackmsg = print_to_string('\t' + track.title + ' is already rated in Plex')
                rating = getAllPOPM(localfile)
                newrating = convertRatingsFromPlexToId3(float(track.userRating))
                if ((rating == None) or (rating.rating != newrating)):
                    if (UPDATEFILE):
                        # Ratings on both? We prefer plex to dictate for now, so we always write it on the file if present
                        print('\t**Updating file ' + track.locations[0] + ' from rating:',rating,' to rating:', newrating )
                        updateID3Rating(localfile, newrating)
                        justsynced += 1
                    else:
                        print('\t**Run in update mode to Update file ' + track.locations[0] +' from rating:',rating,' to rating:', newrating )
            else:
                # This case is where Plex has no rating so it tries to fetch a value from the id3 tag
                trackmsg = print_to_string('\t "' + track.title + '" (' + track.locations[0]  + ') has no rating in Plex, checking file id3 tag. ', end = '')
                file = ID3(localfile)
                rating = getAllPOPM(localfile)
                
                if (rating is not None):
                    newrating =convertRatingsFromId3ToPlex(rating.rating)
                    if (UPDATEPLEX):
                        # this case is where Plex has no rating but the iD3 tag does so the next steps import the rating into Plex.
                        print('\t"' + track.title + '" (' + track.locations[0]  + ') ID3 tag rating ' + str(rating.rating) + ' found and saved to Plex userRating field as ' + str(newrating))
                        track.rate(newrating)
                        justsynced += 1 

                    else:
                        print('\t**Run in update mode to Update plex song ' + str(album) + ":" + track.title + ' to rating:'  + str(newrating))  
                else:
                    trackmsg = trackmsg + print_to_string('No tag present in file or Plex.')
                    notag += 1
        except ID3NoHeaderError as noid3:
            if (LOGNOID3ERROR):
                print('\tNo ID3 Tag found on ' + track.locations[0]) #, err )
            error += 1

        except Exception as err:
            print('\n\t** Exception processing file ' + track.locations[0]  +':', err )
            error += 1
        if (DEBUGSONG):
            print(trackmsg)

        

# Stats Output                          
print(str(insync) + ' files alread in sync')
print(str(justsynced) + ' newly synced files')
print(str(notag) + ' files with no tags')
print(str(error) + ' files had errors')
