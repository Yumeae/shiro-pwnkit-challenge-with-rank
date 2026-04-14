FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

# Install Java 8, Maven and polkit (vulnerable version is present in Ubuntu 20.04 base)
RUN apt-get update && apt-get install -y --no-install-recommends \
    openjdk-8-jdk \
    maven \
    polkit \
    sudo \
    curl \
    bash \
    && rm -rf /var/lib/apt/lists/*

# Ensure pkexec retains its SUID bit (required for CVE-2021-4034)
RUN chmod u+s /usr/bin/pkexec

# ── Build the Shiro challenge application ──────────────────────────────────────
WORKDIR /build
COPY pom.xml .
# Pre-download Maven dependencies (caches this layer separately from source)
RUN mvn dependency:go-offline -B

COPY src/ src/
RUN mvn package -DskipTests -B && \
    cp target/shiro-challenge-1.0.0.jar /app.jar && \
    cd / && rm -rf /build

# ── Create CTF user ────────────────────────────────────────────────────────────
RUN useradd -m -s /bin/bash ctf && \
    echo 'ctf:ctf' | chpasswd

# Allow ctf user to write to its own players directory
RUN mkdir -p /home/ctf/players /root/players && \
    chown ctf:ctf /home/ctf/players && \
    chmod 755 /home/ctf/players && \
    chmod 777 /root/players

# ── Flag files ─────────────────────────────────────────────────────────────────
# User-level flag
RUN printf '============================================================\n\
Congratulations! You have obtained USER access via Shiro RCE!\n\
============================================================\n\
\n\
Flag: flag{user_b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8}\n\
\n\
To appear on the LEADERBOARD, create a file with your name:\n\
\n\
    touch /home/ctf/players/YOUR_NICKNAME\n\
\n\
Good luck with the next step: privilege escalation via PwnKit!\n\
============================================================\n' \
    > /home/ctf/flag.txt && \
    chown ctf:ctf /home/ctf/flag.txt && \
    chmod 444 /home/ctf/flag.txt

# Root-level flag
RUN printf '============================================================\n\
Congratulations! You have escalated to ROOT via PwnKit!\n\
============================================================\n\
\n\
Flag: flag{root_f0e1d2c3b4a5968778695a4b3c2d1e0f}\n\
\n\
To appear on the ROOT LEADERBOARD, create a file with your name:\n\
\n\
    touch /root/players/YOUR_NICKNAME\n\
\n\
You have fully pwned this machine!\n\
============================================================\n' \
    > /root/flag.txt && \
    chmod 444 /root/flag.txt

# ── Entrypoint ─────────────────────────────────────────────────────────────────
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8080

ENTRYPOINT ["/entrypoint.sh"]
