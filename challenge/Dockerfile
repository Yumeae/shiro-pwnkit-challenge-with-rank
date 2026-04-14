# ── Shiro + PwnKit CTF Challenge ───────────────────────────────────────────────
#
# The vulnerable Shiro 1.2.4 application is shipped as a pre-built JAR
# (app.jar) so that no pom.xml with vulnerable Maven coordinates needs to
# exist in this repository.  The JAR was compiled once from the reference
# source in src-reference/ and is committed as a binary.
#
# Vulnerability surface (intentional CTF targets):
#   Stage 1 — CVE-2016-4437  Apache Shiro 1.2.4 hardcoded rememberMe key
#              (commons-collections 3.2.1 gadget chain inside the JAR)
#   Stage 2 — CVE-2021-4034  polkit pkexec SUID privilege escalation (PwnKit)
#
# DO NOT expose this container to untrusted networks.
# See SECURITY_NOTICE.md for the full isolation checklist.
# ──────────────────────────────────────────────────────────────────────────────

FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

# Ubuntu 20.04 (Focal) reached EOL in April 2025; archive.ubuntu.com and
# old-releases.ubuntu.com may not reliably serve focal packages.
# Use the official Ubuntu snapshot archive pinned to December 2021 — before the
# polkit CVE-2021-4034 patch (USN-5252-1, January 2022) — so that:
#   • Packages are always resolvable regardless of mirror/EOL status.
#   • The vulnerable polkit version required for the PwnKit CTF stage is installed.
# Acquire::Check-Valid-Until=false is required because the snapshot Release files
# have a ValidUntil timestamp that has long since passed.
RUN printf 'deb http://snapshot.ubuntu.com/ubuntu/20211201T000000Z focal main restricted universe multiverse\n\
deb http://snapshot.ubuntu.com/ubuntu/20211201T000000Z focal-updates main restricted universe multiverse\n\
deb http://snapshot.ubuntu.com/ubuntu/20211201T000000Z focal-security main restricted universe multiverse\n' \
    > /etc/apt/sources.list && \
    printf 'Acquire::Check-Valid-Until "false";\n' \
    > /etc/apt/apt.conf.d/99snapshot

# Install only the runtime packages needed.
# polkit is intentionally kept at the Ubuntu 20.04 default version which is
# vulnerable to CVE-2021-4034 (PwnKit). Do NOT run apt-get upgrade.
RUN apt-get update && apt-get install -y --no-install-recommends \
    openjdk-8-jre \
    polkit \
    sudo \
    bash \
    && rm -rf /var/lib/apt/lists/*

# Ensure pkexec retains its SUID bit (required for CVE-2021-4034)
RUN chmod u+s /usr/bin/pkexec

# ── Deploy the pre-built Shiro 1.2.4 application ──────────────────────────────
# app.jar is a Spring Boot fat-jar built from src-reference/ and committed as
# a binary so that no Maven manifest (pom.xml) is required in the repository.
COPY app.jar /app.jar

# ── Create CTF user ────────────────────────────────────────────────────────────
RUN useradd -m -s /bin/bash ctf && \
    echo 'ctf:ctf' | chpasswd

# Allow ctf user to write to its own players directory
RUN mkdir -p /home/ctf/players /root/players && \
    chown ctf:ctf /home/ctf/players && \
    chmod 755 /home/ctf/players && \
    chmod 777 /root/players

# ── Flag files ─────────────────────────────────────────────────────────────────
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

ENV LEADERBOARD_URL=http://localhost:80

ENTRYPOINT ["/entrypoint.sh"]
