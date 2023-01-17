# plexmusic-rating-sync

Install Requirments with:

```
pip install -r requirements.txt
```

Create a .env file and populate it with your secrets:

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
LOGNOID3ERROR="false"
LOGALLRATINGS="false"
SHOWPROGRESS="true"
RATINGID3TAG="POPM:no@email"
```

Running from docker

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
-e LOGNOID3ERROR="false" \
-e LOGALLRATINGS="false" \
-e SHOWPROGRESS="true" \
-e RATINGID3TAG="POPM:no@email" \
-v "/volume1/music:/music:rw" \
tailslide/sync-plex-music-ratings:latest
```