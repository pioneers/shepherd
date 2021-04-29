# Shepherd

Shepherd is the team that is in charge of field control. 
Shepherd brings together all the data on the game field into one centralized location, where it keeps track of score, processes game-specific actions, keeps track of time, and informs the scoreboard.

## Architecture

Shepherd is essentially a [Flask](https://palletsprojects.com/p/flask/) web app that communicates with:

* Arduino devices on the field over USB serial.
* Each robot's [Runtime](https://github.com/pioneers/PieCentral/tree/master/runtime) instance using MessagePack remote procedure calls over TCP.
* Each driver station's [Dawn](https://github.com/pioneers/PieCentral/tree/master/dawn) instance.
* Each scoreboard client, which is rendered with jQuery. Typically, there is a scoreboard on each side of the field, a projection for spectators, and a fourth for the field control staff.
* Each perk selection tablet (specific to Sugar Blast).

## Running Shepherd

See the [docker instructions](https://github.com/pioneers/shepherd/blob/docker/setup/howtodocker.md) to pull and create the docker container as well as run Shepherd. If you have already created the container and added the `whale` [alias](https://github.com/pioneers/shepherd/blob/docker/setup/howtodocker.md#setting-up-the-docker-container), you can run the following:
```
docker restart sheep
whale Shepherd.py
```

This will run Shepherd. Based on what you are working on, you may also want to run the staff gui or the scoreboard, which can be done as follows (in seperate terminals)

```
whale server.py
```
and 
```
whale scoreboard_server.py
```

`whale` is short for `docker exec -it sheep run`.

## Running Sensors

For talking to sensors, we use a Shepherd specific version of `dev_handler`, which stands for device handler, and the Lowcar Framework which were written by Runtime. First, connect the Arduinos to your computer (they should have already been flashed). Then run the following:
```
cd shepherd/sensors
make clean && make
./dev_handler
```
Then, run the Shepherd code that interfaces with dev handler in another terminal.
```
cd shepherd
python3 Sensors.py
```

## 2021 Instructions

For competition, we have 6 different scripts to run. Matthew has created a tmux script that we encourage you to modify in future years because it is really easy to use.

```
docker restart sheep
docker attach
cd outsideshep/shepherd
./shepherd_tmux.sh
```
This _almost_ works but **TODO**: we need to modify the docker run command so that dev_handler can talk to serial. Otherwise, the `Sensors.py` terminal will error.