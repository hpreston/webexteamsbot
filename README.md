# webexteamsbot
This package makes creating [Webex Teams](https://www.webex.com/products/teams/index.html) bots in Python super simple.  

[![PyPI version](https://badge.fury.io/py/webexteamsbot.svg)](https://badge.fury.io/py/webexteamsbot)

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

1. A [sample script](sample.py) is also provided for your convenience

    ```python
    # -*- coding: utf-8 -*-
    """
    Sample code for using webexteamsbot
    """

    import os
    import requests
    from webexteamsbot import TeamsBot
    from webexteamsbot.models import Response

    # Retrieve required details from environment variables
    bot_email = os.getenv("TEAMS_BOT_EMAIL")
    teams_token = os.getenv("TEAMS_BOT_TOKEN")
    bot_url = os.getenv("TEAMS_BOT_URL")
    bot_app_name = os.getenv("TEAMS_BOT_APP_NAME")

    # Create a Bot Object
    #   Note: debug mode prints out more details about processing to terminal
    bot = TeamsBot(
        bot_app_name,
        teams_bot_token=teams_token,
        teams_bot_url=bot_url,
        teams_bot_email=bot_email,
        debug=True,
    )


    # Create a custom bot greeting function returned when no command is given.
    # The default behavior of the bot is to return the '/help' command response
    def greeting(incoming_msg):
        # Loopkup details about sender
        sender = bot.teams.people.get(incoming_msg.personId)

        # Create a Response object and craft a reply in Markdown.
        response = Response()
        response.markdown = "Hello {}, I'm a chat bot. ".format(sender.firstName)
        response.markdown += "See what I can do by asking for **/help**."
        return response


    # Create functions that will be linked to bot commands to add capabilities
    # ------------------------------------------------------------------------

    # A simple command that returns a basic string that will be sent as a reply
    def do_something(incoming_msg):
        """
        Sample function to do some action.
        :param incoming_msg: The incoming message object from Teams
        :return: A text or markdown based reply
        """
        return "i did what you said - {}".format(incoming_msg.text)


    # An example using a Response object.  Response objects allow more complex
    # replies including sending files, html, markdown, or text. Rsponse objects
    # can also set a roomId to send response to a different room from where
    # incoming message was recieved.
    def ret_message(incoming_msg):
        """
        Sample function that uses a Response object for more options.
        :param incoming_msg: The incoming message object from Teams
        :return: A Response object based reply
        """
        # Create a object to create a reply.
        response = Response()

        # Set the text of the reply.
        response.text = "Here's a fun little meme."

        # Craft a URL for a file to attach to message
        u = "https://sayingimages.com/wp-content/uploads/"
        u = u + "aaaaaalll-righty-then-alrighty-meme.jpg"
        response.files = u
        return response


    # An example command the illustrates using details from incoming message within
    # the command processing.
    def current_time(incoming_msg):
        """
        Sample function that returns the current time for a provided timezone
        :param incoming_msg: The incoming message object from Teams
        :return: A Response object based reply
        """
        # Extract the message content, without the command "/time"
        timezone = bot.extract_message("/time", incoming_msg.text).strip()

        # Craft REST API URL to retrieve current time
        #   Using API from http://worldclockapi.com
        u = "http://worldclockapi.com/api/json/{timezone}/now".format(
            timezone=timezone
        )
        r = requests.get(u).json()

        # If an invalid timezone is provided, the serviceResponse will include
        # error message
        if r["serviceResponse"]:
            return "Error: " + r["serviceResponse"]

        # Format of returned data is "YYYY-MM-DDTHH:MM<OFFSET>"
        #   Example "2018-11-11T22:09-05:00"
        returned_data = r["currentDateTime"].split("T")
        cur_date = returned_data[0]
        cur_time = returned_data[1][:5]
        timezone_name = r["timeZoneName"]

        # Craft a reply string.
        reply = "In {TZ} it is currently {TIME} on {DATE}.".format(
            TZ=timezone_name, TIME=cur_time, DATE=cur_date
        )
        return reply


    # Create help message for current_time command
    current_time_help = "Look up the current time for a given timezone. "
    current_time_help += "_Example: **/time EST**_"

    # Set the bot greeting.
    bot.set_greeting(greeting)

    # Add new commands to the box.
    bot.add_command("/dosomething", "help for do something", do_something)
    bot.add_command(
        "/demo", "Sample that creates a Teams message to be returned.", ret_message
    )
    bot.add_command("/time", current_time_help, current_time)

    # Every bot includes a default "/echo" command.  You can remove it, or any
    # other command with the remove_command(command) method.
    bot.remove_command("/echo")


    if __name__ == "__main__":
        # Run Bot
        bot.run(host="0.0.0.0", port=5000)
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
