#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdio.h>
#include <stdlib.h>
#include <windows.h>
#include <conio.h>
#include <tchar.h>
#include <semaphore.h>

struct PipeHeader {
  LPCTSTR first;
  LPCTSTR last;
} pipeHeader;
