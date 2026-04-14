# Shiro + PwnKit Challenge with Ranking

一个结合 Apache Shiro 反序列化 RCE 和 PwnKit 提权的网络安全靶场，附带实时排行榜。

A CTF-style security challenge combining Apache Shiro RememberMe deserialization RCE
(CVE-2016-4437) and PwnKit privilege escalation (CVE-2021-4034), with a live leaderboard
that auto-updates when contestants create their name-files in the target directories.

> ⚠️ **For educational / CTF use only. Run in an isolated environment.**

---

## Architecture

```
┌──────────────────────────────────────────────────┐
│  docker-compose                                  │
│                                                  │
│  ┌─────────────────┐    ┌──────────────────────┐ │
│  │  challenge :8080│    │  leaderboard :80     │ │
│  │                 │    │                      │ │
│  │ Spring Boot +   │    │ Python Flask         │ │
│  │ Shiro 1.2.4     │    │                      │ │
│  │ (CVE-2016-4437) │    │ Reads player files   │ │
│  │                 │    │ from shared volumes  │ │
│  │ Ubuntu 20.04 +  │    │                      │ │
│  │ polkit/pkexec   │    │ Serves HTML + JSON   │ │
│  │ (CVE-2021-4034) │    │ leaderboard API      │ │
│  └────────┬────────┘    └──────────┬───────────┘ │
│           │  volumes               │             │
│           │  user_players ─────────┤             │
│           │  root_players ─────────┘             │
└──────────────────────────────────────────────────┘
```

### Services

| Service       | Port | Description                                  |
|---------------|------|----------------------------------------------|
| `challenge`   | 8080 | Vulnerable Shiro web app + PwnKit environment|
| `leaderboard` | 80   | Live ranking board (auto-refreshes every 30s)|

---

## Quick Start

### Prerequisites

- Docker >= 20.10
- Docker Compose >= 1.29

### Run

```bash
git clone https://github.com/Yumeae/shiro-pwnkit-challenge-with-rank.git
cd shiro-pwnkit-challenge-with-rank
docker-compose up --build -d
```

- Challenge web app → http://\<host\>:8080
- Leaderboard       → http://\<host\>:80

---

## Challenge Walk-through

### Stage 1 — Shiro RememberMe RCE (CVE-2016-4437)

Apache Shiro ≤ 1.2.4 ships with a **hardcoded AES key** (`kPH+bIxk5D2deZiIxcaaaA==`) used
to encrypt the `rememberMe` cookie.  An attacker can forge a cookie that contains a
serialized Java payload (e.g. via Commons Collections gadget chain) to achieve RCE.

1. Navigate to `http://<host>:8080/login`
2. Log in with **Remember Me** checked (credentials: `admin` / `admin123`)
3. Craft a malicious `rememberMe` cookie using ysoserial or shiro-exploit tools
4. Send the crafted cookie to the server → get a reverse shell as user `ctf`
5. Read `/home/ctf/flag.txt` for the flag and leaderboard instructions
6. Run: `touch /home/ctf/players/<YOUR_NICKNAME>`

### Stage 2 — PwnKit Privilege Escalation (CVE-2021-4034)

The container runs Ubuntu 20.04 with a vulnerable version of `polkit` (`pkexec`).
PwnKit allows any unprivileged local user to escalate to `root`.

1. From the `ctf` shell obtained in Stage 1
2. Download and compile a PwnKit exploit (e.g. https://github.com/ly4k/PwnKit)
3. Execute it → get a root shell
4. Read `/root/flag.txt` for the root flag and leaderboard instructions
5. Run: `touch /root/players/<YOUR_NICKNAME>`

### Leaderboard

The leaderboard at `http://<host>:80` reads the filenames from:

- `/home/ctf/players/`  → **User Access** ranking
- `/root/players/`      → **Root Access** ranking

Rankings are sorted by file modification time (first solver = rank 1) and
auto-refresh every **30 seconds**.

---

## Directory Layout

```
.
├── docker-compose.yml
├── challenge/                    # Vulnerable target machine
│   ├── Dockerfile
│   ├── entrypoint.sh
│   ├── pom.xml                   # Maven build: Spring Boot + Shiro 1.2.4
│   └── src/
│       └── main/
│           ├── java/com/ctf/shiro/
│           │   ├── Application.java
│           │   ├── config/ShiroConfig.java     # Hardcoded rememberMe key
│           │   ├── realm/UserRealm.java
│           │   └── controller/HomeController.java
│           └── resources/
│               ├── application.properties
│               └── templates/
│                   ├── login.html
│                   └── index.html
└── leaderboard/                  # Ranking service
    ├── Dockerfile
    ├── app.py                    # Flask API + file reader
    ├── requirements.txt
    └── templates/
        └── index.html            # Hacker-themed dual leaderboard UI
```

---

## Flags

| Stage | File              | Default value                                |
|-------|-------------------|----------------------------------------------|
| User  | `/home/ctf/flag.txt` | `flag{user_b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8}` |
| Root  | `/root/flag.txt`     | `flag{root_f0e1d2c3b4a5968778695a4b3c2d1e0f}` |

> Customize the flag values in `challenge/Dockerfile` before deployment.

---

## Stopping

```bash
docker-compose down
```

To also remove the leaderboard player data volumes:

```bash
docker-compose down -v
```
