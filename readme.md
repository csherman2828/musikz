# Musikz 2.0

The updated Musikz 2.0 will leverage the most recent version of packages and
support my creative liberties in rearchitecting the components of `MusicCog`.

Musikz is powered by:
- [`discord.py`][1] - for Discord bot support
- [`youtube_dl`][2] - for YouTube music support

## Setup

First, make sure you have Python 3.8 installed. The [`discord.py`][1] library
we'll be using requires more recent updates found in Python >=3.8. We'll also be
using `python3.8-venv`.

```
## Install python3.8 a if you do not have it
$ sudo apt update
$ sudo apt install python3.8 python3.8-venv
```

For more info on installing Python 3.8, see [this article][3]

Once that's done, make sure you've cloned this repository and entered the
directory with this repository in your shell.

Then, we'll want to set up the virtual environment for this project. This
will keep our Python libraries localized to this project.

```
# Set up virtual environment using 'venv' in a directory called '.venv/'
$ python3.8 -m venv ./.venv

# Activate the virtual environment
$ source ./.venv/bin/activate

# Once activated, you can deactivate easily
$ deactivate
```

Next, with the `venv` activated, we'll need to make sure `pip` is up to date.

```
# Update pip
$ python3.8 -m pip install --upgrade pip
```

Finally, we can install the dependencies according to the `requirements.txt` 
file.

```
# Install dependencies from 'requirements.txt'
$ python3.8 -m pip install -r requirements.txt
```

Finally, you will need to set up your bot's token that you can get from the
Discord Developer Portal. Create a `config.json` in the root repository
directory according to the format specified in `config-example.json`.

Finally, you should be good to go to run the bot!

```
$ python3.8 main.py
```

[1]: https://pypi.org/project/discord.py/
[2]: https://pypi.org/project/youtube_dl/
[3]: https://linuxize.com/post/how-to-install-python-3-8-on-ubuntu-18-04/