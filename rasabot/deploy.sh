# make a network for main rasa and rasa action server to talk
# https://rasa.com/docs/rasa/user-guide/docker/building-in-docker/
docker network create rasa-network 

# run rasa in its own container in the background
docker run --detach --publish 5005:5005 --name 582rasa-standalone --net rasa-network 582rasa run 

# run rasa action server in its own container in the background
docker run --detach --publish 5055:5055 --name 582rasa-actions-standalone --net rasa-network 582rasa \
    run -vv actions --debug

