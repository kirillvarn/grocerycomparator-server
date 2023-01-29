cron # this starts the cron process
TMP # some commands we need to run next to cron command (we prepare app env here)

# Append CMD from Dockerfile NOTE this is important so you can then use CMD after ENTRYPOINT inside DOCKERFILE
exec "$@"