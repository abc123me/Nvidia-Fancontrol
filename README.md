# Nividia-Fancontrol
It's a script that controls the fan on a nvidia graphics card

## Progress
Currently it is in its very early stages but still usable
(I'm working on making it better)
### TODO
- Rewrite in C++ (in progress)
- Test it on more cards, I have a GTX 760 and 1060 I can use but would hope to have some users tell me what they're using.
- Make a daemon or some automatic-startup script which would run quiet (non verbose)
- Java GUI for controlling said daemon aswell as nice fan speed over time plotting using my graphing library

## Usage
- `python3 main.py` No special privledges required!
- `python3 main.py -v` Same as before but launches it in verbose mode
### Modifications
You can modify main.py to make a custom fan curve, or use a different GPU/Fan.

## Tested configurations
- Ubuntu with GTX760 and GTX1060 6GB (No problems)
- LXDE with GTX1060 6GB (No problems)
- Everything else is untested (however it will probably work)

# Documentation
Refer to [nvfan.py](https://github.com/abc123me/Nividia-Fancontrol/blob/master/nvfan.py)

# Contributors
[mstrobl2](https://github.com/mstrobl2) Fixed a bug in version checking, better defaults
