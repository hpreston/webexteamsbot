# webexteamsbot

This package makes creating [Webex Teams](https://www.webex.com/products/teams/index.html) bots in Python super simple.  

[![PyPI version](https://badge.fury.io/py/webexteamsbot.svg)](https://badge.fury.io/py/webexteamsbot) [![published](https://static.production.devnetcloud.com/codeexchange/assets/images/devnet-published.svg)](https://developer.cisco.com/codeexchange/github/repo/hpreston/webexteamsbot)

> This package is based on the previous [ciscosparkbot](https://github.com/imapex/ciscosparkbot) project.  This version will both move to new Webex Teams branding as well as add new functionality.  If you've used `ciscosparkbot` you will find this package very similar and familiar.  

# Prerequisites

If you don't already have a [Webex Teams](https://www.webex.com/products/teams/index.html) account, go ahead and [register](https://www.webex.com/pricing/free-trial.html) for one.  They are free.

1. You'll need to start by adding your bot to the Webex Teams website.

    [https://developer.webex.com/my-apps](https://developer.webex.com/my-apps)

1. Click **Create a New App**

    ![add-app](https://github.com/hpreston/webexteamsbot/raw/master/images/newapp.jpg)

1. Click **Create a Bot**.

    ![create-bot](https://github.com/hpreston/webexteamsbot/raw/master/images/createbot.jpg)

2. Fill out all the details about your bot.  You'll need to set a name, username, icon (either upload one or choose a sample), and provide a description.

    ![add-bot](https://github.com/hpreston/webexteamsbot/raw/master/images/newbot.jpg)

3. Click **Add Bot**.

1. On the Congratulations screen, make sure to copy the *Bot's Access Token*, you will need this in a second.

    ![enter-details](https://github.com/hpreston/webexteamsbot/raw/master/images/botcongrats.jpg)

# Installation

> Python 3.6+ is recommended.  Python 2.7 should also work.  

1. Create a virtualenv and install the module

    ```
    python3.6 -m venv venv
    source venv/bin/activate
    pip install webexteamsbot
    ```

# Usage

1. The easiest way to use this module is to set a few environment variables

    > Note: See [ngrok](#ngrok) for details on setting up an easy HTTP tunnel for development.

    ```
    export TEAMS_BOT_URL=https://mypublicsite.io
    export TEAMS_BOT_TOKEN=<your bots token>
    export TEAMS_BOT_EMAIL=<your bots email>
    export TEAMS_BOT_APP_NAME=<your bots name>
    ```

1. A basic bot requires very little code to get going.  

    ```python
    import os
    from webexteamsbot import TeamsBot

    # Retrieve required details from environment variables
    bot_email = os.getenv("TEAMS_BOT_EMAIL")
    teams_token = os.getenv("TEAMS_BOT_TOKEN")
    bot_url = os.getenv("TEAMS_BOT_URL")
    bot_app_name = os.getenv("TEAMS_BOT_APP_NAME")

    # Create a Bot Object
    bot = TeamsBot(
        bot_app_name,
        teams_bot_token=teams_token,
        teams_bot_url=bot_url,
        teams_bot_email=bot_email,
    )


    # A simple command that returns a basic string that will be sent as a reply
    def do_something(incoming_msg):
        """
        Sample function to do some action.
        :param incoming_msg: The incoming message object from Teams
        :return: A text or markdown based reply
        """
        return "i did what you said - {}".format(incoming_msg.text)


    # Add new commands to the box.
    bot.add_command("/dosomething", "help for do something", do_something)


    if __name__ == "__main__":
        # Run Bot
        bot.run(host="0.0.0.0", port=5000)
    ```

1. A [sample script](https://github.com/hpreston/webexteamsbot/blob/master/sample.py) that shows more advanced bot features and customization is also provided in the repo.  

## Advanced Options
### Changing the Help Message
1. Although "set_greeting" has existed for a while now, you may mostly like the internal greeting mechanism, but only want to change the help banner itself. You can do that with the "set_help_message" command like this:
    ```python
    bot.set_help_message("Welcome to the Super Cool Bot! You can use the following commands:\n")
    ```
### Working with events other than created messages
1. By default, the bot will configure the webhook to listen for messages:created events. This behavior can be changed using the "webhook_resource" and "webhook_event" parameters. So, for example, if you wish for the bot to monitor any changes to a room's membership list, you would instanciate the bot like this:
    ```python
    # Create a Bot Object
    bot = TeamsBot(
        bot_app_name,
        teams_bot_token=teams_token,
        teams_bot_url=bot_url,
        teams_bot_email=bot_email,
        webhook_resource="memberships",
        webhook_event="all",
    )
    ```

    You also need a way to catch anything other than "messages", which is the only thing handled entirely inside the bot framework. Continuing the example of monitoring for membership changes in a room, you would also need to add a "command" to catch the membership events. You would use the following to do so:
    ```python
    # check membership:all webhook to verify that person added to room (or otherwise modified) is allowed to be in the room 
    def check_memberships(api, incoming_msg):
        wl_dom = os.getenv("WHITELIST_DOMAINS")
        if wl_dom.find("[") < 0:
            wl_dom = '["' + wl_dom + '"]'
            wl_dom = wl_dom.replace(",", '","')
    
        if wl_dom and incoming_msg["event"] != "deleted":
            pemail = incoming_msg["data"]["personEmail"]
            pid = incoming_msg["data"]["personId"]
            pdom = pemail.split("@")[1]
            plist = json.loads(wl_dom)
            print(pemail, pdom, plist)
            if pdom in plist or pemail == bot_email:
                # membership check succeeded
                return ""
            else:
                # membership check failed
                print("membership failed. deleting " + incoming_msg["data"]["id"])
                api.memberships.delete(incoming_msg["data"]["id"])
                api.messages.create(toPersonId=pid, markdown="You were automatically removed from the space because "
                                            "it is restricted to employees.")
                return "'" + pemail + "' was automatically removed from this space; it is restricted to only " \
                                        "internal users."
    
        return ""
    
    ###### 
    
    bot.add_command('memberships', '*', check_memberships)
    ```
    The first argument, "memberships", tells the bot to look for resources of the type "memberships", the second argument "*" instructs the bot that this is not something that should be included in the internal "help" command, and the third command is the function to execute to handle the membership creation.

1. The bot can also be configured to listen for multiple different events. So, for example, if you wish for the bot to monitor not only new messages in a room, but also any card actions in a room, you would instanciate the bot like this:
    ```python
    # Create a Bot Object
    bot = TeamsBot(
        bot_app_name,
        teams_bot_token=teams_token,
        teams_bot_url=bot_url,
        teams_bot_email=bot_email,
        webhook_resource_event=[{"resource": "messages", "event": "created"},
                                {"resource": "attachmentActions", "event": "created"}]
    )
    ```
    Once again, You also need a way to catch anything other than "messages". Continuing the example of monitoring card actions, you would also need to add a "command" to catch the card actions. You would use the following to do so:
    ```python
    # API request to get card actions (not currently covered in webexteamssdk==1.2)
    def get_attachment_actions(attachmentid):
        headers = {
            'content-type': 'application/json; charset=utf-8',
            'authorization': 'Bearer ' + teams_token
        }
    
        url = 'https://api.ciscospark.com/v1/attachment/actions/' + attachmentid
        response = requests.get(url, headers=headers)
        return response.json()

    # check attachmentActions:created webhook to handle any card actions 
    def handle_cards(api, incoming_msg):
        m = get_attachment_actions(incoming_msg["data"]["id"])
        print(m)
            
        return m["inputs"]
    
    ###### 
    
    bot.add_command('attachmentActions', '*', handle_cards)
    ```
    The first argument, "attachmentActions", tells the bot to look for resources of the type "attachmentActions", the second argument "*" instructs the bot that this is not something that should be included in the internal "help" command, and the third command is the function to execute to handle the card action.

### Creating arbitrary HTTP Endpoints/URLs 
1. You can also add a new path to Flask by using the "add_new_url" command. You can use this so that the bot can handle things other than Webex Teams Webhooks. For example, if you wanted to receive other webhooks to the "/webhooks" path, you would use this:
    ```python
    def handle_webhooks():
        try:
            webhook_event = json.loads(request.data.decode("UTF-8"))
        except:
            return ""
        netid = webhook_event["networkId"]
        print(netid)

    ###### 

    bot.add_new_url("/webhooks", "webhooks", handle_webhooks)
    ```
    The first argument, "/webhooks", represents the URL path to listen for, the second argument represents the Flask endpoint, and the third command is the function to execute to handle GET, PUT, or POST actions.

### Limiting Who Can Interact with the Bot 
1. By default the bot will reply to any Webex Teams user who talks with it.  But you may want to setup a Bot that only talks to "approved users". 
1. Start by creating a list of email addresses of your approved users. 

    ```python
    approved_users = [
        "josmith@demo.local",
    ]
    ```

1. Now when creating the bot object, simply add the `approved_users` parameter. 

    ```python
    bot = TeamsBot(
        bot_app_name,
        teams_bot_token=teams_token,
        teams_bot_url=bot_url,
        teams_bot_email=bot_email,
        approved_users=approved_users,
    )
    ```

1. Now if a users **NOT** listed in the `approved_users` list attempts to communicate with the bot, the message will be ignored and a notification is logged. 

    ```
    Message from: hapresto@cisco.com
    User: hapresto@cisco.com is not approved to interact with bot. Ignoring.
    ```

# ngrok

[ngrok](http://ngrok.com) will make easy for you to develop your code with a live bot.

You can find installation instructions here: [https://ngrok.com/download](https://ngrok.com/download)

1. After you've installed `ngrok`, in another window start the service

    ```
    ngrok http 5000
    ```

1. You should see a screen that looks like this:

    ```
    ngrok by @inconshreveable                                                                                                                                 (Ctrl+C to quit)

    Session Status                online
    Version                       2.2.4
    Region                        United States (us)
    Web Interface                 http://127.0.0.1:4040
    Forwarding                    http://this.is.the.url.you.need -> localhost:5000
    Forwarding                    https://this.is.the.url.you.need -> localhost:5000

    Connections                   ttl     opn     rt1     rt5     p50     p90
                                  2       0       0.00    0.00    0.77    1.16

    HTTP Requests
    -------------

    POST /                         200 OK
    ```

1. Make sure and update your environment with this url:

    ```
    export TEAMS_BOT_URL=https://this.is.the.url.you.need

    ```

1. Now launch your bot!!

    ```
    python sample.py
    ```

## Local Development

If you have an idea for a feature you would like to see, we gladly accept pull requests.  To get started developing, simply run the following..

```
git clone https://github.com/hpreston/webexteamsbot
cd webexteamsbot
pip install -r requirements_dev.txt
python setup.py develop
```

### Linting

We use flake 8 to lint our code. Please keep the repository clean by running:

```
flake8
```

### Testing

Tests are located in the [tests](./tests) directory.

To run the tests in the `tests` folder, you can run the following command
from the project root.

```
coverage run --source=webexteamsbot setup.py test
coverage html
```

This will generate a code coverage report in a directory called `htmlcov`

# Credits
The initial packaging of the original `ciscosparkbot` project was done by [Kevin Corbin](https://github.com/kecorbin).  

This package was created with
[Cookiecutter](https://github.com/audreyr/cookiecutter) and the
[audreyr/cookiecutter-pypackage](https://github.com/audreyr/cookiecutter-pypackage)
project template.
