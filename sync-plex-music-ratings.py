# USE AT YOUR OWN RISK!!!!
#
# Requires eyed3 and plexapi libraries, written & tested in python 3.9

from plexapi.myplex import MyPlexAccount
import mutagen
import mutagen.id3
import os
import io
import traceback
from mutagen import id3
from mutagen._iff import InvalidChunk
from mutagen.mp3 import HeaderNotFoundError
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
LOGINVALIDCHUNKERROR = os.getenv('LOGINVALIDCHUNKERROR') == "true"
LOGNOHEADERNOTFOUNDERROR = os.getenv('LOGNOHEADERNOTFOUNDERROR') == "true"
LOGALLRATINGS = os.getenv('LOGALLRATINGS') == "true"
SHOWPROGRESS = os.getenv('SHOWPROGRESS') == "true"
RATINGPOPMEMAIL = os.getenv('RATINGPOPMEMAIL')
RATINGID3TAG="POPM:" + RATINGPOPMEMAIL
FLACRATINGTAG= os.getenv('FLACRATINGTAG')
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

# ID3 has ['RATING'] 0-255, plex has rating 0.0-10.0
def convertRatingsFromId3ToPlex(n):
    return round(float(float(n/255) * float(10)),1)

# ID3 has ['RATING'] 0-255, plex has rating 0.0-10.0
def convertRatingsFromPlexToId3(n):
    return int(float(n/10) * float(255))

# flac sometimes has ['RATING'] 0-100 (mediamonkey) also sometimes has 0-5 (others)
# store as 0-100 but handle case of 0-5 on read
def convertRatingsFromFlacToPlex(n):
    if (n <= 5):
        return float(n) * 2
    else:
        return float(float(n)/float(10))

# flac has ['RATING'] 0-100 (mediamonkey) also sometimes has 0-5 (others)
def convertRatingsFromPlexToFlac(n):
    return int(round(n*10,0))

def convertRatingsToMusicBee(n):
    return int(n * 255 / 10)

def print_to_string(*args, **kwargs):
    output = io.StringIO()
    print(*args, file=output, **kwargs)
    contents = output.getvalue()
    output.close()
    return contents

def getFile(localfile):
    try:
        file = mutagen.File(localfile)
        # if ((file == None) and localfile.lower().endswith('.dts')):
        #     file = mutagen.wave.WAVE(localfile)
        return file
    except InvalidChunk as ic:
        #error!
        raise
    except HeaderNotFoundError as hnf:
        #error!
        raise
    except Exception as ex:
        #error!
        raise

def convertPlexRatingToFileRating(file, plexrating):
    try:
        filerating = getFileRating(file)
        if (type(file) is mutagen.flac.FLAC):
            return convertRatingsFromPlexToFlac(plexrating)
        else:
            return convertRatingsFromPlexToId3(plexrating)
    except Exception as ex:
        #error!
        raise
    


def getFileRatingAsPlexRating(file):
    try:
        filerating = getFileRating(file)
        if filerating is None:
            return None
        if (type(file) is mutagen.flac.FLAC):
            return convertRatingsFromFlacToPlex(filerating)
        else:
            if LOGALLRATINGS:
                popms = [i for i in file if i.startswith('POPM')]
                for rating in popms:
                    popm = file[rating]
                    print("found rating for " + rating + "=", popm)
            return convertRatingsFromId3ToPlex(filerating)
    except InvalidChunk as ic:
        #error!
        raise
    except HeaderNotFoundError as hnf:
        #error!
        raise
    except Exception as ex:
        #error!
        raise

def getFileRating(file):
    try:
        if (type(file) is mutagen.flac.FLAC):
            if ((FLACRATINGTAG in file.tags) and (file.tags[FLACRATINGTAG] is not None)):
                ratings=file.tags[FLACRATINGTAG]
                ratingnum = int(ratings[0]) if ratings[0].isdigit() else None
                return ratingnum # tags are always arrays for some weird reason
        else:
            if RATINGID3TAG in file:
                if (file[RATINGID3TAG] is not None):
                    return file[RATINGID3TAG].rating
        return None
    except Exception as ex:
        #error!
        raise

