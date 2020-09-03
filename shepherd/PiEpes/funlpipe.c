#include "funlpipe.h"
static HANDLE create_pipe(const char* name) {
  HANDLE pipe = INVALID_HANDLE_VALUE;
	char username[UNLEN + 1];
	DWORD unlen = UNLEN + 1;
  if (GetUserNameA(username, &unlen)) {
		char pipe_name[MAX_PATH];
		sprintf(pipe_name, "\\\\.\\pipe\\%s\\%s_pipe", username, name);
		const size_t buffer_size = 1024;
		// create the pipe
		pipe = CreateNamedPipeA(pipe_name,
			PIPE_ACCESS_DUPLEX,
			PIPE_TYPE_MESSAGE | PIPE_READMODE_MESSAGE | PIPE_WAIT,
			PIPE_UNLIMITED_INSTANCES,
			buffer_size,
			buffer_size,
			NMPWAIT_USE_DEFAULT_WAIT,
			NULL);

		if (pipe != INVALID_HANDLE_VALUE) {
			// try to connect to the named pipe
			if (FALSE == ConnectNamedPipe(pipe, NULL)) {
				// fail to connect the pipe
				CloseHandle(pipe);
				pipe = INVALID_HANDLE_VALUE;
			}
		}
	}
	return pipe;
}