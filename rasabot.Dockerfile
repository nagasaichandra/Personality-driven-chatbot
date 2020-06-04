# get rasa image
FROM rasa/rasa:1.10.2-full

# build arguments for ENV
ARG RASA_ACTION_ENDPOINT_ARG="http://localhost:5055/webhook"
ARG RASA_IRC_CHANNEL_ARG="#CPE582"
ARG RASA_IRC_NICKNAME_ARG="plato"
ARG RASA_IRC_SERVER_ARG="irc.freenode.net"
ARG RASA_IRC_PORT_ARG=6667

ARG RASA_IRC_WEBHOOK_BASE_URL_ARG="http://localhost:5005"
ARG RASA_IRC_WEBHOOK_PATH_ARG="/webhooks/rest/webhook"
ARG RASA_IRC_CHANNEL_ARG="#CPE582"
ARG RASA_IRC_SERVER_ARG="irc.freenode.net"
ARG RASA_IRC_PORT_ARG=6667
ARG RASA_SHELL_STREAM_READING_TIMEOUT_IN_SECONDS_ARG=10

# setup environment variables
# rasa
ENV RASA_ACTION_ENDPOINT=${RASA_ACTION_ENDPOINT_ARG}
# irc
ENV RASA_IRC_CHANNEL=${RASA_IRC_CHANNEL_ARG}
ENV RASA_IRC_NICKNAME=${RASA_IRC_NICKNAME_ARG}
ENV RASA_IRC_SERVER=${RASA_IRC_SERVER_ARG}
ENV RASA_IRC_PORT=${RASA_IRC_PORT_ARG}
# irc worker
ENV RASA_IRC_WEBHOOK_BASE_URL=${RASA_IRC_WEBHOOK_BASE_URL_ARG}
ENV RASA_IRC_WEBHOOK_PATH=${RASA_IRC_WEBHOOK_PATH_ARG}
ENV RASA_IRC_CHANNEL=${RASA_IRC_CHANNEL_ARG}
ENV RASA_IRC_SERVER=${RASA_IRC_SERVER_ARG}
ENV RASA_IRC_PORT=${RASA_IRC_PORT_ARG}
ENV RASA_SHELL_STREAM_READING_TIMEOUT_IN_SECONDS=${RASA_SHELL_STREAM_READING_TIMEOUT_IN_SECONDS_ARG}

# copy source code over to image
COPY rasabot/ /rasabot

CMD ["rasa", "run", "-vv", \
    "--model", "rasabot/models", \
    "--verbose" \
    "--credentials", "rasabot/credentials.yml", \
    "--endpoints", "rasabot/endpoints.yml", \
    "--debug", \
    "--enable-api", \
    "--connector", "rasabot.irc_channel.IRCInput" ]
