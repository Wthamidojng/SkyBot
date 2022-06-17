SkyBot
======

The SkyClan Discord Bot, now fully free and open source.

Features
--------

### Stars
Stars are just pins but from the bot.

### Economy
Levels are given to users after a certain amount of messages, and they are able to gain **SkyBucks**

### Music
Support for voice channels and music input is provided via PyNaCl and youtube-dl. Spotify and YouTube are supported, with experimental Soundcloud support.

### Games
There are games in this bot as there are games in any other Discord bot in the modern era. This has not been yet integrated with the economic system of the code.

### Reddit
It can load stuff from Reddit.

### Counting
SkyBot can automatically count in counting channels.

### Administration
So far, we have basic admin commands and procedures such as `purge`, `bannedwords`, etc.

Installation
------------
**It is recommended you create a virtual environment to house this bot.**

### Required Modules
* asqlite: `pip install git+https://github.com/Rapptz/asqlite`
* attrs
* certifi
* cffi
* discord2
* idna
* PyNaCl
* pycparser
* six
* typing-extensions
* urllib3
* youtube-dl

TODO
----
* Add `setup.sh`
* Add more installation details.
* Add more feature details.
* Comment and format source files.

Credits
-------
The hard work done at SkyClan and those who contributed to SkyBot is protected by the Apache License, Version 2.0.
The license can be found at `/LICENSE` and the corresponding copyright notice is at `/NOTICE`.
The code was formatted with the [Black](http://black.readthedocs.io/en/latest/) formatter, which has a really nice and clean style.
