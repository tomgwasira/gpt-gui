# Graphical User Interface Implementation for General Power Theory

## Development
### Install PyQt5
```
sudo apt-get install python3-pyqt5
```

Warning: PyQt does not play well with virtual environments especially on the Raspberry Pi.

### Install Qt Designer
```
sudo apt-get install qttools5-dev-tools
sudo apt-get install qttools5-dev
```

### Install PyQtGraph
```
pip3 install pyqtgraph
```

## Packaging with PyInstaller

### Install PyInstaller

```
pip3 install pyinstaller
```

### Compile

```
python3 -m PyInstaller script.py -F --i icon.png -noconsole

## About the Project
Qt is overall superior to Gtk in terms of flexibility. It allows much more control over style, font sizes etc. Group boxes etc. are so powerful, using Gtk is caveman vibes.
```

## Contributing to Project

### Programming Style

The programming style is largely influenced by PyQt5.
