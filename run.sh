#! /bin/bash

cat << EOF > .env
UID=$(id -u)
GID=$(id -g)
EOF

docker-compose build && docker-compose up -d
