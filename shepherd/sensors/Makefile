LIBFLAGS=-pthread -lrt -Wall
DEPENDCIES=dev_handler.c message.c shepherd_util.c shm_wrapper.c

dev_handler: shm_api.c $(DEPENDCIES)
	gcc $(DEPENDCIES) -o dev_handler $(LIBFLAGS)

shm_api.c: shm_api.pyx setup.py shm_wrapper.c shepherd_util.c
	python3 setup.py build_ext -i

clean:
	rm -f ./dev_handler
	rm -rf build/
	rm -f shm_api.c
	rm -f shm_api*.so
