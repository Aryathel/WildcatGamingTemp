:loop
pipenv run py main.py
timeout /t 5
goto loop
PAUSE
ECHO "Somehow returned from infinite loop. Time to start panicking."
