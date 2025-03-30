# Run through interpreter

First activate your python virtual environment

```
source env/bin/activate
```

If you don't have a virtual environment create one with

```
python3 -m venv env
```

Install dependencies (make sure your virtual environment is activated!)

```
pip install -r requirements.txt
```

Run with

```
python3 src/main.py
```

# Build executable

We use pyinstaller to create the bundle

```
pyinstaller --add-data "assets:assets" src/main.py
```

Then run with

```
dist/main/main
```

# Run unit tests

```
python3 -m unittest tests
```

# Todo in rough order of importance

- Connect to leetcode account and detect that a question was solved
- add unit tests
- Boss fight
- Camera motions at start of level
- Make clickable elements change color when clicked (plus cursor image changes)

- Add a mental health notes (new feature)
- Make dance floor lights look nicer
- Add type annotations
- Consolidate some sprite behaviors into a base class
- Consolidate some menu UI behavior into a base controls class
- Figure out why music isn't working
- don't initialize every single level at once
