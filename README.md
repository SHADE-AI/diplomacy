# Diplomacy: DATC-Compliant Game Engine [![Build Status](https://travis-ci.org/diplomacy/diplomacy.svg?branch=master)](https://travis-ci.org/diplomacy/diplomacy) [![Documentation Status](https://readthedocs.org/projects/diplomacy/badge/?version=latest)](https://diplomacy.readthedocs.io/en/latest/?badge=latest)

This project contains an open-source DATC-compliant Diplomacy game engine, a client-server architecture for network play, a web interface to play against bots and to visualize games, and a DAIDE-compatible adapter to connect DAIDE bots to the server.

<p align="center">
  <img width="500" src="https://github.com/SHADE-AI/diplomacy/blob/master/docs/images/map_overview.png" alt="Diplomacy Map Overview">
</p>

## Documentation

The complete documentation is available at [diplomacy.readthedocs.io](https://diplomacy.readthedocs.io/).

## Getting Started

### Installation

The latest version of the package can be installed with:

```python3
pip install diplomacy
```

The package is compatible with Python 3.5, 3.6, and 3.7.

### Running a game

The following script plays a game locally by submitting random valid orders until the game is completed.

```python3
import random
from diplomacy import Game
from diplomacy.utils.export import to_saved_game_format

# Creating a game
# Alternatively, a map_name can be specified as an argument. e.g. Game(map_name='pure')
game = Game()
while not game.is_game_done:

    # Getting the list of possible orders for all locations
    possible_orders = game.get_all_possible_orders()

    # For each power, randomly sampling a valid order
    for power_name, power in game.powers.items():
        power_orders = [random.choice(possible_orders[loc]) for loc in game.get_orderable_locations(power_name)
                        if possible_orders[loc]]
        game.set_orders(power_name, power_orders)

    # Messages can be sent locally with game.add_message
    # e.g. game.add_message(Message(sender='FRANCE',
    #                               recipient='ENGLAND',
    #                               message='This is a message',
    #                               phase=self.get_current_phase(),
    #                               time_sent=int(time.time())))

    # Processing the game to move to the next phase
    game.process()

# Exporting the game to disk to visualize (game is appended to file)
# Alternatively, we can do >> file.write(json.dumps(to_saved_game_format(game)))
to_saved_game_format(game, output_path='game.json')
```

## Web interface

It is also possible to install a web interface in React to play against bots and/or other humans and to visualize games.

The web interface can be installed with:

```bash
# Install NVM
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.34.0/install.sh | bash

# Clone repo
git clone https://github.com/diplomacy/diplomacy.git

# Install package locally
# You may want to install it in a conda or virtualenv environment
cd diplomacy/
pip install -r requirements_dev.txt

# Build node modules
cd diplomacy/web
npm install .
npm install . --only=dev

# In a terminal window or tab - Launch React server
npm start

# In another terminal window or tab - Launch diplomacy server
python -m diplomacy.server.run
```

The web interface will be accessible at http://localhost:3000.

To login, users can use admin/password or username/password. Additional users can be created by logging in with a username that does not exist in the database.

![](docs/images/web_interface.png)

### Visualizing a game

It is possible to visualize a game by using the "Load a game from disk" menu on the top-right corner of the web interface.

![](docs/images/visualize_game.png)


## Network Game

It is possible to join a game remotely over a network using websockets. The script below plays a game over a network.

Note. The server must be started with `python -m diplomacy.server.run` for the script to work.

From the root directory of this repository, execute:

```
python diplomacy/agents/rand_dip.py -g GAMEID -p ENGLAND,FRANCE,GERMANY,ITALY,RUSSIA,TURKEY
```

Here, `GAMEID` could be something like `admin_1643763675779` which you will find in the created game (7 human players)

## License

This project is licensed under the APGLv3 License - see the [LICENSE](LICENSE) file for details
