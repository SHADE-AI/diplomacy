import asyncio
import random
from diplomacy.client.connection import connect
from diplomacy.utils import exceptions
from random import *
from diplomacy.utils import strings
import time
import argparse
import sys

def on_message_received(network_game, notification):
    msg = notification.message
    sender = msg.sender
    recipient = msg.recipient
    message = msg.message
    print("({}/{}): {} received the following message from {}: \n\t{}".format(network_game.get_current_phase(), notification.game_role, recipient, sender, message))


async def create_game(game_id, hostname='localhost', port=8432):
    """ Creates a game on the server """
    connection = await connect(hostname, port)
    channel = await connection.authenticate('random_user', 'password')
    await channel.create_game(game_id=game_id, map_name='standard_france_austria', rules={'REAL_TIME', 'NO_DEADLINE', 'POWER_CHOICE'})

async def play(game_id, power_name, player_type, hostname='localhost', port=8432):
    """ Play as the specified power """
    connection = await connect(hostname, port)
    channel = await connection.authenticate("power_name_" + player_type,'password')

    # Waiting for the game, then joining it
    while not (await channel.list_games(game_id=game_id)):
        await asyncio.sleep(1.)

    #type = strings.PRESS_BOT
    type = player_type
    print("({}): joining as type = {}".format(power_name, type))
    game = await channel.join_game(game_id=game_id, power_name=power_name, player_type=type)
    print(game)

    game.add_on_game_message_received(on_message_received)

    opponent = ''
    if power_name == "FRANCE": 
        opponent = "AUSTRIA" 
    else: 
        opponent = "FRANCE"
    print(f"Current power: {power_name}\ttype: {player_type}\topponent: {opponent}")

    allPlayersJoined = False
    while game.is_game_active == False & allPlayersJoined == False:

        #all player_type must be not strings.NONE to proceed
        playerTypes = [pow.player_type for pow in game.powers.values()]
        if strings.NONE not in playerTypes:
            allPlayersJoined = True
            print("{}: everyone is ready!".format(power_name))

        await asyncio.sleep(2)

    while not game.is_game_done:
        current_phase = game.get_current_phase()

        if player_type != strings.ADVISOR:
            #send message to opponent
            await asyncio.sleep(15)
            recipient = opponent
            #msg = "({}/{}): sending message to {}".format(current_phase, power_name, recipient)
            msg = f"Hey there from {power_name}:{player_type}"
            print(msg)
            await game.send_game_message(message=game.new_power_message(recipient, msg))
            await asyncio.sleep(5)

            recipient = power_name
            #msg = "({}/{}): sending message to {}".format(current_phase, power_name, recipient)
            msg = f"{power_name}:{player_type} sending message to my advisor"
            print(msg)
            await game.send_game_message(message=game.new_power_message(recipient, msg))
            await asyncio.sleep(5)
        if player_type == strings.ADVISOR:
            await asyncio.sleep(30)
            recipient = power_name
            msg = "({}/{}): sending message to {}".format(current_phase, power_name, recipient)
            msg = f"{power_name}:{player_type} sending message to my player"
            print(msg)
            await game.send_game_message(message=game.new_power_message(recipient, msg))
            await asyncio.sleep(5)

        # Waiting for game to be processed
        while current_phase == game.get_current_phase():
            await asyncio.sleep(2)



async def launch(game_id, power, player_type, host, create_game_flag):
    
    if create_game_flag:
        await create_game(game_id, hostname = host)
    await play(game_id, power, player_type, hostname=host)
    #await asyncio.gather(*[play(game_id, "AUSTRIA", player_type=strings.HUMAN), play(game_id, "AUSTRIA", player_type=strings.ADVISOR),play(game_id, "FRANCE", player_type=strings.HUMAN)])
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--game_id", type=str)
    parser.add_argument("--power", type=str)
    parser.add_argument("--player-type", type=str)
    parser.add_argument("--host", type=str)
    parser.add_argument("--create-game", type=str, required=False)

    args = parser.parse_args()
    print(args.game_id)

    create_game_flag = False
    if args.create_game is not None:
        if args.create_game == "yes":
            create_game_flag = True

    print(create_game_flag)

    asyncio.run(launch(args.game_id, args.power, args.player_type, args.host, create_game_flag))
