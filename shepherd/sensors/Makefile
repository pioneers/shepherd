LIBFLAGS=-lrt -pthread -Wall # add -lrt to the front of this for linux, but not mac
DEPENDENCIES=message.c shepherd_util.c shm_wrapper.c ../logger/logger.c 
FILES=shepherd_util.c shm_wrapper.c ../logger/logger.c
all: dev_handler shm_api shm_start shm_stop

dev_handler: dev_handler.c $(DEPENDENCIES)
	gcc $^ -o dev_handler $(LIBFLAGS)

shm_api: shm_api.pyx setup.py shm_wrapper.c shepherd_util.c
	python3 setup.py build_ext -i

shm_start: shm_start.c $(FILES)
	gcc $^ -o $@ $(LIBFLAGS)

shm_stop: shm_stop.c $(FILES)
	gcc $^ -o $@ $(LIBFLAGS)

clean:
	rm -f ./dev_handler
	rm -rf build/
	rm -f shm_api.c
	rm -f shm_api*.so
