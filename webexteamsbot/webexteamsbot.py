# -*- coding: utf-8 -*-

"""Main module."""

from flask import Flask, request
from webexteamssdk import WebexTeamsAPI
from webexteamsbot.models import Response
import sys
import json

# __author__ = "imapex"
# __author_email__ = "CiscoTeamsBot@imapex.io"
# __copyright__ = "Copyright (c) 2016 Cisco Systems, Inc."
# __license__ = "Apache 2.0"


class TeamsBot(Flask):
    """An instance of a Webex Teams Bot"""

    def __init__(
        self,
        teams_bot_name,
        teams_bot_token=None,
        teams_api_url=None,
        teams_bot_email=None,
        teams_bot_url=None,
        default_action="/help",
        debug=False,
    ):
        """
        Initialize a new TeamsBot

        :param teams_bot_name: Friendly name for this Bot (webhook name)
        :param teams_bot_token: Teams Auth Token for Bot Account
        :param teams_api_url: URL to the Teams/Webex API endpoint
        :param teams_bot_email: Teams Bot Email Address
        :param teams_bot_url: WebHook URL for this Bot
        :param default_action: What action to take if no command found.
                               Defaults to /help
        :param debug: boolean value for debut messages
        """

        super(TeamsBot, self).__init__(teams_bot_name)

        # Verify required parameters provided
        if None in (
            teams_bot_name,
            teams_bot_token,
            teams_bot_email,
            teams_bot_token,
        ):
            raise ValueError(
                "TeamsBot requires teams_bot_name, "
                "teams_bot_token, teams_bot_email, teams_bot_url"
            )

        self.DEBUG = debug
        self.teams_bot_name = teams_bot_name
        self.teams_bot_token = teams_bot_token
        self.teams_bot_email = teams_bot_email
        self.teams_bot_url = teams_bot_url
        self.default_action = default_action

        # Create Teams API Object for interacting with Teams
        if teams_api_url:
            self.teams = WebexTeamsAPI(
                access_token=teams_bot_token, base_url=teams_api_url
            )
        else:
            self.teams = WebexTeamsAPI(access_token=teams_bot_token)

        # A dictionary of commands this bot listens to
        # Each key in the dictionary is a command, with associated help
        # text and callback function
        # By default supports 2 command, /echo and /help
        self.commands = {
            "/echo": {
                "help": "Reply back with the same message sent.",
                "callback": self.send_echo,
            },
            "/help": {"help": "Get help.", "callback": self.send_help},
        }

        # Flask Application URLs
        # Basic Health Check for Flask Application
        self.add_url_rule("/health", "health", self.health)
        # Endpoint to enable dynamically configuring account
        self.add_url_rule("/config", "config", self.config_bot)
        # Teams WebHook Target
        self.add_url_rule(
            "/", "index", self.process_incoming_message, methods=["POST"]
        )

        # Setup the Teams WebHook and connections.
        self.teams_setup()

    # *** Bot Setup and Core Processing Functions

    def teams_setup(self):
        """
        Setup the Teams Connection and WebHook
        :return:
        """
        # Update the global variables for config details
        globals()["teams_token"] = self.teams_bot_token
        globals()["bot_email"] = self.teams_bot_email

        sys.stderr.write("Teams Bot Email: " + self.teams_bot_email + "\n")
        sys.stderr.write("Teams Token: REDACTED\n")

        # Setup the Teams Connection
        globals()["teams"] = WebexTeamsAPI(access_token=self.teams_bot_token)
        globals()["webhook"] = self.setup_webhook(
            self.teams_bot_name, self.teams_bot_url
        )
        sys.stderr.write("Configuring Webhook. \n")
        sys.stderr.write("Webhook ID: " + globals()["webhook"].id + "\n")

    # noinspection PyMethodMayBeStatic
    def setup_webhook(self, name, targeturl):
        """
        Setup Teams WebHook to send incoming messages to this bot.
        :param name: Name of the WebHook
        :param targeturl: Target URL for WebHook
        :return: WebHook
        """
        # Get a list of current webhooks
        webhooks = self.teams.webhooks.list()

        # Look for an Existing Webhook with this name, if found update it
        wh = None
        # webhooks is a generator
        for h in webhooks:
            if h.name == name:
                sys.stderr.write("Found existing webhook.  Updating it.\n")
                wh = h

        # No existing webhook found, create new one
        # we reached the end of the generator w/o finding a matching webhook
        if wh is None:
            sys.stderr.write("Creating new webhook.\n")
            wh = self.teams.webhooks.create(
                name=name,
                targetUrl=targeturl,
                resource="messages",
                event="created",
            )

        # if we have an existing webhook update it
        else:
            # Need try block because if there are NO webhooks it throws error
            try:
                wh = self.teams.webhooks.update(
                    webhookId=wh.id, name=name, targetUrl=targeturl
                )
            # https://github.com/CiscoDevNet/ciscoteamsapi/blob/master/ciscoteamsapi/api/webhooks.py#L237
            except Exception as e:
                msg = "Encountered an error updating webhook: {}"
                sys.stderr.write(msg.format(e))

        return wh

    def config_bot(self):
        """
        Method to check and change the Bot Token and Email on the fly.
        :return: Configuration Data for Bot
        """
        # Return the config detail to API requests
        config_data = dict(
            SPARK_BOT_EMAIL=self.teams_bot_email,
            SPARK_BOT_TOKEN="--Redacted--",
            SPARK_BOT_URL=self.teams_bot_url,
            SPARK_BOT_NAME=self.teams_bot_name,
        )

        return json.dumps(config_data)

    # def process_webhook(self):
    #     """
    #     Main entry point for incoming WebHooks
    #     :return: Message reply to send
    #     """
    #
    #     if self.DEBUG:
    #         sys.stderr.write(request)
    #     # Check if the Teams connection has been made
    #     if self.teams is None:
    #         sys.stderr.write("Bot not ready.  \n")
    #         return "Teams Bot not ready.  "
    #
    #     # Retrieve contents of the WebHook
    #     post_data = request.get_json(force=True)
    #     if self.DEBUG:
    #         sys.stderr.write("Webhook content:" + "\n")
    #         sys.stderr.write(str(post_data) + "\n")
    #
    #     # Take the posted data and send to the processing function
    #     msg = self.process_incoming_message()
    #     return jsonify({"message": msg})

    # Not strictly needed for most bots
    # def after_request(self, response):
    #     """
    #     Add additional headers for API
    #     :param response:
    #     :return:
    #     """
    #     response.headers.add('Access-Control-Allow-Origin', '*')
    #     response.headers.add('Access-Control-Allow-Headers',
    #                          'Content-Type,Authorization,Key')
    #     response.headers.add('Access-Control-Allow-Methods',
    #                          'GET,PUT,POST,DELETE,OPTIONS')
    #     return response

    # noinspection PyMethodMayBeStatic
    def health(self):
        """
        Flask App Health Check to verify Web App is up.
        :return:
        """
        return "I'm Alive"

    def process_incoming_message(self):
        """
        Process an incoming message, determine the command and action,
        and determine reply.
        :return:
        """

        # Get the webhook data
        post_data = request.json

        # Determine the Teams Room to send reply to
        room_id = post_data["data"]["roomId"]

        # Get the details about the message that was sent.
        message_id = post_data["data"]["id"]
        message = self.teams.messages.get(message_id)
        if self.DEBUG:
            sys.stderr.write("Message content:" + "\n")
            sys.stderr.write(str(message) + "\n")

        # First make sure not processing a message from the bots
        # Needed to avoid the bot talking to itself
        # We check using IDs instead of emails since the email
        # of the bot could change while the bot is running
        # for example from bot@teamsbot.io to bot@webex.bot
        if message.personId in self.teams.people.me().id:
            if self.DEBUG:
                sys.stderr.write("Ignoring message from our self" + "\n")
            return ""

        # Log details on message
        sys.stderr.write("Message from: " + message.personEmail + "\n")

        # Find the command that was sent, if any
        command = ""
        for c in self.commands.items():
            if message.text.find(c[0]) != -1:
                command = c[0]
                sys.stderr.write("Found command: " + command + "\n")
                # If a command was found, stop looking for others
                break

        # Build the reply to the user
        reply = ""

        # Take action based on command
        # If no command found, send the default_action
        if command in [""] and self.default_action:
            # noinspection PyCallingNonCallable
            reply = self.commands[self.default_action]["callback"](message)
        elif command in self.commands.keys():
            # noinspection PyCallingNonCallable
            reply = self.commands[command]["callback"](message)
        else:
            pass

        # allow command handlers to craft their own Teams message
        if reply and isinstance(reply, Response):
            # If the Response lacks a roomId, set it to the incoming room
            if not reply.roomId:
                reply.roomId = room_id
            reply = reply.as_dict()
            self.teams.messages.create(**reply)
            reply = "ok"
        elif reply:
            self.teams.messages.create(roomId=room_id, markdown=reply)
        return reply

    def add_command(self, command, help_message, callback):
        """
        Add a new command to the bot
        :param command: The command string, example "/status"
        :param help_message: A Help string for this command
        :param callback: The function to run when this command is given
        :return:
        """
        self.commands[command] = {"help": help_message, "callback": callback}

    def remove_command(self, command):
        """
        Remove a command from the bot
        :param command: The command string, example "/status"
        :return:
        """
        del self.commands[command]

    def extract_message(self, command, text):
        """
        Return message contents following a given command.
        :param command: Command to search for.  Example "/echo"
        :param text: text to search within.
        :return:
        """
        cmd_loc = text.find(command)
        message = text[cmd_loc + len(command) :]
        return message

    def set_greeting(self, callback):
        """
        Configure the response provided by the bot when no command is found.
        :param callback: The function to run to create and return the greeting.
        :return:
        """
        self.add_command(
            command="/greeting", help_message="*", callback=callback
        )
        self.default_action = "/greeting"

    # *** Default Commands included in Bot
    def send_help(self, post_data):
        """
        Construct a help message for users.
        :param post_data:
        :return:
        """
        message = "Hello!  "
        message += "I understand the following commands:  \n"
        for c in self.commands.items():
            if c[1]["help"][0] != "*":
                message += "* **%s**: %s \n" % (c[0], c[1]["help"])
        return message

    def send_echo(self, post_data):
        """
        Sample command function that just echos back the sent message
        :param post_data:
        :return:
        """
        # Get sent message
        message = self.extract_message("/echo", post_data.text)
        return message
