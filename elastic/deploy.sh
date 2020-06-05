#!/bin/sh

# runs the `CMD` defined in the Dockerfile
docker run --detach --publish 9200:9200 --publish 9300:9300 -e "discovery.type=single-node" --name 582elastic-standalone 582elastic
