import threading
import subprocess

def run_script(s):
    subprocess.run(["python", s], check=True)

threading.Thread(target=run_script, args=("server.py",)).start()
threading.Thread(target=run_script, args=("shepherd.py",)).start()
threading.Thread(target=run_script, args=("ydl.py",)).start()
