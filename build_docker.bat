.\venv\scripts\pip.exe freeze >> requirements.txt
docker build --tag tailslide/sync-plex-music-ratings .
docker scan tailslide/sync-plex-music-ratings --severity high
echo listing files
pause
docker run --rm tailslide/sync-plex-music-ratings ls -alR
echo running built container
pause
docker run --env-file=.\.env tailslide/sync-plex-music-ratings
echo pushing to dockerhub
pause
docker push tailslide/sync-plex-music-ratings:latest
