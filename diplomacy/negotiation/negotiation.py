
import json
import logging
import pkg_resources
import requests

import sys


from diplomacy.engine.daide_composer_message import DaideComposerMessage
from diplomacy.engine.power import Power
import diplomacy.settings

LOGGER = logging.getLogger(__name__)

# Load Name2Token lookup reference.
LOOKUP_REF = json.loads(pkg_resources.resource_stream(
    __name__, 'reference.json').read().decode())


def empires_to_tokens(empires):
    # Process empires list to tokens separated by

    return ' '.join([*map(LOOKUP_REF.get, [e.lower() for e in empires])])


def build_daide(daide, negotiation, message_history, messages, sender, recipient, powers):
    LOGGER.info(f'Building DAIDE from: {negotiation}')
    # Build DAIDE based on the root negotiation action.
    action = str(negotiation['action']).lower()

    if 'alliance' in action:
        # Level 10 ALY
        actors = empires_to_tokens(negotiation['actors'])
        targets = empires_to_tokens(negotiation['targets'])
        daide = daide + f"(PRP (ALY ({actors}) VSS ({targets})))"

    elif 'dmz' in action:
        # Level 20 DMZ
        actors = empires_to_tokens([sender,recipient])
        provinces = negotiation['dmzLocation']\
            .replace('ENG','ECH') #fix for ENG to English Channel
        daide = daide + f'(PRP (DMZ ({actors}) ({provinces})))'

    elif 'draw' in action:
        # Level 10 DRW
        actors = empires_to_tokens(negotiation['actors'])
        if len(actors) > 0:
            daide = daide + f'(PRP (DRW))'
        else:
            daide = daide + f'(PRP (DRW ({actors})))'

    elif 'order' in action:
        # Level 20 XRD
        # move, hold, support move, support hold, convoy
        # An XDO arrangement applies to the next turn in which the order type is valid – so the next movement turn for a HLD, MTO,
        # SUP, CVY or CTO order, the next retreat turn for a RTO or DSB order, and the next adjustment turn for a BLD, REM or WVE
        # order.

        # diplomacy/web/src/gui/utils/order_building.js LN 141 single letters lookup to DAIDE.

        # Process order components.
        order = negotiation['order'] if 'order' in negotiation else None
        end_location = negotiation['endLocation'].replace('ENG','ECH') if 'endLocation' in negotiation else None
        start_location = negotiation['startLocation'].replace('ENG','ECH') if 'startLocation' in negotiation else None
        mid_location = negotiation['midLocation'].replace('ENG','ECH') if 'midLocation' in negotiation else None
        target = negotiation['orderTarget'] if 'orderTarget' in negotiation else None

        # Check target
        if target == 'player':
            target_name = sender
            second_name = recipient
        else:
            target_name = recipient
            second_name = sender

        # Process order components to DAIDE.
        if order == 'H':
            order = 'HLD'
        elif order == 'M':
            order = 'MTO'
        elif order == 'S':
            order = 'SUP'
        elif order == "C":
            order = "CVY"

        # Obtain the target power and its unit types
        power = powers[target_name]
        units = power.units
        units_dict = {}
        for i in units:
            location = i.split(' ')[1]
            unit_type = i.split(' ')[0]
            if unit_type == 'F':
                unit_type_daide = 'FLT'
            elif unit_type == 'A':
                unit_type_daide = 'AMY'
            units_dict[location] = unit_type_daide
        LOGGER.info(f"Units: {units_dict}")

        # Determine what type of unit it has at the start location (fleet vs army)
        unit = units_dict[start_location]
        actor = empires_to_tokens([target_name])
        secondary_unit = ''
        secondary_actor = ''
        # We really need to check what the unit/power combo of the mid_location is agnostically from the sender/recipient data.
        # Best way I have thought is to check first if the target has units in that location, then check recipient, then loop through all available powers.
        # The possibleOrders object takes a location but doesn't tie to powers. The power.units needs the chosen power first.
        if mid_location:
            if mid_location in units_dict:
                secondary_unit = units_dict[mid_location]
                secondary_actor = empires_to_tokens([target_name])
            else:
                try:
                    second_unit_dict = construct_units_dict(power_name=second_name, powers=powers)
                    secondary_unit = second_unit_dict[mid_location]
                    secondary_actor = empires_to_tokens([second_name])
                except Exception as e:
                    LOGGER.info("Likely a third party in support move: {}".format(e))
                    for power in powers:
                        LOGGER.info("Power info: {}".format(power))
                        if power != sender and power != recipient:
                            second_unit_dict = construct_units_dict(power_name=power, powers=powers)
                            if mid_location in second_unit_dict:
                                secondary_unit = second_unit_dict[mid_location]
                                secondary_actor = empires_to_tokens([power])


        if(order != "SUP" and order != "CVY"):
            daide = daide + \
                f'(PRP (XDO (({actor} {unit} {start_location}) {order} {end_location})))'
        elif(order == "SUP"):
            if end_location:
                daide = daide + \
                    f'(PRP (XDO (({actor} {unit} {start_location}) {order} ({secondary_actor} {secondary_unit} {mid_location}) MTO {end_location})))'
            else:
                daide = daide + \
                    f'(PRP (XDO (({actor} {unit} {start_location}) {order} ({secondary_actor} {secondary_unit} {mid_location})))'
        elif(order == "CVY"):
            daide = daide + \
                f'(PRP (XDO (({actor} {unit} {start_location}) {order} ({secondary_actor} {secondary_unit} {mid_location}) MTO {end_location})))'

    elif 'peace' in action:
        # Level 10 PCE

        # Process actors to tokens.
        actors = empires_to_tokens(negotiation['actors'])
        daide = daide + f'(PRP (PCE ({actors})))'

    elif 'solo' in action:
        # Level 10 SLO

        actors = empires_to_tokens(negotiation['actors'])
        daide = daide + f'(PRP (SLO ({actors})))'

    elif 'response' in action:

        # Level 10 YES, REJ, BSW responses
        # message_daide: (PRP (ALY (ITA) VSS (GER)))

        # Filter for messages between these powers.
        message_daide = get_message_daide(
            message_history, messages, sender, recipient, 'response')

        # no: REJ, noyb: BWX, default to yes
        response = str(negotiation['response']).lower()
        if response == 'no':
            response = 'REJ'
        elif response == 'noyb':
            response = 'BWX'
        else:
            response = 'YES'

        daide = daide + f'({response} ({message_daide}))'

    elif 'cancel' in action:
        # Level 10 Cancelling a proposal

        # Filter for messages between these powers.
        message_daide = get_message_daide(
            message_history, messages, sender, recipient, 'cancel')
        daide = daide + f'(CCL ({message_daide}))'

    # Handle action modifiers.
    if 'notify' in action:
        # Add FCT to arrangement.
        daide = f"{daide.replace('PRP', 'FCT')}"

    if 'oppose' in action:
        # Add NOT to arrangement.
        daide = f"{daide.replace('PRP', 'PRP (NOT')})"

    LOGGER.info(f'Built DAIDE: {daide}')
    return daide


