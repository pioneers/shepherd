from libc.stdint cimport *
from cpython.mem cimport PyMem_Malloc, PyMem_Free

cdef extern from "shepherd_util.h":
    int MAX_DEVICES
    int MAX_PARAMS
    ctypedef enum process_t:
        EXECUTOR
    ctypedef struct device_t:
        char* name
        uint8_t type
        uint8_t num_params
        param_desc_t* params
    ctypedef union param_val_t:
        int32_t p_i
        float p_f
        uint8_t p_b
    ctypedef enum param_type_t:
        INT, FLOAT, BOOL
    ctypedef struct param_desc_t:
        char* name
        param_type_t type
        uint8_t read
        uint8_t write
    device_t* get_device(uint8_t dev_type)

cdef extern from "shm_wrapper.h" nogil:
    ctypedef enum stream_t:
        DATA, COMMAND
    void shm_connect()
    int device_read_uid(uint64_t device_uid, process_t process, stream_t stream, uint32_t params_to_read, param_val_t *params)
    int device_write_uid(uint64_t device_uid, process_t process, stream_t stream, uint32_t params_to_write, param_val_t *params)
    int place_sub_request (uint64_t dev_uid, process_t process, uint32_t params_to_sub)


## Functions needed by Shepherd

class DeviceError(Exception):
    """An exception caused by using an invalid device. """


cpdef get_value(str device_id, str param_name):
    """ 
    Get a device value. 
    
    Args:
        device_id: string of the format '{device_type}_{device_uid}' where device_type is LowCar device ID and device_uid is 64-bit UID assigned by LowCar.
        param_name: Name of param to get.
    """
    # Convert Python string to C string
    cdef bytes param = param_name.encode('utf-8')

    # Getting device identification info
    splits = device_id.split('_')
    if len(splits) != 2:
        raise ValueError(f"First argument device_id must be of the form <device_type>_<device_uid>")
    cdef int device_type = int(splits[0])
    cdef uint64_t device_uid = int(splits[1])
    
    # Getting parameter info from the name
    cdef device_t* device = get_device(device_type)
    if not device:
        raise DeviceError(f"Device with uid {device_uid} has invalid type {device_type}")
    cdef param_type_t param_type
    cdef int8_t param_idx = -1
    for i in range(device.num_params):
        if device.params[i].name == param:
            param_idx = i
            param_type = device.params[i].type
            break
    if param_idx == -1:
        raise DeviceError(f"Invalid device parameter {param_name} for device type {device.name.decode('utf-8')}({device_type})")

    # Allocate memory for parameter
    cdef param_val_t* param_value = <param_val_t*> PyMem_Malloc(sizeof(param_val_t) * MAX_PARAMS)
    if not param_value:
        raise MemoryError("Could not allocate memory to get device value.")

    # Read and return parameter
    cdef int err = device_read_uid(device_uid, EXECUTOR, DATA, 1 << param_idx, param_value)
    if err == -1:
        PyMem_Free(param_value)
        raise DeviceError(f"Device with type {device.name.decode('utf-8')}({device_type}) and uid {device_uid} isn't connected to the robot")

    if param_type == INT:
        ret = param_value[param_idx].p_i
    elif param_type == FLOAT:
        ret = param_value[param_idx].p_f
    elif param_type == BOOL:
        ret = bool(param_value[param_idx].p_b)
    PyMem_Free(param_value)
    return ret


cpdef void set_value(str device_id, str param_name, value) except *:
    """ 
    Set a device parameter.
    
    Args:
        device_id: string of the format '{device_type}_{device_uid}' where device_type is LowCar device ID and device_uid is 64-bit UID assigned by LowCar.
        param_name: Name of param to get.
        value: Value to set for the param.
    """
    # Convert Python string to C string
    cdef bytes param = param_name.encode('utf-8')

    # Get device identification info
    splits = device_id.split('_')
    if len(splits) != 2:
        raise ValueError(f"First argument device_id must be of the form <device_type>_<device_uid>")
    cdef int device_type = int(splits[0])
    cdef uint64_t device_uid = int(splits[1])

    # Getting parameter info from the name
    cdef device_t* device = get_device(device_type)
    if not device:
        raise DeviceError(f"Device with uid {device_uid} has invalid type {device_type}")
    cdef param_type_t param_type
    cdef int8_t param_idx = -1

    for i in range(device.num_params):
        if device.params[i].name == param:
            param_idx = i
            param_type = device.params[i].type
            break

    if param_idx == -1:
        raise DeviceError(f"Invalid device parameter {param_name} for device type {device.name.decode('utf-8')}({device_type})")

    # Allocating memory for parameter to write
    cdef param_val_t* param_value = <param_val_t*> PyMem_Malloc(sizeof(param_val_t) * MAX_PARAMS)
    if not param_value:
        raise MemoryError("Could not allocate memory to get device value.")

    if param_type == INT:
        param_value[param_idx].p_i = value
    elif param_type == FLOAT:
        param_value[param_idx].p_f = value
    elif param_type == BOOL:
        param_value[param_idx].p_b = int(value)
    cdef int err = device_write_uid(device_uid, EXECUTOR, COMMAND, 1 << param_idx, param_value)
    PyMem_Free(param_value)
    if err == -1:
        raise DeviceError(f"Device with type {device.name.decode('utf-8')}({device_type}) and uid {device_uid} isn't connected to the robot")

cpdef void dev_handler_connect() except *:
    shm_connect()