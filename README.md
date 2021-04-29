# Shepherd

Shepherd is the team that is in charge of field control. 
Shepherd brings together all the data on the game field into one centralized location, where it keeps track of score, processes game-specific actions, keeps track of time, and informs the scoreboard.

## Running Shepherd (with Docker)

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

After you are done, be sure to stop the container to please Samuel.
```
docker stop sheep
```

## Running Shepherd (without Docker)

I will leave basic guidance in this section but since we are switching to Docker, it will be mediocre.

### Dependencies

If you are on windows, you probably won't be able to install LCM so you should use the Docker instructions. If you are on Linux, run the `./installlcm` script to install it. If on Mac, set your Java version to 8 `export JAVA_HOME=$(/usr/libexec/java_home -v 1.8)` and then run the `./installlcm` script.

For python dependencies, run `pip install -r requirements.txt`.

### Actually Running

Once you have all the dependencies, you can run Shepherd using:
```
python3 Shepherd.py
```
You can run the staff gui and scoreboard by doing the following in separate terminals:
```
python3 server.py
```
and
```
python3 scoreboard.py
```

## Running Sensors

For talking to sensors, we use a Shepherd specific version of `dev_handler`, which stands for device handler, and the Lowcar Framework which were written by Runtime. First, connect the Arduinos to your computer (they should have already been flashed).

If you are using docker (recommended), use `docker exec -it bash` to get a new terminal and `cd outsideshep`. If not, simply open a new terminal. Run the following:

```
cd shepherd/sensors
make clean && make
./dev_handler
```
Then, in another terminal, run the Shepherd code that interfaces with dev handler in another terminal.
```
cd shepherd
python3 Sensors.py
```

## Architecture

To read about Shepherd in detail, check out the [onboarding readme](https://github.com/pioneers/shepherd-onboarding#about-shepherd). This is where you will find detailed information about what each component of Shepherd does.

## 2021 Instructions

For competition, we have 5 different scripts to run. Matthew has created a tmux script that runs everything we need that we encourage you to modify in future years because it is really easy to use. Do this inside a terminal (not VSCode) so that you have space.

```
docker restart sheep
docker attach sheep
cd outsideshep/shepherd
./shepherd_tmux.sh
```
After you are done, be sure to stop the container to please Samuel.
```
docker stop sheep
```

One part of this that has not yet been tested is dev handler communication with Arduino devices. After that, Shepherd should be able to run straight out of the Docker container.

If you are not using docker, open a terminal, cd into shepherd and run
```
./shepherd_tmux.sh
```