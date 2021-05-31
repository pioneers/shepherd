<img align="right" src="https://github.com/pioneers/shepherd/blob/testing-framework/shepherd/readmefigures/PiE%20Sheep.png" alt="PiE Sheep" width="86" height="135">

# Shepherd Testing Utility

## Sections

- [Intro](#Intro)
- [Commands](#Commands)
- [Test Structure](#Test-Structure)
- [Running Tests](#Running-Tests)
- [Future Modifications](#Future-Modifications)

## Intro

The testing utility was designed as an asynchronous dummy that would be able to mock up the communication between a piece of shepherd and the rest. It is designed to make simple responses to LCM messages sent by the piece of shepherd that is being tested, and it can be used to test any number of shepherd pieces together. Unfortunately, the shepherd testing utility requires LCM to communicate with other parts of shepherd, so a computer without LCM will not be able to run it.

The testing utility communicates via LCM targets, and there are a few important things to be aware of while using the utility. All LCM targets and headers must be included in Utils.py, otherwise the utility will not recognize them. In addition, Utils.py is not imported into the internal environment for python execution that the tester provides. LCM headers and targets will be looked up in Utils.py when they appear in a non-python context, but otherwise they would need to be imported via a RUN statement. Due to underlying limitations, we can only read from one target at a time, so each READ statement will override any previous READ statements, and change our LCM target. Furthermore, we cannot wait on a header from a target before we read from that target, so READ should probably be the first line of your script.

While the error recognition and reporting in this utility is helpful, it is not exhaustive. Some disallowed behavior in the following command may not result in a runtime exception, and instead have unexpected and undefined consequences. Adhering to the syntax provided below is the best way to make sure your script works.

It is possible to run multiple .shepherd scripts at once, and have them communicate, however having multiple scripts read from the same LCM target is currently untested and may result in undefined behavior. Also keep in mind that there is no synchronization or timing command in this utility yet, however the RUN command may be used in combination with python timing and synchronization to create the same effect.

## Commands

The testing utility reads in .shepherd testing scripts and emulates the LCM communication per those script's specifications. These scripts use special syntax, which is covered below.

### Comments

Comments can be added to .shepherd by starting a line with `##`. This will cause the line to be skipped during execution. Comments cannot start mid line.

Usage: `## <comment>`

### READ

The READ statement will mount a listener to the LCM channel that is indicated.

Typically, this is put at the top of a test file but it is possible to have multiple READ statements in a test. Subsequent READ statements will cause the LCM queue to clear.

Usage: `READ <LCM target>`

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

### SLEEP

The SLEEP statement is used in order to pause the execution of the .shepherd interpreter for a specified amount of time. Any LCM messages received while the interpreter is paused will still be recorded and may be processed by the next WAIT statement that the interpreter encounters. The sleep time may be a decimal, and is in terms of seconds. SLEEP may take a python expression as an argument, so long as it evaluates to a float.

Usage: `SLEEP <time / python expression>`

### DISCARD

The DISCARD statement clears the LCM / YDL of any messages that have been received so far, but have not been processed, ensuring that they will not be processed. This is helpful after a SLEEP statement, to ensure that any messages that were received during the sleep would be ignored, if that is the desired functionality.

Usage: `DISCARD`

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

- A LCM header must follow the WAIT statement, this is the header that will be waited on.

- FROM

- A LCM target must follow the header, separated by the keyword FROM. This is the LCM channel that the WAIT statement will listen to for the specified header.

- WITH can then be specified, to store arguments from the header into the namespace. This must follow the target specified by FROM. The WITH statement looks something like this, `WITH argument = 'argument in header'`. The name of the argument in the header must be surrounded by single quotes. If the argument is not present in the header, an error will be thrown.

- WITH INFER is a special kind of WITH statement which instructs the testing script to place all of the data found in the LCM message into the namespace with the variable name inferred as the name of the key in the data dictionary from the header. Any key in the data dictionary that is used in another WITH statement will not be inferred, and therefore will not be copied into the namespace a second time. The WITH INFER statement does not need to go in any particular place and will look both ahead and behind when calculating what statements to infer. This means it can go anywhere a normal WITH statement can go. It is important to note that any header keys that are inferred that are not valid python variable names, or that begin with an underscore will cause an error. Therefore you must explicitly name and store any such key values in their own WITH statements in order to give them valid names and cause WITH INFER to skip over them.

- SET can then be specified, which will execute a line of python code when the header is received. The SET statement looks something like this, `SET test = True`.

- Any number or WITH and SET statements can follow the FROM statement, and they may be arranged in any order (WITH does not need to come first). Likewise, there are no guarantees about the order that the WITH and SET statements will be executed in, so they should not rely on the execution of one another.

- AND and OR can be used to chain multiple headers into one WAIT statement. This will cause the WAIT statement to wait until multiple headers have been received. AND and OR statements will be evaluated from left to right, and as soon as conditions allow for the execution to continue, it will. The OR statement is satisfied as soon as one of the headers on either side of it have been received, and the AND statement will be satisfied once both headers have been received. Adjacent AND and OR statements in the same WAIT statement will wait on each other, so `1 AND 2 AND 3` would wait for all 3 headers to be received, while `1 OR 2 AND 3 OR 4` would proceed once either 1 , 4, or both 2 and 3 had been received.

  - All headers in a WAIT statement that are chained together are considered together. This means that if a WAIT statement is waiting on the same header twice, when that header arrives both places it is referenced will be evaluated. Additionally, this means that if a header has already been satisfied but execution is blocked by another unsatisfied header chained together, and the header is received a second time, the header will be evaluated again using the new data.

  - WAIT statements will only apply changes to the environment as soon as a header is received, however since execution cannot continue until all chained headers are satisfied, all changes effectively are applied after the WAIT statement, using the most recent version of each header.

Usage: `WAIT <header> FROM <target> WITH <assignment>... SET <python expression>... AND <header> FROM <target>... OR...`

### EMIT

The EMIT statement will send an LCM message from the script to a target. The EMIT statement is significantly simpler than the WAIT statement, and it's structure is as follows:

- A LCM header must follow the EMIT statement, this is the header that will be sent.

- TO

  - A LCM target must follow the header, separated by the keyword TO. This is the LCM channel that the EMIT statement send specified header to.

- WITH can then be specified to set the arguments into the header from the namespace. This must follow the header specified by TO. The WITH statement looks something like this, `WITH 'argument in header' = argument`. The name of the argument in the header must be surrounded by single quotes. It is worth noting that this is the reverse of the WITH statement used in WAIT.

- Multiple WITH statements may be specified in order to set multiple arguments in the header. The order of these statements is undefined.

Usage: `EMIT <header> TO <target> WITH <assignment>...`

## Test Structure

Each test will be contained in a folder which consists of a number of files, representing different parts of Shepherd that are being run.

For example, the [example](./example) test contains an example_client.shepherd and an example.shepherd which interact with each other through EMIT and WAIT commands.

Each test will also contain an instructions.shepherd file (see [example](./example/instructions.shepherd)) which has a list of the order in which to run the test files. This is important when one target needs to be WAITing before another test EMITs to it.

## Running Tests

To run all the tests, run

```
python3 testing_script.py
```

To run a specific test folder, run

```
python3 testing_script.py example
```

where example is the name of the test folder. You can include as many tests as you want separated by spaces.

To run an individual test file, run

```
python3 Tester.py example/example_client.shepherd
```

where example/example_client.shepherd is the path to a test inside the tests folder. When there are multiple test files to run, you can run each of them in a different terminal tab. This method might be more helpful when debugging test results.

## Future modifications:

The testing utility right now is functional, but flawed. The most precarious systems are the syntax error recognition, the execution of IF and WHILE statements, and the LCM interactions. There are also quite a few features that the framework might benefit from.

### Modifications:

- Syntax for the testing utility is currently hard coded into each of the processing functions. A more robust solution would be to introduce a tokenizer and parser using regular expressions and a grammar such as CUP or BISON to ensure that the syntax makes sense. Unfortunately some of the more specific error messages in the current implementation would become generic, however all syntax errors would be caught.

- The IF and WHILE statements would also see more reliable functionality from the previous strategy. The grammar would allow IF and WHILE to be packaged with their corresponding END statements, and this would make execution faster and more robust. Furthermore, unbalanced END statements would be detected when the file was read in, and not at runtime (how they currently are) making debugging a script much simpler.

- LCM is ultimately too niche (hard to install) and overly complicated for Shepherd's needs, however until a better alternative is found (or coded), the best solution to the LCM issues is to modify the interaction with queues used in the start loop of the tester. Having a dynamic way to reassign LCM targets, or potentially to even read from multiple would make the scripting much more intuitive.

### Additions:

- Adding an optional (but highly recommended) timeout to the WAIT statements would make detecting a failed test via travis much simpler. Right now, a timeout may be applied to the entire test, however this feels sloppy and makes it harder to have intentional delays in a test. WAIT statement specific timeouts would increase the flexibility of the testing framework, especially when automated testing is involved, and would provide clearer feedback about what timed out.

- Adding a succinct method of delaying the script execution from line to line would allow time sensitive scripts to be very easy to create. something like leading a line with `#200` for a delay of 200ms would be easy to write and opens up lots of options for shepherd script.

- Adding functionality for the testing framework to interact with COM ports and socketio connections would allow a far greater number of things to be tested by the scripts. This would allow the testing framework to simulate interactions with sensors on the field, or inputs from one of the UI elements, so that the servers can be tested.
