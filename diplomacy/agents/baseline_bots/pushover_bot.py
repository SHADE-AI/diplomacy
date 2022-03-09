__author__ = "Sander Schulhoff"
__email__ = "sanderschulhoff@gmail.com"

from baseline_bot import BaselineBot
from daide_utils import parse_orr_xdo

class PushoverBot(BaselineBot):
    """
    Does whatever the last message/bot told it to do
    NOTE: only executes non-aggressive action
    """
    def __init__(self, power_name, game) -> None:
        super().__init__(power_name, game)

    def act(self):
        # get proposed orders sent by other countries
        messages = game.filter_messages(messages = game.messages, game_role=bot_power)
        keys = list(messages.keys())
        keys.sort(reverse=True)
        last_message = messages[keys[0]]
        # parse may fail
        try:
            orders = parse_orr_xdo(last_message.message)
        except:
            pass

        # set the orders
        game.set_orders(self.power_name, orders)

if __name__ == "__main__":
    from diplomacy import Game
    from diplomacy.utils.export import to_saved_game_format
    from random_proposer_bot import RandomProposerBot
    # game instance
    game = Game()
    powers = list(game.get_map_power_names())
    # select the first name in the list of powers
    bot_power = powers[0]
    # instantiate proposed random honest bot
    bot = PushoverBot(bot_power, game)
    proposer_1 = RandomProposerBot(powers[1], game)
    proposer_2 = RandomProposerBot(powers[2], game)
    while not game.is_game_done:
        proposer_1.act()
        proposer_2.act()
        bot.act()

        game.process()


    to_saved_game_format(game, output_path='PushoverBotGame.json')