def get_message_daide(message_history, messages, sender, recipient, action):
    """
    Description
    -----------
        For responses, get the original message DAIDE without sender/recipient.

    Parameters
    ----------
        messages: SortedDict in diplomacy.utils.sorted_dict
            For the current turn.
        message_history: SortedDict of SortedDict objects
            Loaded from json db and completed turns.
            "phase": {timestamp:Message, timestamp:Message, ...}
        sender: str
            The sender of the message being processed.
        recipient: str
            The recipient of the message being processed.
        action: str
            response or cancel, determines directionality of message we want.

    Notes
    -----
        For a response, we look for messages that reverse the directionality of the
        current message's sender and recipient.

        For a cancel, we look for messages with the same sender and recipient.

    """

    # Determine the directionality of the messages.
    if 'response' in action:
        messenger1 = sender
        messenger2 = recipient
    else:
        messenger2 = sender
        messenger1 = recipient

    for message in messages.reversed_values():
        if (message.recipient == messenger1 and message.sender == messenger2):
            # Last message between these powers.
            # message.daide: FRM (AUS) (ITA) (PRP (ALY (ITA) VSS (GER)))

            # Leave only PRP, FCT, etc. portion.
            # Split after 3rd (.
            proposal = message.daide.split('(')[3:]
            # Rejoin array with ( and remove trailing ).
            return '('.join(proposal)[:-1]

    for phase_message_history in message_history.reversed_values():
        for message in phase_message_history.reversed_values():
            if (message.recipient == messenger1 and message.sender == messenger2):
                # Last message between these powers.
                # message.daide: FRM (AUS) (ITA) (PRP (ALY (ITA) VSS (GER)))

                # Leave only PRP, FCT, etc. portion.
                # Split after 3rd (.
                proposal = message.daide.split('(')[3:]
                # Rejoin array with ( and remove trailing ).
                return '('.join(proposal)[:-1]

    return None


