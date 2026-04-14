# ── Stage 1: Build the Shiro vulnerable web application ───────────────────────
# Apache Shiro is a Java security framework; CVE-2016-4437 is a Java
# deserialization vulnerability, so Java/Maven are required here.
FROM maven:3.8.8-eclipse-temurin-8 AS builder

WORKDIR /build
COPY pom.xml .
# Pre-download dependencies as a separate cached layer
RUN mvn dependency:go-offline -B

COPY src/ src/
RUN mvn package -DskipTests -B

# ── Stage 2: Ubuntu 20.04 runtime (keeps the PwnKit-vulnerable environment) ───
FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

# Install only what is needed at runtime.
# polkit is intentionally kept at the Ubuntu 20.04 default (vulnerable to
# CVE-2021-4034 / PwnKit). Do NOT run apt-get upgrade.
RUN apt-get update && apt-get install -y --no-install-recommends \
    openjdk-8-jre \
    polkit \
    sudo \
    bash \
    && rm -rf /var/lib/apt/lists/*

# Ensure pkexec retains its SUID bit (required for CVE-2021-4034)
RUN chmod u+s /usr/bin/pkexec

# Copy the pre-built jar from the builder stage
COPY --from=builder /build/target/shiro-challenge-1.0.0.jar /app.jar

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
