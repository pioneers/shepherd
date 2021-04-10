# Running Shepherd with docker

## Installing Docker

Windows: install Docker Desktop
Mac: install Docker Desktop
Linux: install Docker for Linux

Linux users may need to add `sudo` to all Docker commands.

## Building the Image

First, `cd dockerfiles` (the folder with the Dockerfile). This is where Docker will grab the necessary config files from.

Then run `docker build -t shepherd:latest .` (if you get an error that it takes one argument, you need to include the last `.`). This will build an image using the current directory's files, with the name "shepherd:latest".

This process may take up to 5-10 minutes. After it completes, you can optionally run `docker images` to see the image you just built (or you can see it in the GUI on Docker Desktop).

## Creating the Container

This only requires one command, but it's a long one:
```
docker run -it -v '/absolute/path/to/shepherd':/outsideshep -p=5000:5000 -p=5500:5500 --name=sheep shepherdtest:latest
```

A breakdown of what this means:
 - `docker run`: this will create the container, and run it
 - `it`: it will run it interactively, so you will be popped into a bash terminal when the container starts
 - `-v '/absolute/path/to/shepherd':/outsideshep`: this will link the shepherd repo on your computer, to a folder named "outsideshep" inside the container. Both must be absolute paths.
 - `-p=5000:5000 -p=5500:5500`: this will link the container's ports to your computer's ports, so you can run the python server inside the container and reach it from your computer's web browser.
 - `--name=sheep`: this names the container "sheep". Otherwise, Docker would give it a random name.
 - `shepherdtest:latest`: this is the name of the image that the container will be created off of.
 
If you are successful, it should pop you into a root shell, and `ls outsideshep` should list the files in your Shepherd repo. If this is the case, exit the shell (you can run the command `exit`), and procceed to the next section.

If you are unsuccessful, run `docker rm sheep` to destroy the bad container, and then try again.

## Running Shepherd inside the container

Run `docker ps -a`. You should see the `sheep` container, and the status should be `exited`.

Run the following:
```
docker restart sheep # starts the container
docker exec -it sheep bash # starts a bash terminal inside the container
    # at this point you should be inside the container
cd outsideshep/shepherd
python3 Shepherd.py
```

And then in a seperate terminal window:

```
docker exec -it sheep bash
    # at this point you should be inside the container
cd outsideshep/shepherd
python3 Shepherd.py
```

Now, you should be able to navigate to <http://localhost:5000/staff_gui.html> and see the staff gui running. If so, congrats! You have successfully set up and run Shepherd in a Docker container.

When you are done, exit both terminals, and then run
```
docker stop sheep
```
If you do not do this step, the container will continue running 24/7, which is a little inefficient. 