def pressgloss(message_obj: DaideComposerMessage, message_history, messages, powers, return_message_obj_str: bool = True):
    """
    Description
    -----------
    Add DAIDE syntax to message.daide and pressgloss to message.message

    Parameters
    ----------
    message_obj: Message
        The Message to modify.

    return_message_obj: bool = True
        Return the Message object as a json string (for press gloss),
        or the tens/glossed message text string (send message).

    Returns
    -------
        The Message object as a json string (for press gloss),
        or the tens/glossed message text string (send message).

    """

    # Convert the Message object negotation str to a dict.
    negotiation = json.loads(message_obj.negotiation)

    # Convert the message to DAIDE.
    LOGGER.info(f'Converting message to DAIDE: {message_obj.message}')
    if message_obj.negotiation != '{}':
        message_obj.daide = to_daide(
            negotiation, message_obj.sender, message_obj.recipient, message_history, messages, powers)

    # Backwards compatible massaging of the tones.
    if 'tones' in negotiation:
        tones = [tone.lower().capitalize() for tone in negotiation['tones']]
    elif message_obj.tones:
        tones = message_obj.tones
    else:
        tones = ["Haughty", "Urgent"]

    # Set the message_obj message to the TENS message created by the Pressgloss API.
    message_obj.message = to_tens(message_obj.daide, tones)

    LOGGER.info(message_obj.to_dict())
    # strip out the the FRM () () ( and final ) from new_message_obj_str
    temp = message_obj.daide[17:(len(message_obj.daide)-1)]
    message_obj.daide = temp

    # If return_message_obj_str == True, then the entire Message object json
    # is returned as a string.
    if return_message_obj_str:
        message_dict = message_obj.to_dict()
        message_string = json.dumps(message_dict)
        return message_string
    else:
        # Return only the generated Pressgloss text.
        return message_obj.message


