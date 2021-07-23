#!/bin/sh

TIMEOUT="5s"

while : ; do
  pipenv run python main.py
  echo "Restarting in $TIMEOUT"
  sleep $TIMEOUT
done
echo "Somehow returned from infinite loop. Time to start panicking."
