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
        - dicionary of params names to param objects
            - params should be linked when added
        - uuid
        - type

    - parameter class (sensor)
        - name
        - should_poll flag
        - identifier
        - LCM header (optional)
        - debounce threshold (optional, default to None)
        - value from header method
        - is state change significant method
        - construct LCM message method

    - global sensor state database dictionary
        - sensor instance : [value, debounce time stamp]

- debouncer:
    - debouncer initialized with width w
    - stores last w values
    - if 70% of last w values == current value, bounce.. else debounce
    - write down w -> time delay formula for posterity