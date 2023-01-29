#!/bin/bash

# Start the run once job.
echo "Docker container has been started"

# Setup a cron schedule
echo "* * * * * /cron.py
# This extra line makes it a valid cron" > scheduler.txt

crontab scheduler.txt
cron -f