#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `webexteamsbot` package."""


import unittest
from webexteamsbot import TeamsBot
import requests_mock
from .teams_mock import MockTeamsAPI


class TeamsBotTests(unittest.TestCase):
    @requests_mock.mock()
    def setUp(self, m):
        m.get(
            "https://api.ciscospark.com/v1/webhooks",
            json=MockTeamsAPI.list_webhooks(),
        )
        m.post(
            "https://api.ciscospark.com/v1/webhooks",
            json=MockTeamsAPI.create_webhook(),
        )
        bot_email = "test@test.com"
        teams_token = "somefaketoken"
        bot_url = "http://fakebot.com"
        bot_app_name = "testbot"
        # Create a new bot
        bot = TeamsBot(
            bot_app_name,
            teams_bot_token=teams_token,
            teams_bot_url=bot_url,
            teams_bot_email=bot_email,
            debug=True,
        )

        # Add new command
        bot.add_command(
            "/dosomething", "help for do something", self.do_something
        )
        bot.testing = True
        self.app = bot.test_client()

    def do_something(self, incoming_msg):
        """
        Sample function to do some action.
        :param incoming_msg: The incoming message object from Teams
        :return: A text or markdown based reply
        """
        return "i did what you said - {}".format(incoming_msg.text)

    @requests_mock.mock()
    def test_webhook_already_exists(self, m):
        m.get(
            "https://api.ciscospark.com/v1/webhooks",
            json=MockTeamsAPI.list_webhooks_exist(),
        )
        m.post(
            "https://api.ciscospark.com/v1/webhooks",
            json=MockTeamsAPI.create_webhook(),
        )

        bot_email = "test@test.com"
        teams_token = "somefaketoken"
        bot_url = "http://fakebot.com"
        bot_app_name = "testbot"
        # Create a new bot
        bot = TeamsBot(
            bot_app_name,
            teams_bot_token=teams_token,
            teams_bot_url=bot_url,
            teams_bot_email=bot_email,
            debug=True,
        )

        # Add new command
        bot.add_command(
            "/dosomething", "help for do something", self.do_something
        )
        bot.testing = True
        self.app = bot.test_client()

    @requests_mock.mock()
    def test_bad_config_raises_valueerror(self, m):
        with self.assertRaises(ValueError):
            m.get(
                "https://api.ciscospark.com/v1/webhooks",
                json=MockTeamsAPI.list_webhooks_exist(),
            )
            m.post(
                "https://api.ciscospark.com/v1/webhooks",
                json=MockTeamsAPI.create_webhook(),
            )

            bot_email = None
            teams_token = "somefaketoken"
            bot_url = "http://fakebot.com"
            bot_app_name = "testbot"
            # Create a new bot
            bot = TeamsBot(
                bot_app_name,
                teams_bot_token=teams_token,
                teams_bot_url=bot_url,
                teams_bot_email=bot_email,
                debug=True,
            )

            # Add new command
            bot.add_command(
                "/dosomething", "help for do something", self.do_something
            )
            bot.testing = True
            self.app = bot.test_client()

    @requests_mock.mock()
    def test_teams_setup(self, m):
        m.get(
            "https://api.ciscospark.com/v1/webhooks",
            json=MockTeamsAPI.list_webhooks(),
        )
        m.post(
            "https://api.ciscospark.com/v1/webhooks",
            json=MockTeamsAPI.create_webhook(),
        )

    def test_health_endpoint(self):
        resp = self.app.get("/health")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"I'm Alive", resp.data)

    def test_config_endpoint(self):
        resp = self.app.get("/config")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"test@test.com", resp.data)

    @requests_mock.mock()
    def test_process_incoming_message_send_help(self, m):
        m.get("//api.ciscospark.com/v1/people/me", json=MockTeamsAPI.me())
        m.get(
            "//api.ciscospark.com/v1/messages/incoming_message_id",
            json=MockTeamsAPI.get_message_help(),
        )
        m.post("//api.ciscospark.com/v1/messages", json={})
        resp = self.app.post(
            "/",
            data=MockTeamsAPI.incoming_msg(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        print(resp.data)
        self.assertIn(b"I understand the following commands", resp.data)

    @requests_mock.mock()
    def test_process_incoming_message_default_command(self, m):
        m.get("//api.ciscospark.com/v1/people/me", json=MockTeamsAPI.me())
        m.get(
            "//api.ciscospark.com/v1/messages/incoming_message_id",
            json=MockTeamsAPI.empty_message(),
        )
        m.post("//api.ciscospark.com/v1/messages", json={})
        resp = self.app.post(
            "/",
            data=MockTeamsAPI.incoming_msg(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        print(resp.data)
        self.assertIn(b"I understand the following commands", resp.data)

    @requests_mock.mock()
    def test_process_incoming_membership_check_sender_fail(self, m):
        m.get('https://api.ciscospark.com/v1/webhooks',
              json=MockTeamsAPI.list_webhooks())
        m.post('https://api.ciscospark.com/v1/webhooks',
               json=MockTeamsAPI.create_webhook())
        m.post('//api.ciscospark.com/v1/messages', json={})
        bot_email = "test@test.com"
        teams_token = "somefaketoken"
        bot_url = "http://fakebot.com"
        bot_app_name = "testbot"
        # Create a new bot
        bot = TeamsBot(bot_app_name,
                       teams_bot_token=teams_token,
                       teams_bot_url=bot_url,
                       teams_bot_email=bot_email,
                       debug=True,
                       webhook_resource="memberships",
                       webhook_event="all")

        # Add new command
        bot.add_command('memberships',
                        '*',
                        self.check_membership)
        bot.testing = True
        self.app = bot.test_client()

        resp = self.app.post('/',
                             data=MockTeamsAPI.incoming_membership_fail(),
                             content_type="application/json")
        self.assertEqual(resp.status_code, 200)
        print(resp.data)
        self.assertIn(b"failed", resp.data)

    @requests_mock.mock()
    def test_process_incoming_membership_check_sender_pass(self, m):
        m.get('https://api.ciscospark.com/v1/webhooks',
              json=MockTeamsAPI.list_webhooks())
        m.post('https://api.ciscospark.com/v1/webhooks',
               json=MockTeamsAPI.create_webhook())
        m.post('//api.ciscospark.com/v1/messages', json={})
        bot_email = "test@test.com"
        teams_token = "somefaketoken"
        bot_url = "http://fakebot.com"
        bot_app_name = "testbot"
        # Create a new bot
        bot = TeamsBot(bot_app_name,
                       teams_bot_token=teams_token,
                       teams_bot_url=bot_url,
                       teams_bot_email=bot_email,
                       debug=True,
                       webhook_resource="memberships",
                       webhook_event="all")

        # Add new command
        bot.add_command('memberships',
                        '*',
                        self.check_membership)
        bot.testing = True
        self.app = bot.test_client()

        resp = self.app.post('/',
                             data=MockTeamsAPI.incoming_membership_pass(),
                             content_type="application/json")
        self.assertEqual(resp.status_code, 200)
        print(resp.data)
        self.assertIn(b"success", resp.data)

    def check_membership(self, ob, incoming_msg):
        """
        Sample function to do some action.
        :param incoming_msg: The incoming message object from Spark
        :param ob: Spark API object
        :return: A text or markdown based reply
        """

        whitelist = ["cisco.com"]
        pemail = incoming_msg["data"]["personEmail"]
        pdom = pemail.split("@")[1]

        if pdom in whitelist:
            return "success"
        else:
            return "failed"

    @requests_mock.mock()
    def test_process_incoming_message_match_command(self, m):
        m.get("//api.ciscospark.com/v1/people/me", json=MockTeamsAPI.me())
        m.get(
            "//api.ciscospark.com/v1/messages/incoming_message_id",
            json=MockTeamsAPI.get_message_dosomething(),
        )
        m.post("//api.ciscospark.com/v1/messages", json={})
        resp = self.app.post(
            "/",
            data=MockTeamsAPI.incoming_msg(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        print(resp.data)
        # self.assertIn(b'I understand the following commands', resp.data)

    @requests_mock.mock()
    def test_process_incoming_message_from_bot(self, m):
        m.get("//api.ciscospark.com/v1/people/me", json=MockTeamsAPI.me())
        m.get(
            "//api.ciscospark.com/v1/messages/incoming_message_id",
            json=MockTeamsAPI.get_message_from_bot(),
        )
        m.post("//api.ciscospark.com/v1/messages", json={})
        resp = self.app.post(
            "/",
            data=MockTeamsAPI.incoming_msg(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        print(resp.data)

    def tearDown(self):
        pass
