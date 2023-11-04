# plexmusic-rating-sync

Install Requirements with:

```
pip install -r requirements.txt
```

Running from docker (alternatively you can use PLEXTOKEN and PLEXURL to authenticate directly to the server)

```
docker run \
-e PYTHONUNBUFFERED=1 \
-e PLEXSERVER="127.0.0.1" \
-e PLEXUSER="myplexusername" \
-e PLEXPW="myplexpassword" \
-e PLEXLIB="NAS5" \
-e PLEXREPLACEFROM="/volume1/music" \
-e PLEXREPLACETO="/music" \
-e UPDATEFILE="false" \
-e UPDATEPLEX="false" \
-e DEBUGRESOURCES="false" \
-e DEBUGSONG="false" \
-e DEBUGALBUM="false" \
-e LOGNOID3ERROR="true" \
-e LOGNOHEADERNOTFOUNDERROR="false" \
-e LOGINVALIDCHUNKERROR="true" \
-e LOGALLRATINGS="false" \
-e SHOWPROGRESS="true" \
-e RATINGEMAIL="no@email" \
-e FLACRATINGTAG="RATING" \
--rm \
-v "/volume1/music:/music:rw" \
tailslide/sync-plex-music-ratings:latest
```

Running outside of docker: Create a .env file and populate it with your secrets:

```
PLEXSERVER="127.0.0.1"
PLEXUSER="plexusername"
PLEXPW="plexpassword"
PLEXLIB="MYNAS1"
PLEXREPLACEFROM = "/volume1/music"
PLEXREPLACETO = "\\MYNAS1\music"
UPDATEFILE="false"
UPDATEPLEX="false"
DEBUGSONG="false"
LOGNOID3ERROR="true"
LOGNOHEADERNOTFOUNDERROR="false"  #known issue in mutagen https://github.com/quodlibet/mutagen/issues/562
LOGINVALIDCHUNKERROR="true" #known issue in mutagen https://github.com/quodlibet/mutagen/issues/592
LOGALLRATINGS="false"
SHOWPROGRESS="true"
RATINGEMAIL="no@email"
FLACRATINGTAG="RATING"
```

