#!/bin/sh
# https://rasa.com/docs/rasa/user-guide/docker/building-in-docker/#installing-docker
docker run -v $(pwd):/app rasa/rasa:1.10.2-full init --no-prompt

