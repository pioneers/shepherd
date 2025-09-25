# Google Sheet Authorization



## Preliminary

* You DO HAVE `client_secret.json` handy
* You DO NOT HAVE `user_token.json`; if you happen to be with it, then exit this tutorial - you're good to go!


## Authorization

* On your command line, execute

### Anywhere
```
python3 -m ydl
```

### Shepherd/src
```
python3 sheet.py
```

* A webpage should pop up, follow the instructions - login to Google; grant `PiE 2018 Spreadsheet` access; done.

## Verification

* On your command line, execute

### Shepherd/src
```
python3 sheet.py
```

* Then you should see the following

```
Success.
```