def to_daide(negotiation: dict, sender: str, recipient: str, message_history, messages, powers):
    """
    Description
    -----------
    Convert UI form data to DAIDE syntax e.g. "FRM (FRA) (ENG) (PRP (XDO ((ENG AMY LVP) HLD)))"
    The UI uses a discreet list of available orders.
    Uses Message.negotiation which is a json string of the Web UI form data and can
    have multiple messages (e.g. for ORR and AND):
        “negotiation":
        {
            "1": {
                “actors": [“France", “Italy"],
                “targets": [“Russia", “Turkey"],
                “action": “Propose alliance",
                “tones" : [“Haughty"],
                "conditional": "OR"
            },
            "2": {
                “actors": [“France", “Italy"],
                “targets": ["Austria", “Germany"],
                “action": “Propose alliance",
                “tones" : [“Haughty"],
                "conditional": ""
        }
    """
    # Initialize the daide string with FROM TO e.g. FRM (FRA) (ENG)
    daide = f'FRM ({LOOKUP_REF[sender.lower()]}) ({LOOKUP_REF[recipient.lower()]}) '

    if len(negotiation.keys()) > 1:
        # Backwards compatibility patch for earlier version of negotiation without indices.
        if ('action' in negotiation and 'order' in negotiation):
            LOGGER.info('action/order negotiation')
            daide = build_daide(daide, negotiation, message_history,
                                messages, sender, recipient, powers)
            return daide

        # Handle Level 30 Mutlipart arrangements and multiple-negotiations.
        # Loop through possibly multiple negotations in message.negotiation.

        for idx, neg in negotiation.items():
            if idx == "1":
                # Set the conditional based on the first negotiation.
                conditional = neg['conditional']
                if conditional.lower() == 'and':
                    daide = daide + 'PRP (AND'
                else:
                    daide = daide + 'PRP (ORR'

            # Build the arrangement based on the standard formula.
            LOGGER.info('multi-part negotiation')
            arrangement_daide = build_daide(
                "", neg, message_history, messages, sender, recipient, powers)

            # Strip (PRP  and final )from the arrangement_daide.
            arrangement_daide = arrangement_daide[5:][:-1]

            # Add the arrangement daide to the main PRP AND/ORR daide.
            daide = f'{daide} {arrangement_daide}'

        # Add the closing PRP ).
        daide = daide + ')'
    else:
        LOGGER.info(negotiation)
        LOGGER.info('other negotiation')
        daide = build_daide(
            daide, negotiation["1"], message_history, messages, sender, recipient, powers)

    LOGGER.info(daide)
    return daide


def to_tens(daide_text, tones):
    """
    Description
    -----------
    Pass DAIDE syntax to the pressgloss API to return
    Tone-ENhanced Syntax

    Parameters
    ----------
    daide_text: str
        DAIDE syntax to pass to the pressgloss API.

    tones: list[str]
        Optional tones.

    """
    if not diplomacy.settings.PRESSGLOSS_URL:
        LOGGER.info("Skipping sending DAIDE to Pressgloss API")
        return None

    LOGGER.info("Sending DAIDE to Pressgloss API")
    endpoint = f"{diplomacy.settings.PRESSGLOSS_URL}/daide2gloss"
    tones=[]
    request_json = {"daidetext": daide_text, "tones": tones}

    try:
        gloss_response = requests.post(endpoint, json=request_json).json()
        gloss = gloss_response.get("gloss", None)
        LOGGER.info(f"Pressgloss response: {gloss}")
        return gloss

    except Exception as e:
        print(e)

# Returns a constructed unit dictionary for unit type lookup by location.
def construct_units_dict(power_name, powers):
    # Obtain the target power and its unit types
    power = powers[power_name]
    units = power.units
    units_dict = {}
    for i in units:
        location = i.split(' ')[1]
        unit_type = i.split(' ')[0]
        if unit_type == 'F':
            unit_type_daide = 'FLT'
        elif unit_type == 'A':
            unit_type_daide = 'AMY'
        units_dict[location] = unit_type_daide
    return units_dict


"""
negotiation = {
    "1": {
        "actors": ["France", "Italy"],
        "targets": ["Russia", "Turkey"],
        "action": "Propose alliance",
        "tones" : ["Haughty"],
        "conditional": "OR"
        },
    "2": {
        "actors": ["France", "Italy"],
        "targets": ["Germany", "Austria"],
        "action": "Propose alliance",
        "tones" : ["Haughty"],
        "conditional": ""
        }
}

daide = to_daide(negotiation=negotiation, sender='France', recipient="Italy", message_history=None, messages=None)
print(daide) # FRM (FRA) (ITA) PRP (ORR (ALY (FRA ITA) VSS (RUS TUR)) (ALY (FRA ITA) VSS (GER AUS)))
"""

"""
negotiation = { 
    "1": {
        "actors": ["France", "Italy"],
        "targets": [],
        "action": "Propose peace",
        "tones" : ["Haughty"],
        "conditional": ""
        }}
daide = to_daide(negotiation=negotiation, sender='France', recipient="Italy", message_history=None, messages=None)
print(daide) # FRM (FRA) (ITA) (PRP (PCE (FRA ITA)))
"""