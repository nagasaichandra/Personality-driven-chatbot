#!/bin/sh
docker run -it -v $(pwd):/rasabot 582rasa shell


# docker run -d -v $(pwd)/actions:/app/actions --net my-project --name action-server rasa/rasa-sdk:1.10.1

