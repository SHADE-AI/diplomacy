from diplomacy.integration.base_api import BaseAPI
from diplomacy.integration.webdiplomacy_net.game import state_dict_to_game_and_power
from diplomacy.integration.webdiplomacy_net.orders import Order
from diplomacy.integration.webdiplomacy_net.utils import CACHE, GameIdCountryId
import ujson as json
from diplomacy.utils.export import to_saved_game_format
import time
import argparse

def main(args):

    inFile = args['file']
    wd = args['indir']
    outDir = args['outdir']

    inPath = wd + "/" + inFile
    outFile = outDir + "/" + inFile.split(".json")[0] + "_shade.json"


    t1 = time.perf_counter();
    print("Reading file: " + inPath)
    with open(inPath, 'r') as f:
        state_dict = json.load(f)

    country_id = 1
    max_phases = 1000
    game, power_name = state_dict_to_game_and_power(state_dict, country_id, max_phases=max_phases)

    print("Writing data to " + outFile)
    to_saved_game_format(game, outFile)

    t2 = time.perf_counter()
    print(f"{t2-t1}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    #"/Users/jadrake/Local_dev/webdip_db/webDiplomacy/data.json"

    parser.add_argument("--file", type=str, help="Input file name")
    parser.add_argument("--indir", type=str, help="Working directory containing input files to translate")
    parser.add_argument("--outdir", type=str, help="Directory to write output files to")

    args = vars(parser.parse_args())

    main(args)
