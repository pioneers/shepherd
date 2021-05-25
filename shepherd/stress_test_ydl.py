import queue
import time
from YDL import ydl_send, ydl_start_read


NUM_TO_SEND = 40000
PAYLOAD = {
    "pp": "C"*10
}

incoming = queue.Queue()
ydl_start_read("dummy_cheese", incoming)

tt = time.time()
print("sending")

for a in range(NUM_TO_SEND):
    ydl_send("dummy_cheese", "cheese", PAYLOAD)

print("receiving ({})".format(time.time() - tt))

recd = 0
while recd < NUM_TO_SEND:
    while not incoming.empty():
        incoming.get()
        recd += 1
    time.sleep(0.00001)

print("done ({})".format(time.time() - tt))
