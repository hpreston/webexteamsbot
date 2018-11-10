# -*- coding: utf-8 -*-
"""
Sample code for using webexteamsbot
"""

import os
from webexteamsbot import TeamsBot
from webexteamsbot.models import Response

# Retrieve required details from environment variables
bot_email = os.getenv("TEAMS_BOT_EMAIL")
teams_token = os.getenv("TEAMS_BOT_TOKEN")
bot_url = os.getenv("TEAMS_BOT_URL")
bot_app_name = os.getenv("TEAMS_BOT_APP_NAME")


def do_something(incoming_msg):
    """
    Sample function to do some action.
    :param incoming_msg: The incoming message object from Teams
    :return: A text or markdown based reply
    """
    return "i did what you said - {}".format(incoming_msg.text)


def ret_message(incoming_msg):
    m = Response()
    u = 'https://sayingimages.com/wp-content/uploads/'
    u = u + 'aaaaaalll-righty-then-alrighty-meme.jpg'
    m.files = u
    return m


# Create a new bot
bot = TeamsBot(bot_app_name, teams_bot_token=teams_token,
               teams_bot_url=bot_url, teams_bot_email=bot_email, debug=True)


# Add new command
bot.add_command('/dosomething', 'help for do something', do_something)
bot.add_command('/demo', 'sample that allows Webex Teams message to be returned',
                ret_message)

# Run Bot
bot.run(host='0.0.0.0', port=5000)
