import os
import time
from flask import Flask, jsonify, render_template

app = Flask(__name__)

NORMAL_DIR = os.environ.get("NORMAL_DIR", "/data/normal")
ROOT_DIR = os.environ.get("ROOT_DIR", "/data/root")

# Files to exclude from leaderboard listings
EXCLUDED_NAMES = {
    "flag.txt", ".bashrc", ".bash_logout", ".bash_profile",
    ".profile", ".bash_history", ".cache", ".config",
    "lost+found", ".", "..",
}


def list_players(directory: str) -> list:
    """
    Read all filenames from *directory*, exclude system/flag files,
    and return a sorted list of (rank, name, timestamp) dicts.
    """
    entries = []
    try:
        for name in os.listdir(directory):
            if name in EXCLUDED_NAMES or name.startswith("."):
                continue
            full_path = os.path.join(directory, name)
            try:
                stat = os.stat(full_path)
                entries.append({
                    "name": name,
                    "ts": int(stat.st_mtime),
                })
            except OSError:
                continue
    except FileNotFoundError:
        pass

    # Sort by creation/modification time ascending (first solver ranks first)
    entries.sort(key=lambda e: e["ts"])

    result = []
    for rank, entry in enumerate(entries, start=1):
        result.append({
            "rank": rank,
            "name": entry["name"],
            "time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(entry["ts"])),
        })
    return result


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/leaderboard")
def leaderboard():
    return jsonify({
        "user": list_players(NORMAL_DIR),
        "root": list_players(ROOT_DIR),
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
