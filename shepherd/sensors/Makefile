LIBFLAGS=-pthread -lrt -Wall

dev_handler: dev_handler.c message.c shepherd_util.c shm_wrapper.c
	gcc $^ -o dev_handler $(LIBFLAGS)

clean:
	rm -f ./dev_handler
    