def updateFileRating(file, filerating):
    try:
        if (type(file) is mutagen.flac.FLAC):
            updateFlacRating(file, filerating)
        else:
            updateID3Rating(file, filerating)
    except Exception as ex:
        #error!
        raise

def updateFlacRating(file, filerating):
    try:    
        print(' to rating:', filerating )
        file.tags[FLACRATINGTAG] = filerating
        file.save()
    except Exception as ex:
        #error!
        raise

def updateID3Rating(file, filerating):
    try:
        #file = ID3(localfile)

        if RATINGID3TAG in file:
            tag = file[RATINGID3TAG]
            tag.rating=filerating
        else:
            frame= mutagen.id3.POPM(email=RATINGPOPMEMAIL, rating= filerating)
            file.add(frame)
        
        file.save()
    except Exception as ex:
        #error!
        raise



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
        # Iterates across all tracks
        if (track.locations[0]== "/volume1/music/!!FLAC/Bad Company - Bad Company (2006 Gold CD) (Flac)/02 - Rock Steady.FLAC"):
            print("Check this one out")
        if ((str(album) == '<Album:185809:Broken-Boy-Soldiers>') and (track.title == "Together") ):
            print("Check this one out")
        try:
            trackmsg = ""
            localfile = makeRemoteString(track.locations[0])
            file = getFile(localfile)
            fileplexrating = getFileRatingAsPlexRating(file)
            filerating = getFileRating(file)

            if isinstance(track.userRating, float): 
                # Checks to see if the Plex userRating exists, var type will be float if track is rated, it will be nonetype if not.
                
                trackmsg = print_to_string('\t' + track.title + ' is already rated in Plex')
                newrating =convertPlexRatingToFileRating (file, track.userRating)
                #newrating = convertRatingsFromPlexToId3(float(track.userRating))
                if ((filerating == None) or (fileplexrating != track.userRating)):
                    if (UPDATEFILE):
                        print('\t**Updating file ' + track.locations[0] + ' from rating:',filerating,' to rating:', newrating )
                        # Ratings on both? We prefer plex to dictate for now, so we always write it on the file if present
                        updateFileRating(file, newrating)
                        justsynced += 1
                    else:
                        print('\t**Run in update mode to Update file ' + track.locations[0] +' from rating:',filerating,' to rating:', newrating )
            else:
                # This case is where Plex has no rating so it tries to fetch a value from the id3 tag
                trackmsg = print_to_string('\t "' + track.title + '" (' + track.locations[0]  + ') has no rating in Plex, checking file id3 tag. ', end = '')
                
                if (fileplexrating is not None):
                    if (UPDATEPLEX):
                        # this case is where Plex has no rating but the iD3 tag does so the next steps import the rating into Plex.
                        print('\t"' + track.title + '" (' + track.locations[0]  + ') ID3 tag rating ' + str(filerating) + ' found and saved to Plex userRating field as ' + str(fileplexrating))
                        track.rate(fileplexrating)
                        justsynced += 1 

                    else:
                        print('\t**Run in update mode to Update plex song ' + str(album) + ":" + track.title + ' to rating:', fileplexrating)
                else:
                    trackmsg = trackmsg + print_to_string('No tag present in file or Plex.')
                    notag += 1
        except ID3NoHeaderError as noid3:
            if (LOGNOID3ERROR):
                print('\tNo ID3 Tag found on ' + track.locations[0]) #, err )
                print(traceback.format_exc())
            error += 1
        except InvalidChunk as ic:
            if (LOGINVALIDCHUNKERROR):
                print('\tInvalid Chunk on  ' + track.locations[0]) #, err )
                print(traceback.format_exc())
            #error!
            error += 1
        except HeaderNotFoundError as hnf:
            if (LOGNOHEADERNOTFOUNDERROR):
                print('\tHeader Not Found Error on ' + track.locations[0]) #, err )
                print(traceback.format_exc())
            error += 1
        except Exception as err:
            print('\n\t** Exception processing file ' + track.locations[0]  +':', err )
            print(traceback.format_exc())
            error += 1
        if (DEBUGSONG):
            print(trackmsg)

        

# Stats Output                          
print(str(insync) + ' files alread in sync')
print(str(justsynced) + ' newly synced files')
print(str(notag) + ' files with no tags')
print(str(error) + ' files had errors')
