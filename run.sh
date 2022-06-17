#!/bin/sh

while true;
do
	git add .gitignore
	git stash
	git pull
	python3 "bot.py" &
	sleep 21600 
	pkill python3
done
