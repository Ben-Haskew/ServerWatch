#watch minecraft server docker container logs
#if x joined the game, add +1 to player count
#if x left the game, subtract -1 from player count
import subprocess

def getTempsLinux():
    result = subprocess.run(['docker', 'logs', 'mcserver', '--tail', '20'], capture_output=True, text=True) 
    output = result.stdout + result.stderr
    players = {}
    for line in output.split('\n'):
            if 'joined' in line:
                name = line.split(']: ')[1].split()[0]
                players[name] = True
            elif 'left' in line:
                name = line.split(']: ')[1].split()[0]
                players[name] = False

    return players
if __name__ == '__main__':
    players = getTempsLinux()

    online = [name for name, isOnline in players.items() if isOnline]
    print(f"Online: {len(online)} {online}")
