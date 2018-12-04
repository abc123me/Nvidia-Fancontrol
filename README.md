# Nvidia-Fancontrol
It's a script that controls the fan on a nvidia graphics card

## Progress
Currently it is in its very early stages but still usable
(I'm working on making it better)
### TODO
- Rewrite in C/C++ (in progress)
  - I already have a nice Thinkpad fan control program that I want it to be merged with
  - I think python is stupid, and I don't like using it for big projects due to its messiness
  - C++, C, and Assembly are for fan control scripts - not python
- Make a daemon or some automatic-startup script which would run quiet (non verbose)
- Java GUI for controlling said daemon aswell as nice fan speed over time plotting using my graphing library

## Usage
- `python3 main.py` No special privledges required!
- `python3 main.py -v` Same as before but launches it in verbose mode
### Modifications
You can modify main.py to make a custom fan curve, or use a different GPU/Fan.<br>
But please don't commit these changes, because the fan curve is already decent!

## Tested configurations
- Ubuntu with GTX760 and GTX1060 6GB (No problems)
- LXDE with GTX1060 6GB (No problems)
- Everything else is untested (however it will probably work)

# Documentation
Refer to [nvfan.py](https://github.com/abc123me/Nividia-Fancontrol/blob/master/nvfan.py)

# Contributors
[mstrobl2](https://github.com/mstrobl2) Fixed a bug in version checking, better defaults
