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

# Create a custom bot greeting function returned when no command is given.
# The default behavior of the bot is to return the '/help' command response
def greeting(incoming_msg):
    # Loopkup details about sender
    sender = bot.teams.people.get(incoming_msg.personId)

    # Create a Response object and craft a reply in Markdown.
    response = Response()
    response.markdown = "Hello {nickname}, I'm a chat bot.  See what I can do by asking for **/help**.".format(
        nickname=sender.firstName
    )
    return response


def do_something(incoming_msg):
    """
    Sample function to do some action.
    :param incoming_msg: The incoming message object from Teams
    :return: A text or markdown based reply
    """
    return "i did what you said - {}".format(incoming_msg.text)


def ret_message(incoming_msg):
    m = Response()
    u = "https://sayingimages.com/wp-content/uploads/"
    u = u + "aaaaaalll-righty-then-alrighty-meme.jpg"
    m.files = u
    return m


# Create a new bot
bot = TeamsBot(
    bot_app_name,
    teams_bot_token=teams_token,
    teams_bot_url=bot_url,
    teams_bot_email=bot_email,
    debug=True,
)

# Change the bot greeting
bot.set_greeting(greeting)

# Add new command
bot.add_command("/dosomething", "help for do something", do_something)
bot.add_command(
    "/demo",
    "sample that allows Webex Teams message to be returned",
    ret_message,
)

# Run Bot
bot.run(host="0.0.0.0", port=5000)
