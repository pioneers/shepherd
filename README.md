# Shepherd

Shepherd is the team that is in charge of field control.
Shepherd brings together all the data on the game field into one centralized location, where it keeps track of score, processes game-specific actions, keeps track of time, and informs the scoreboard.

## Sections

- [Architecture](#Architecture)
- [Installing Dependencies](#Installing-Dependencies)
- [Running Shepherd](#Running-Shepherd)
- [Testing](./shepherd/tests/TESTING_DOCS.md)

## Architecture

Shepherd is essentially a [Flask](https://palletsprojects.com/p/flask/) web app that communicates with:

- Arduino devices on the field over USB serial.
- Each robot's [Runtime](https://github.com/pioneers/PieCentral/tree/master/runtime) instance using MessagePack remote procedure calls over TCP.
- Each driver station's [Dawn](https://github.com/pioneers/PieCentral/tree/master/dawn) instance.
- Each scoreboard client, which is rendered with jQuery. Typically, there is a scoreboard on each side of the field, a projection for spectators, and a fourth for the field control staff.
- Each perk selection tablet (specific to Sugar Blast).

## Installing dependencies

```bash
pip3 install -r requirements.txt
```

## Architecture

To read about Shepherd in detail, check out the [onboarding readme](https://github.com/pioneers/shepherd-onboarding#about-shepherd). This is where you will find detailed information about what each component of Shepherd does.

## 2021 Instructions

First get the release labelled "working game spring 2021" or grab the core_game_2021 branch. 

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