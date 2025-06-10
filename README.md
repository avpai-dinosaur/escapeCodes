# EscapeCodes

<div align="center"> 
 <img src="assets/images/logo.png" alt="EscapeCodes logo" width="500"/>
</div>

A story-based video game which helps aspiring software engineers study for technical interviews.

## Controls
 - WASD to move
 - Q to zoom camera in
 - E to zoom camera out
 - P to punch
 - SPACEBAR to dash
 - ESC to close ui elements

## Run through interpreter

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
python3 -m src.main
```

## Build standalone executable

We use pyinstaller to create the bundle

For Linux and MacOs
```
pyinstaller --add-data "assets:assets" src/main.py
```

For Windows
```
pyinstaller --add-data "assets;assets" src\main.py
```

Then run with
```
dist/main/main
```

## Run unit tests

```
python3 -m unittest tests
```