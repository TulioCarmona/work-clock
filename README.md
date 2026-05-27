# Work Clock

A floating desktop widget that tracks your daily work progress.

## Requirements

- Python 3.9 or newer (must be installed on the system)
- Internet connection for the **first-time setup only**

## First-time setup

Run this once to download the required packages into the `libs/` folder:

```bash
cd "work clock"
python setup.py
```

This installs `PyQt6` and `Pillow` locally inside the project — nothing is added to your system Python.
If you already have `PyQt6` and `Pillow` installed on your system, skip this step.

## Running the app

```bash
cd "work clock"
python run.py
```

After setup, the app runs fully offline and portably. You can copy the whole folder to any machine that has Python, and it will work without any extra installation steps.

## Personalization

It is possible to tweak the appearance of the widget, the settings menu allows the user to perform the following modifications: 

- Change between `dark` and `light` theme.
- Change the transparency of the background of the widget so it is easy to read, depending on the content of your screen.
- Choose different fonts for the clock and greetings from the ones already included, or download a different font `.ttf` file and move it to the `fonts` directory. The widget will automatically load the fonts the next time it is open, and the new font will appear in the settings menu. 

## Folder structure

```
work clock/
├── WC_App.py       ← main application
├── run.py          ← portable launcher (use this to start)
├── setup.py        ← one-time package installer
├── config.json     ← saved settings (auto-updated)
├── icons/          ← bundled icon assets
└── libs/           ← bundled packages (created by setup.py)
```
