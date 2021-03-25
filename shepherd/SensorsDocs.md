- LCM messages -> LowcarMessages
        - parameter from header mapping
        - parameter object
            - parameter name
    - Which Device (arduino)
        - parameter stores its parent device
        - device object
            - uuid (int)
            - type (int)
    - What value
        - parameter object stores a value from header method

- LowcarMessage -> filter -> possibly an LCM message
    1. recognize the device and parameter
        - look for parameter's `name` in device that was used
        - relatively trivial
    2. check condition using previous state
        - parameter object method to determine if state change is significant
           - def 
        - optional debounce state change significance
    3. build and send lcm header
        - target and header saved in parameter object
        - parameter object method builds LCM args from Lowcar data and optionaly previous data
    
- data structures:
    - device class (arduino)
        - list of parameters
            - params should be linked when added
        - uuid
        - type

    - parameter class (sensor)
        - name
        - LCM target (optional)
        - LCM header (optional)
        - value from header method
        - is state change significant method
        - construct LCM message method