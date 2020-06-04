#!/bin/sh

# # https://rasa.com/docs/rasa/user-guide/connectors/your-own-website/#rest-channels

# # https://stackoverflow.com/a/2013589
# # export RASA_ACTION_ENDPOINT=${RASA_ACTION_ENDPOINT:="http://localhost:5055/webhook"}

export RASA_IRC_CHANNEL=${RASA_IRC_CHANNEL:="#CPE582"}
export RASA_IRC_NICKNAME=${RASA_IRC_NICKNAME:="plato"}
export RASA_IRC_SERVER=${RASA_IRC_SERVER:="irc.freenode.net"}
export RASA_IRC_PORT=${RASA_IRC_PORT:="6667"}

echo "RASA_IRC_CHANNEL is " $RASA_IRC_CHANNEL
echo "RASA_IRC_NICKNAME is " $RASA_IRC_NICKNAME
echo "RASA_IRC_SERVER is " $RASA_IRC_SERVER
echo "RASA_IRC_PORT is " $RASA_IRC_PORT

# it's really just RestInput
rasa run -vv \
    --model rasabot/models \
    --verbose \
    --credentials rasabot/credentials.yml \
    --endpoints rasabot/endpoints.yml \
    --debug \
    --enable-api \
    --connector rasabot.irc_channel.IRCInput \
    "$@"
