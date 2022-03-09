"""
Some quickly built utils mostly for DAIDE stuff
It would be preferrable to use a real DAIDE parser in prod
"""

__author__ = "Sander Schulhoff"
__email__ = "sanderschulhoff@gmail.com"

from lib2to3.pgen2.parse import ParseError
from typing import List
from diplomacy import Game
import re

def AND(arrangements: List[str]) -> str:
    """
    ANDs together an array of arrangements
    """
    return "AND" + "".join([f" ({a})" for a in arrangements])

def ORR(arrangements: List[str]) -> str:
    """
    ORRs together an array of arrangements
    """
    return "ORR" + "".join([f" ({a})" for a in arrangements])

def XDO(orders: List[str]) -> List[str]:
    """
    Adds XDO to each order in array
    """
    return [f"XDO ({order})" for order in orders]

def get_other_powers(powers: List[str], game: Game):
    """
    :return: powers in the game other than those listed
    in the powers parameter
    """
    return set(game.get_map_power_names()) - set(powers)

def ALY(powers: List[str], game: Game) -> str:
    """
    Forms an alliance proposal string

    :param powers: an array of powers to be allied
    """
    others = get_other_powers(powers, game)
    return "ALY (" + " ".join(powers) + ") VSS (" + " ".join(others) + ")"

def YES(string) -> str:
    """Forms YES message"""
    return f"YES ({string})"

def parse_orr_xdo(msg: str) -> List[str]:
    """
    Attempts to parse a specific message configuration
    """
    # parse may fail
    if "VSS" in msg:
        raise ParseError("This looks an ally message")
    try:
        msg = msg[5:-1]
        parts = msg.split(") (")

        return [part[5:-1] for part in parts]
    except Exception:
        raise ParseError("Cant parse ORR XDO msg")

def parse_alliance_proposal(msg: str, recipient: str) -> List[str]:
    """
    Parses an alliance proposal
    E.g. (assuming the receiving country is RUSSIA)
    "ALY (GERMANY RUSSIA) VSS (FRANCE ENGLAND ITALY TURKEY AUSTRIA)" -> [GERMANY] 
    :param recipient: the power which has received the alliance proposal
    :return: list of allies in the proposal
    """
    groups = re.findall(r'\(([a-zA-Z\s]*)\)', msg)
    
    if len(groups) != 2:
        raise ParseError("Found more than 2 groups")
    
    # get proposed allies
    allies = groups[0].split(" ")

    if recipient not in allies:
        raise ParseError("Recipient not in allies")
    
    allies.remove(recipient)

    if allies:
        return allies 
    else:
        raise ParseError("A minimum of 2 powers are needed for an alliance")


        

def is_order_aggressive(order: str) -> bool:
    """
    Checks if this is an agressive order
    :param order: A string order, e.g. "A BUD S F TRI"
    """
    # empty string
    if not order:
        return True

    return order[0] == 'A'

def get_non_aggressive_orders(orders: List[str]) -> List[str]:
    """
    :return: all non aggressive orders in orders
    """
    return [order for order in orders if not is_order_aggressive(order)]

# def parse_daide_message(msg):
#     """where's ocaml when I need it"""

if __name__ == "__main__":
    from diplomacy import Game
    # game instance
    game = Game()
    # print(AND(["GO HOME", "BAD MONKEY"]))
    # print(XDO(["Move back", "Move"]))
    # msg = ORR(XDO(["Move back", "Move"]))
    # print(parse_orr_xdo(msg))
    # print(ALY(["p1", "p2"]))
    # print(ALY(["GERMANY", "RUSSIA"], game))
    print(parse_alliance_proposal("ALY (GERMANY RUSSIA) VSS (FRANCE ENGLAND ITALY TURKEY AUSTRIA)", "RUSSIA"))
