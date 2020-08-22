# Shepherd Testing Utility

The testing utility was designed as an asynchronous dummy that would be able to mock up the communication between a piece of shepherd and the rest. It is designed to make simple responses to LCM messages sent by the piece of shepherd that is being tested, and it can be used to test any number of shepherd pieces together. Since shepherd is not asynchronous in this project, the tester has been more or less hacked into shepherd to be compatible with the LCM changes. This means that rather than running the tester as a separate program, and having it talk to the parts being tested, we now directly call the tester from our program, which we run in testing mode.

Several changes are also made to LCM communication between the tester and the program being tested:

  * Sending an LCM message to the tester will act like a function call to the tester, and this will cause the tester to advance until the next WAIT statement, which will wait for another LCM message. At this point, control will transfer back to the original program.
  * Sending an LCM message from the tester using EMIT will not immediately send the message, but rather it will send all LCM messages one after another once the next WAIT statement has been reached.

## Testing Scripts

The testing utility reads in .shepherd testing scripts and emulates the LCM communication per those script's specifications. These scripts use special syntax, which is covered below.

### READ

The READ statement will mount a listener to the LCM channel that is indicated.

Usage: `READ <LCM target>`

  * this is unimplemented in the tester provided for this project, but it is still good style to include it.

### RUN

The RUN statement allows the scripter to execute python code. A single frame is provided for all python statements in the script, so there are no local variables; everything is global. This is implemented under the hood using the unsafe python exec function, which can cause catastrophic issues if exploited. You have been warned. For the most part however, this should be safe to execute python code.

Usage: `RUN <python code>`

All code executed via the RUN statement must be one-line. In other words, multiple RUN statements are run in sequence, in the same name space, but cannot see each other. That means that multiline constructs, such as a for loop must be modified to fit. For loops can be modified using \n to simulate the multiple lines and using spaces to simulate indents. A better alternative however is to write complex functions in a python file, and then import that module at the beginning of the script.

### PRINT

The PRINT statement will naively print whatever comes after it, doing absolutely no evaluation. This means that the PRINT statement can only write static messages, and there is no way to have a dynamic message.

Usage: `PRINT <message>`

### PRINTP

The PRINTP statement is used to create dynamic messages, and will evaluate a python expression that it is given and write the result to std out.

Usage: `PRINTP <python expression>`

### IF

The IF statement accepts a python conditional expression, which it evaluates. All normal python rules apply. The code following the IF statement will be executed only if the expression evaluates to True in python. The IF statement must be closed using and END statement.

USAGE:

`IF <python conditional expression>`

`<script to be run if true>`

`END`

### WHILE

The WHILE statement follows all the same rules as the IF statement, however it will run the code block after iteratively, so long as the condition trailing the WHILE is true. The condition will be re-evaluated each time the script execution passes back over the WHILE statement.

USAGE:

`WHILE <python conditional expression>`

`<script to be run while true>`

`END`

### END

The END statement is used to close the code blocks after the IF and WHILE statements. An imbalanced number of END statements will lead to undefined behavior and to errors being thrown.

Usage: `END`

### PASS

The PASS statement will terminate the test script with a positive reply. Optionally, a python conditional expression can be added, which if false, will cause the code execution to ignore the PASS statement, and continue as normal.

Usage: `PASS <optional python conditional expression>`

### FAIL

The FAIL statement will terminate the test script with a failing reply. Optionally, a python conditional expression can be added, which if false, will cause the code execution to ignore the FAIL statement, and continue as normal.

Usage: `FAIL <optional python conditional expression>`

### ASSERT

The ASSERT statement is intended for use at the end of a script, and requires a python conditional expression. If that expression evaluates to true, the program will exit with a positive result, and if it evaluates to false the script will exit with a failing result.

Usage: `ASSERT <python conditional expression>`

### WAIT

The WAIT statement is used to pause code execution until a specific LCM message is received by the testing script. A WAIT statement consists of the following pieces:

  * A LCM header must follow the WAIT statement, this is the header that will be waited on.

  * FROM

  * A LCM target must follow the header, separated by the keyword FROM. This is the LCM channel that the WAIT statement will listen to for the specified header.

  * WITH can then be specified, to store arguments from the header into the namespace. This must follow the header specified by FROM. The WITH statement looks something like this, `WITH argument = 'argument in header'`. The name of the argument in the header must be surrounded by single quotes. If the argument is not present in the header, an error will be thrown.

  * SET can then be specified, which will execute a line of python code when the header is received. The SET statement looks something like this, `SET test = True`.

  * Any number or WITH and SET statements can follow the FROM statement, and they may be arranged in any order (WITH does not need to come first). Likewise, there are no guarantees about the order that the WITH and SET statements will be executed in, so they should not rely on the execution of one another.

  * AND and OR can be used to chain multiple headers into one WAIT statement. This will cause the WAIT statement to wait until multiple headers have been received. AND and OR statements will be evaluated from left to right, and as soon as conditions allow for the execution to continue, it will. The OR statement is satisfied as soon as one of the headers on either side of it have been received, and the AND statement will be satisfied once both headers have been received. Adjacent AND and OR statements in the same WAIT statement will wait on each other, so `1 AND 2 AND 3` would wait for all 3 headers to be received, while `1 OR 2 AND 3 OR 4` would proceed once either 1 , 4, or both 2 and 3 had been received.

Usage: `WITH <header> FROM <target> WHERE <assignment>... SET <python expression>... AND <header> FROM <target>... OR...`

### EMIT

The EMIT statement will send an LCM message from the script to a target. The EMIT statement is significantly simpler than the WAIT statement, and it's structure is as follows:

  * A LCM header must follow the EMIT statement, this is the header that will be sent.

  * TO

  * A LCM target must follow the header, separated by the keyword TO. This is the LCM channel that the EMIT statement send specified header to.

  * WITH can then be specified to set the arguments into the header from the namespace. This must follow the header specified by TO. The WITH statement looks something like this, `WITH 'argument in header' = argument`. The name of the argument in the header must be surrounded by single quotes. It is worth noting that this is the reverse of the WITH statement used in WAIT.

  * Multiple WITH statements may be specified in order to set multiple arguments in the header. The order of these statements is undefined.

Usage: `EMIT <header> TO <target> WHERE <assignment>...`
