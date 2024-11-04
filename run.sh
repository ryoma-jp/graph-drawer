#! /bin/bash

cat << EOF > .env
UID=$(id -u)
GID=$(id -g)
EOF

docker-compose up -d --build
