# USE AT YOUR OWN RISK!
#
# Requires eyed3 and plexapi libraries
# Written and tested in Python 3.9
#
# Plex ratings 0.0-10.0
# FLAC ratings
# - MediaMonkey 0-100
# - MusicBee 0-255
# - MusicBrainz Picard 0.0-1.0
# - Others 0-5
# ID3 ratings 0-255

from plexapi.myplex import MyPlexAccount
from plexapi.server import PlexServer
import mutagen
import mutagen.id3
import os
import io
import traceback
from dotenv import load_dotenv
from mutagen import id3
from mutagen._iff import InvalidChunk
from mutagen.mp3 import HeaderNotFoundError
from mutagen.id3 import ID3, COMR, Frames, Frames_2_2, ID3Warning, ID3JunkFrameError, ID3NoHeaderError

load_dotenv()

LIB = os.getenv('PLEXLIB')
PLEXUSER = os.getenv('PLEXUSER')
PLEXPW = os.getenv('PLEXPW')
PLEXTOKEN = os.getenv('PLEXTOKEN')
PLEXURL = os.getenv('PLEXURL')
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
RATINGEMAIL = os.getenv('RATINGEMAIL')
RATINGID3TAG = "POPM:" + RATINGEMAIL
FLACRATINGTAG = os.getenv('FLACRATINGTAG')

# Counters
insync = 0
justsynced = 0
notag = 0
error = 0

def makeRemoteString(str):
    if (PLEXREPLACEFROM is None or PLEXREPLACEFROM == ""):
        return str
    else:
        return str.replace(PLEXREPLACEFROM, PLEXREPLACETO)

def convertRatingsFromId3ToPlex(n):
    return round(float(float(n / 255) * float(10)), 1)

def convertRatingsFromPlexToId3(n):
    return int(float(n / 10) * float(255))

def convertRatingsFromFlacToPlex(n):
    if (n <= 5):
        return float(n) * 2
    else:
        return float(float(n) / float(10))

def convertRatingsFromPlexToFlac(n):
    return int(round(n * 10, 0))

def print_to_string(*args, **kwargs):
    output = io.StringIO()
    print(*args, file = output, **kwargs)
    contents = output.getvalue()
    output.close()
    return contents

def getFile(localfile):
    try:
        file = mutagen.File(localfile)
        return file
    except InvalidChunk as ic:
        # error!
        raise
    except HeaderNotFoundError as hnf:
        # error!
        raise
    except Exception as ex:
        # error!
        raise

def convertPlexRatingToFileRating(file, plexrating):
    try:
        filerating = getFileRating(file)
        if (type(file) is mutagen.flac.FLAC):
            return convertRatingsFromPlexToFlac(plexrating)
        else:
            return convertRatingsFromPlexToId3(plexrating)
    except Exception as ex:
        # error!
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
        # error!
        raise
    except HeaderNotFoundError as hnf:
        # error!
        raise
    except Exception as ex:
        # error!
        raise

def getFileRating(file):
    try:
        if (type(file) is mutagen.flac.FLAC):
            if ((FLACRATINGTAG in file.tags) and (file.tags[FLACRATINGTAG] is not None)):
                ratings = file.tags[FLACRATINGTAG]
                ratingnum = int(ratings[0]) if ratings[0].isdigit() else None
                return ratingnum # tags are always arrays for some weird reason
        else:
            if RATINGID3TAG in file:
                if (file[RATINGID3TAG] is not None):
                    return file[RATINGID3TAG].rating
        return None
    except Exception as ex:
        # error!
        raise

def updateFileRating(file, filerating):
    try:
        if (type(file) is mutagen.flac.FLAC):
            updateFlacRating(file, filerating)
        elif (type(file) is mutagen.mp3.MP3):
            updateID3Rating(file, filerating)
        else:
            print('***unknown file type:', type(file))
    except Exception as ex:
        # error!
        raise

def updateFlacRating(file, filerating):
    try:
        print(' to rating:', filerating)
        file.tags[FLACRATINGTAG] = str(filerating)
        file.save()
    except Exception as ex:
        # error!
        raise

