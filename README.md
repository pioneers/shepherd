# Shepherd

Shepherd is the team that is in charge of field control. 
Shepherd brings together all the data on the game field into one centralized location, where it keeps track of score, processes game-specific actions, keeps track of time, and informs the scoreboard.

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

## Architecture

To read about Shepherd in detail, check out the [onboarding readme](https://github.com/pioneers/shepherd-onboarding#about-shepherd).

## 2021 Instructions

For competition, we have 6 different scripts to run. Matthew has created a tmux script that we encourage you to modify in future years because it is really easy to use.

```
docker restart sheep
docker attach
cd outsideshep/shepherd
./shepherd_tmux.sh
```

One part of this that has not yet been tested is dev handler communication with Arduino devices. After that, Shepherd should be able to run straight out of the Docker container.