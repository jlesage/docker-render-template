#!/bin/sh

DOCKER_OPTS=
DOCKER_CMD_ARGS=

for ARG in "$@"; do
    if [ -f "$ARG" ]; then
        FILE="$(readlink -f "$ARG")"
        DOCKER_OPTS="$DOCKER_OPTS -v \"$FILE:$FILE:ro\""
        DOCKER_CMD_ARGS="$DOCKER_CMD_ARGS \"$FILE\""
    else
        DOCKER_CMD_ARGS="$DOCKER_CMD_ARGS \"$ARG\""
    fi
done

eval "docker run --rm $DOCKER_OPTS jlesage/render-template $DOCKER_CMD_ARGS"
