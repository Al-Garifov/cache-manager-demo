## Install
Inside of repo root: ```pip install --target ./scripts/python/site-packages/ lucidity```

Then copy folders `toolbar` and `scripts` to your `~/Documents/houdini{version}` folder.

Relaunch Houdini and look for a shelf called **"Breakdown"**.

## Test
Inside of repo root: ```pytest -v -s```

Check code style quality with ```pip install pylint``` and then ```pylint ./scripts/python/```

## Known issues
Could be found via FIXME and TODO tags in the sources.

# Warning!
Critical bug related to Houdini API described in `scripts/python/main.py`!
