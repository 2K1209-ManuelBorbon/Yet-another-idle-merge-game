# Yet-another-idle-merge-game

A physics-based merge game where cows bounce around a box and merge
into higher tiers when they collide.

## Run

    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    python main.py

## Folder structure
MA4_HT26/
├── .gitignore
├── requirements.txt
├── README.md
├── main.py                # entry point — the game loop
├── cow.py                 # Cow class + merge/collision logic
├── ui.py                  # Button and TextField classes
└── assets/                # Sprites/sounds