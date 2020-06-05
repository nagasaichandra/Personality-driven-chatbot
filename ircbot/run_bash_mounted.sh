#!/bin/sh
docker run -it -v $(pwd):/ircbot --entrypoint /bin/bash --name 582ircbot-bash-mounted 582ircbot "$@"

