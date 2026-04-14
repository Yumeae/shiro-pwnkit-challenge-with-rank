#!/bin/bash
set -e

# Ensure players directories are writable after volume mount
chmod 777 /home/ctf/players 2>/dev/null || true
chmod 777 /root/players 2>/dev/null || true
chown ctf:ctf /home/ctf/players 2>/dev/null || true

# Start the Spring Boot / Shiro application as the ctf user
exec su -s /bin/bash ctf -c \
    "java -jar /app.jar --server.port=8080 --leaderboard.url=${LEADERBOARD_URL:-http://localhost:80}"
