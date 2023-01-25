.\venv\scripts\pip.exe freeze >> requirements.txt
docker build --tag tailslide/sync-plex-music-ratings .
docker scan tailslide/sync-plex-music-ratings --severity high
echo listing files
pause
docker run --rm tailslide/sync-plex-music-ratings ls -alR
rem can't run this remotely on my dev machine must run on plex server on me setup
rem echo running built container
rem pause
rem docker run --env-file=.\.env tailslide/sync-plex-music-ratings
echo pushing to dockerhub
pause
docker push tailslide/sync-plex-music-ratings:latest
