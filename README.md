# plexmusic-rating-sync

Install Requirements with:

```bash
pip install -r requirements.txt
```

Running from docker (alternatively you can use PLEXTOKEN and PLEXURL to authenticate directly to the server)

```bash
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
-e RATINGID3EMAIL="user@example.com" \
-e RATINGFLACTAG="RATING:" \
-e RATINGFLACEMAIL="user@example.com" \
--rm \
-v "/volume1/music:/music:rw" \
tailslide/sync-plex-music-ratings:latest
```

Running outside of docker: Copy `.example.env` to `.env` and populate it with your secrets.
