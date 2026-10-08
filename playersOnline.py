#watch minecraft server docker container logs
#if x joined the game, add +1 to player count
#if x left the game, subtract -1 from player count
import json
import subprocess
from pathlib import Path

CONTAINER = 'mcserver'
STATE_FILE = Path.home() / 'mc_players.json'

def loadPlayers():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except json.JSONDecodeError:
            pass
    return {}

def getPlayers():
    players = loadPlayers()
    try:
        result = subprocess.run(['docker', 'logs', 'mcserver', '--tail', '20'], capture_output=True, text=True) 
        output = result.stdout + result.stderr
    except (subprocess.SubprocessError, OSError):
        return players 
    for line in output.split('\n'):
            if '<' in line:
                continue
            if 'joined' in line:
                name = line.split(']: ')[1].split()[0]
                players[name] = True
            elif 'left' in line:
                name = line.split(']: ')[1].split()[0]
                players[name] = False
    STATE_FILE.write_text(json.dumps(players, indent=2))
    return players
def getPlayerSummary():
    players = getPlayers()
    online = sorted(n for n, is_on in players.items() if is_on)
    return {'count': len(online), 'names': online}
