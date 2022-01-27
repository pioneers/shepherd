# Shepherd

Shepherd is the team that is in charge of field control. 
Shepherd brings together all the data on the game field into one centralized location, where it keeps track of score, processes game-specific actions, keeps track of time, and informs the scoreboard.


## Running Shepherd 

### Installing Shepherd

If you don't have Python and/or a terminal, you will need to install it. Refer to the instructions in https://inst.eecs.berkeley.edu/~cs61a/fa20/lab/lab00/#install-a-terminal for installing a terminal and Python.

Next, you will need to clone the repo. Make a folder named `pie` or something on your computer, then in that folder, run the following:
```
git clone https://github.com/pioneers/shepherd.git
cd shepherd
```
At this point, your terminal should be a folder named `pie/shepherd` (or similar). Now it is time to install dependancies. Run:
```
python3 -m pip install --upgrade -r requirements.txt
```
(or `pip3 install --upgrade -r requirements.txt` if that doesn't work). At this point you are ready to run Shepherd.

### Quickstart

Open 3 seperate terminal windows, and use `cd` to navigate them all to `pie/shepherd/shepherd`. Then in terminal 1, run `python3 server.py`. In terminal 2, run `python3 ydl.py`. In terminal 3, run `python3 shepherd.py`. If this is successful, you should be able to go to any of the urls listed in terminal 1's output, and see a webpage displayed. If so, congrats! You have successfully run Shepherd.



## Game Instructions

To run a full game, you can install tmux, connect the Arduinos to your computer (after flashing), and then run the provided tmux script (in `pie/shepherd`):
```
./shepherd_tmux.sh
```
If you prefer, you can run the game manually instead. First, follow the quickstart instructions, then follow the following sensors instructions.

## Running Sensors

For talking to sensors, we use a Shepherd specific version of `dev_handler`, which stands for device handler, and the Lowcar Framework which were written by Runtime. First, connect the Arduinos to your computer (they should have already been flashed).

Run the following:

```
cd shepherd/sensors
make clean && make
./dev_handler
```
Then, in another terminal, run the Shepherd code that interfaces with dev handler in another terminal.
```
cd shepherd
python3 sensors.py
```

## Architecture

To read about Shepherd in detail, check out the [onboarding readme](https://github.com/pioneers/shepherd-onboarding#about-shepherd). This is where you will find detailed information about what each component of Shepherd does.




