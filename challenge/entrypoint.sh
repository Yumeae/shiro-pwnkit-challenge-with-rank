#!/bin/bash
set -e

# Ensure players directories are writable after volume mount
chmod 777 /home/ctf/players 2>/dev/null || true
chmod 777 /root/players 2>/dev/null || true
chown ctf:ctf /home/ctf/players 2>/dev/null || true

# Ensure pkexec (wrapper and original) retains its SUID bit
chmod u+s /usr/bin/pkexec /usr/bin/pkexec.orig 2>/dev/null || true

# ── PwnKit cleanup daemon ─────────────────────────────────────────────────────
# Every 5 minutes, remove common PwnKit exploit binaries from the ctf user's
# home directory and /tmp.  This raises the difficulty: players must exploit
# quickly or re-upload their tool after each sweep.
(
    while true; do
        sleep 300
        find /home/ctf /tmp -maxdepth 3 \
            \( -name 'PwnKit' -o -name 'pwnkit' -o -name 'pwnkit.*' \
               -o -name 'CVE-2021-4034' -o -name 'cve-2021-4034' \
               -o -name 'pkexec-exploit' -o -name 'pwnkit-exploit' \
               -o -name 'evil.so' -o -name 'evil-so.c' \) \
            -delete 2>/dev/null || true
    done
) &

# Start the Spring Boot / Shiro application as the ctf user
exec su -s /bin/bash ctf -c \
    "java -jar /app.jar --server.port=8080 --leaderboard.url=${LEADERBOARD_URL:-http://localhost:80}"
