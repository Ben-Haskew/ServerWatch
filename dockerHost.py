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
    result = subprocess.run(['docker', 'logs', 'mcserver', '--tail', '20'], capture_output=True, text=True) 
    output = result.stdout + result.stderr
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
if __name__ == '__main__':
    players = getPlayers()
    print(players)
    print(f"Players online: {sum(players.values())}")