def updateID3Rating(file, filerating):
    try:
        if RATINGID3TAG in file:
            tag = file[RATINGID3TAG]
            tag.rating = filerating
        else:
            frame = mutagen.id3.POPM(email = RATINGEMAIL, rating = filerating)
            file.tags.add(frame)

        file.save()
    except Exception as ex:
        # error!
        raise

print("Start. Connecting to Plex with user " + PLEXUSER)
if (UPDATEFILE):
    print("Will update files if existing rating in Plex")
else:
    print("Will **NOT** update files if existing rating in Plex")

if (UPDATEPLEX):
    print("Will update Plex if existing rating in files")
else:
    print("Will **NOT** update Plex if existing rating in files")

if (PLEXTOKEN != None):
    plex = PlexServer(PLEXURL, PLEXTOKEN)
    print('Connected with token')
else:
    account = MyPlexAccount(PLEXUSER, PLEXPW)
    if (DEBUGRESOURCES):
        resources = account.resources()
        print("Found the following resources:")
        for res in resources:
            print(res)

    plex = account.resource(LIB).connect()
    print('Connected with password')

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
        try:
            trackmsg = ""
            localfile = makeRemoteString(track.locations[0])
            file = getFile(localfile)
            fileplexrating = getFileRatingAsPlexRating(file)
            filerating = getFileRating(file)

            if isinstance(track.userRating, float):
                # Checks to see if the Plex userRating exists, var type will be float if track is rated, it will be nonetype if not.
                trackmsg = print_to_string('\t' + track.title + ' is already rated in Plex')
                newrating = convertPlexRatingToFileRating(file, track.userRating)
                if ((filerating == None) or (fileplexrating != track.userRating)):
                    if (UPDATEFILE):
                        print('\t**Updating file ' + track.locations[0] + ' from rating:', filerating, ' to rating:', newrating)
                        # Ratings on both? We prefer Plex to dictate for now, so we always write it on the file if present
                        updateFileRating(file, newrating)
                        justsynced += 1
                    else:
                        print('\t**Run in update mode to update file ' + track.locations[0] + ' from rating:', filerating, ' to rating:', newrating)
                elif (fileplexrating == track.userRating):
                    insync += 1
            else:
                # This case is where Plex has no rating so it tries to fetch a value from the metadata rating tag
                trackmsg = print_to_string('\t "' + track.title + '" (' + track.locations[0] + ') has no rating in Plex, checking file metadata rating tag. ', end = '')

                if (fileplexrating is not None):
                    if (UPDATEPLEX):
                        # This case is where Plex has no rating but the metadata rating tag does so the next steps import the rating into Plex.
                        print('\t"' + track.title + '" (' + track.locations[0] + ') metadata rating tag rating ' + str(filerating) + ' found and saved to Plex userRating field as ' + str(fileplexrating))
                        track.rate(fileplexrating)
                        justsynced += 1
                    else:
                        print('\t**Run in update mode to update Plex song ' + str(album) + ": " + track.title + ' to rating:', fileplexrating)
                else:
                    trackmsg = trackmsg + print_to_string('No tag present in file or Plex.')
                    notag += 1
        except ID3NoHeaderError as noid3:
            if (LOGNOID3ERROR):
                print('\tNo ID3 tag found on ' + track.locations[0])
                print(traceback.format_exc())
            error += 1
        except InvalidChunk as ic:
            if (LOGINVALIDCHUNKERROR):
                print('\tInvalid chunk on ' + track.locations[0])
                print(traceback.format_exc())
            # error!
            error += 1
        except HeaderNotFoundError as hnf:
            if (LOGNOHEADERNOTFOUNDERROR):
                print('\tHeader not found error on ' + track.locations[0])
                print(traceback.format_exc())
            error += 1
        except Exception as err:
            print('\n\t** Exception processing file ' + track.locations[0] +':', err)
            print(traceback.format_exc())
            error += 1
        if (DEBUGSONG):
            print(trackmsg)

# Stats
print(str(insync) + ' files already in sync')
print(str(justsynced) + ' newly synced files')
print(str(notag) + ' files with no tags')
print(str(error) + ' files had errors')
