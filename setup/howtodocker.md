# Running Shepherd with Docker

## Installing Docker

 - Windows: install Docker Desktop
 - Mac: install Docker Desktop
 - Linux: install Docker for Linux. Linux users may need to add `sudo` to all Docker commands (including `make-container`).

## Setting up the Docker Container

If you don't have it already, `git clone` the shepherd repo. From within the setup folder in the repo, run these commands:
```
docker pull pierobotics/shepherd
./make-container
```
If the second command is successful, it should pop you into a root shell. Feel free to look around; when you're done, exit the container (you can run the command `exit`).

Now, add this line to your `~/.bashrc` file (or `~/.zshrc` or `~/.bash_profile`):
```
alias whale="docker exec -it sheep run"
```
After adding the line, close and reopen your terminal, or run `source ~/.bashrc` (or equivalent).

## Running Shepherd

Split your terminal window (or open two). In terminal 1, run
```
docker restart sheep
whale Shepherd.py
```
In terminal 2, run
```
whale server.py
```

Now, you should be able to navigate to <http://localhost:5000/staff_gui.html> and see the staff gui running. If so, congrats! You have successfully set up and run Shepherd in a Docker container. 

When you are done, run
```
docker stop sheep
```
If you do not do this step, the container will continue running 24/7, which is a little inefficient. 

## Going inside the Docker container

You may want to run things directly in the Docker container (for example, for literally anything that isn't a Python script). The commands are similar:
```
docker restart sheep
docker attach sheep

# do things

docker stop sheep
```
Alternatively, you can do `docker exec -it sheep bash` if you want multiple terminals. 


## Optional Advanced Stuff

Some commands you might find useful:
 - `docker ps -a` shows a list of all containers. Shut down running containers if you aren't using them!
 - `docker images` shows a list of all images
 - `docker rm sheep` deletes the sheep container. You can recreate it with `./make-container`.
 - `docker rmi pierobotics/shepherd` deletes the pierobotics/shepherd image. You can get it back with `docker pull pierobotics/shepherd`/
 - `docker stop sheep` shuts down the sheep container
 - `docker restart sheep` starts the sheep container
 
If you ever want to build the image (you updated requirements.txt or something), `cd` into the dockerfiles folder and run `docker build -t pierobotics/shepherd:latest .` (if you get an error that it takes one argument, you need to include the last `.`). This will build an image using the current directory's files, with the name "shepherd:latest". Then, push it to Dockerhub so that everyone can use your changes.

Building the image typically takes around 5 minutes.

Note that if you want to use ports that aren't 5000 or 5500, you'll have to add those ports to the `./make-container` script. Similarly, if you want to run files outside the innermost shepherd folder, you'll have to edit the `dockerfiles/run-python-scripts` file and `whale` alias accordingly.


