from diplomacy.integration.base_api import BaseAPI
from diplomacy.integration.webdiplomacy_net.game import state_dict_to_game_and_power
from diplomacy.integration.webdiplomacy_net.orders import Order
from diplomacy.integration.webdiplomacy_net.utils import CACHE, GameIdCountryId
import ujson as json
from diplomacy.utils.export import to_saved_game_format

def main():

    inFile = "/Users/jadrake/Local_dev/webdip_db/webDiplomacy/data.json"

    with open(inFile, 'r') as f:
        state_dict = json.load(f)

    country_id = 1
    max_phases = 100
    game, power_name = state_dict_to_game_and_power(state_dict, country_id, max_phases=max_phases)
    to_saved_game_format(game, output_path='game.json')


if __name__ == '__main__':
    main()
