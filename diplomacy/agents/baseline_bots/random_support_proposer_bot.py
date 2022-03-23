__author__ = "Kartik Shenoy"
__email__ = "kartik.shenoyy@gmail.com"

from collections import defaultdict
from diplomacy import Message
from diplomacy.agents.baseline_bots.baseline_bot import BaselineBot
import random
from diplomacy.agents.baseline_bots.daide_utils import get_order_tokens, ORR, XDO


class RandomSupportProposerBot(BaselineBot):
    """
    This bot reads proposed order messages from other powers.
    It then randomly selects some to take and messages the proposing powers
    with whichever proposed orders of theirs it selected.
    NOTE: It will only execute non-aggressive moves
    """

    def __init__(self, power_name, game) -> None:
        super().__init__(power_name, game)

    def act(self):
        #TODO: Replace orderable locations with all possible units of a power
        self.possible_orders = self.game.get_all_possible_orders()
        provs = [loc.upper() for loc in self.game.get_orderable_locations(self.power_name)]

        n_provs = set()
        for prov in provs:
            n_provs.update(set([prov2.upper() for prov2 in self.game.map.abut_list(prov) if prov2 not in provs]))
        n2n_provs = set()
        for prov in n_provs:
            n2n_provs.update(
                set([prov2.upper() for prov2 in self.game.map.abut_list(prov) if prov2 not in provs and prov2 not in n_provs]))
        # print(provs)
        # print(n_provs)
        # print(n2n_provs)
        possible_support_proposals = defaultdict(list)
        for n2n_p in n2n_provs:
            if not(self.possible_orders[n2n_p]):
                continue
            possible_orders = self.possible_orders[n2n_p]

            for order in possible_orders:
                order_tokens = get_order_tokens(order)
                if len(order_tokens) <= 1 or order_tokens[1] != 'S':
                    continue
                if len(order_tokens) != 4 or order_tokens[2].split()[1] not in provs or order_tokens[3].split()[1] not in n_provs:
                    continue
                possible_support_proposals[(order_tokens[2].split()[1], order_tokens[3].split()[1])].append((order_tokens[0], order))
        final_messages = defaultdict(list)
        for attack_key in possible_support_proposals:
            selected_order = random.choice(possible_support_proposals[attack_key])
            if self.game._unit_owner(selected_order[0]) is None:
                raise "Coding Error"
            final_messages[self.game._unit_owner(selected_order[0]).name].append(selected_order[1])

        messages = []
        for recipient in final_messages:
            suggested_proposals = ORR(XDO(final_messages[recipient]))
            messages.append((self.power_name, recipient, str(suggested_proposals)))
            # # send the other power a message containing the orders
            # self.game.add_message(Message(
            #     sender=self.power_name,
            #     recipient=recipient,
            #     # convert the random orders to a str
            #     message=str(suggested_proposals),
            #     phase=self.game.get_current_phase(),
            # ))
        random_orders = [random.choice(self.possible_orders[loc]) for loc in
                         self.game.get_orderable_locations(self.power_name)
                         if self.possible_orders[loc]]
        # set the orders
        # self.game.set_orders(self.power_name, random_orders)

        return messages, random_orders

if __name__ == "__main__":
    from diplomacy import Game
    from diplomacy.utils.export import to_saved_game_format
    from random_allier_proposer_bot import RandomAllierProposerBot

    # game instance
    game = Game()
    powers = list(game.get_map_power_names())
    # select the first name in the list of powers
    bot_power = powers[0]
    # instantiate proposed random honest bot
    bot = RandomSupportProposerBot(bot_power, game)
    while not game.is_game_done:
        bot.act()
        game.process()

    to_saved_game_format(game, output_path='RandomSupportProposerBot.json')
