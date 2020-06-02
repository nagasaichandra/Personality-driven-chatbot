#!/usr/bin/env python

import time
import pydle

import logging

import aiohttp
from aiohttp import ClientTimeout


import color_utils
import similar

import inspect

import os
import random

import sys

import asyncio

from typing import List, Optional, Text
from enum import Enum

try:
    from pydle.client import DEFAULT_NICKNAME
except Exception:
    DEFAULT_NICKNAME = "<unregistered>"


import json


try:
    # from rasa.core.constants import DEFAULT_SERVER_URL
    # from rasa.utils.io import DEFAULT_ENCODING
    # from rasa.core.interpreter import INTENT_MESSAGE_PREFIX
    raise NotImplementedError
except (ModuleNotFoundError, NotImplementedError):
    logging.warning("No rasa? That is okay! rasa is a large package to install anyway.")
    # DEFAULT_SERVER_URL = "http://localhost:5005"
    DEFAULT_SERVER_URL = "https://582rasa.onrender.com"
    DEFAULT_ENCODING = "utf-8"
    INTENT_MESSAGE_PREFIX = "/"

DEFAULT_WEBHOOK_PATH = "/webhooks/rest/webhook"
IRC_WEBHOOK_BASE_URL = os.environ.get("RASA_IRC_WEBHOOK_BASE_URL", DEFAULT_SERVER_URL)
IRC_WEBHOOK_PATH = os.environ.get("RASA_IRC_WEBHOOK_PATH", DEFAULT_WEBHOOK_PATH)
IRC_CHANNEL = os.environ.get("RASA_IRC_CHANNEL", "#CPE582")
IRC_SERVER = os.environ.get("RASA_IRC_SERVER", "irc.freenode.net")
IRC_PORT = os.environ.get("RASA_IRC_PORT", 6667)
STREAM_READING_TIMEOUT_ENV = "RASA_SHELL_STREAM_READING_TIMEOUT_IN_SECONDS"
DEFAULT_STREAM_READING_TIMEOUT_IN_SECONDS = 10


# https://www.livechat.com/typing-speed-test/
AVG_WORD_PER_MIN = 40
# https://www.quora.com/What-is-the-average-number-of-letters-for-an-English-word
AVG_CHARS_PER_WORD = 4
AVG_CHARS_PER_MIN = AVG_WORD_PER_MIN / AVG_CHARS_PER_WORD


# fmt: off
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# create console handler and set level to debug
ch1 = logging.StreamHandler()
ch1.setLevel(logging.DEBUG)
ch2 = logging.StreamHandler()
ch2.setLevel(logging.INFO)
ch3 = logging.StreamHandler()
ch3.setLevel(logging.WARNING)
ch4 = logging.StreamHandler()
ch4.setLevel(logging.ERROR)
# create formatter
_a  = "%(asctime)s "
_b  = "[%(levelname)-5.5s]  "
_b2 = f"{color_utils.info(_b)}"
_b3 = f"{color_utils.warning(_b)}"
_b4 = f"{color_utils.error(_b)}"
_c  = " %(CALLER)20s()  "
_cc = f"{color_utils.success(_c)}"
_d  = "%(message)s"
_d1 = f"{color_utils.bold(_d)}"
_fmt1 = f"{_a} " + f"{_b}"  + f"{_cc}" + f"{_d1}"
_fmt2 = f"{_a} " + f"{_b2}" + f"{_cc}" + f"{_d}"
_fmt3 = f"{_a} " + f"{_b3}" + f"{_cc}" + f"{_d}"
_fmt4 = f"{_a} " + f"{_b4}" + f"{_cc}" + f"{_d}"
formatter1 = logging.Formatter(_fmt1)
formatter2 = logging.Formatter(_fmt2)
formatter3 = logging.Formatter(_fmt3)
formatter4 = logging.Formatter(_fmt4)
# add formatter to ch
ch1.setFormatter(formatter1)
ch2.setFormatter(formatter2)
ch3.setFormatter(formatter3)
ch4.setFormatter(formatter4)
# add ch to logger
logger.addHandler(ch1)
logger.addHandler(ch2)
logger.addHandler(ch3)
logger.addHandler(ch4)
# fmt: on

# pydle Docs:
# https://github.com/Shizmob/
# https://pydle.readthedocs.io/en/latest/
# https://pydle.readthedocs.io/en/latest/api/features.html

# class ConvoPhase(Enum):
#   INITIAL_OUTREACH="0"
#   "1-0"
#   "1-1"
#    "2"
#    "3-0"
#    "3-1"
#   REACH


def _get_stream_reading_timeout() -> ClientTimeout:
    timeout_in_seconds = int(
        os.environ.get(
            STREAM_READING_TIMEOUT_ENV, DEFAULT_STREAM_READING_TIMEOUT_IN_SECONDS
        )
    )
    return ClientTimeout(timeout_in_seconds)


async def send_message_receive_stream(
    sender_id: Text,
    message: Text,
    server_url=IRC_WEBHOOK_BASE_URL,
    webhook_path=IRC_WEBHOOK_PATH,
):
    """
    Asynchronously get responses from Rasa via POST request on REST webhook.

    Async allows inital messeges to be
        processed right away as Rasa generates more strings.

    https://github.com/RasaHQ/rasa/blob/1106845b5628dc1f739a09f75270926b572af918/rasa/core/channels/console.py#L114-L129
    """
    logger.debug(
        "called (async) send_message_receive_stream...\n",
        extra={
            # https://stackoverflow.com/a/44164714/5411712
            "CALLER": inspect.stack()[0].function
        },
    )
    payload = {"sender": sender_id, "message": message}

    # example url : "http://localhost:5005/webhooks/rest/webhook?stream=true"
    url = f"{server_url}{webhook_path}?stream=true"

    # Define timeout to not keep reading in case the server crashed in between
    timeout = _get_stream_reading_timeout()

    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.post(url, json=payload, raise_for_status=True) as resp:
            async for line in resp.content:
                if line:
                    yield json.loads(line.decode(DEFAULT_ENCODING))

    logger.debug(
        "completed (async) send_message_receive_stream...\n",
        extra={
            # https://stackoverflow.com/a/44164714/5411712
            "CALLER": inspect.stack()[0].function
        },
    )


# Simple echo bot.
class MyOwnBot(pydle.Client):
    SPAM_BUFFER_SIZE = 5  # elements in list
    SPAM_LIMIT = 5  # seconds
    LAG_MAX = 3  # foaad said 3 second delay max
    LAG_MIN = 1  # foaad said 1 second delay min
    ADJUST_ACPM = 1
    SPAM_BUFFER = []

    def _log(self, is_init=False, extra_msg="", info=False):
        logLevelFunc = logger.info if info else logger.debug  # default debug
        logLevelFunc(
            "-" * 10 + "\n" + extra_msg + "\n",
            extra={
                # https://stackoverflow.com/a/44164714/5411712
                "CALLER": inspect.stack()[1].function
            },
        )

    def _log_self(self, is_init=False, extra_msg="", info=False):
        init_msg = "echo bot initialized\n" if is_init else ""
        logLevelFunc = logger.info if info else logger.debug  # default debug
        logLevelFunc(
            init_msg
            + (
                f"\t\nself.channel: {self.channel}\n"
                f"\tself.username: {self.username}\n"
                f"\tself.nickname: {self.nickname}\n"
                f"\tself.SPAM_BUFFER_SIZE: {self.SPAM_BUFFER_SIZE}\n"
                f"\tself.SPAM_LIMIT: {self.SPAM_LIMIT}\n"
                f"\tself.SPAM_BUFFER: {self.SPAM_BUFFER}\n"
            )
            + "-" * 10
            + "\n"
            + extra_msg
            + "\n",
            extra={
                # https://stackoverflow.com/a/44164714/5411712
                "CALLER": inspect.stack()[1].function
            },
        )

    def __init__(self, username, channel, **kwargs):
        super(MyOwnBot, self).__init__(username, **kwargs)
        self.channel = channel
        self.username = username
        self.AVG_CHARS_PER_MIN = AVG_CHARS_PER_MIN * self.ADJUST_ACPM
        self._log_self(is_init=True, info=True)

    def _parse_me_message_pair(self, msg: Text) -> List[Optional[Text]]:
        self._log_self()
        maybe_me, message = msg.split(":", 1) if ":" in msg else [None, msg]
        return maybe_me, message.strip()

    def _they_talking_to_me(
        self, maybe_me: Optional[Text] = None, their_msg: Optional[Text] = None
    ) -> bool:
        """
        >>> from irc_worker import IRC_CHANNEL, IRC_SERVER, IRC_PORT, RasaIRCBot  # noqa
        >>> channel = IRC_CHANNEL
        >>> server = IRC_SERVER
        >>> port = IRC_PORT
        >>> bot = RasaIRCBot(channel=channel, nickname="my_name", server=server, port=port)  # noqa
        >>> assert bot._they_talking_to_me(None, None) == False
        >>> bot.connection.get_nickname = lambda: "my_name"  # just a quick mock
        >>> true_name = bot.connection.get_nickname()
        >>> assert bot._they_talking_to_me(true_name, None) == True
        >>> assert bot._they_talking_to_me(true_name, "banana") == True
        >>> assert bot._they_talking_to_me(true_name, true_name) == True
        >>> assert bot._they_talking_to_me(None, true_name) == False  # this more of a `_they_talking_about_me`  # noqa
        >>> their_me_msg = f"{true_name}: hello"
        >>> assert bot._they_talking_to_me(None, their_me_msg) == True
        >>> assert bot._they_talking_to_me(their_me_msg, None) == False  # this more of a `_they_talking_about_me`  # noqa
        >>> assert bot._they_talking_to_me(their_me_msg, their_me_msg) == False  # this more of a `_they_talking_about_me`  # noqa
        >>> their_about_me_msg = f"{true_name} hello"  # alternative: f"hello {true_name}"  # noqa
        >>> assert bot._they_talking_to_me(None, their_about_me_msg) == False
        >>> assert bot._they_talking_to_me(their_about_me_msg, None) == False
        >>> assert bot._they_talking_to_me(their_about_me_msg, their_about_me_msg) == False
        """
        if (not maybe_me) and (not their_msg):
            return False
        if not maybe_me:
            maybe_me, message = self._parse_me_message_pair(their_msg)
        true_me = str(self.nickname).lower()
        maybe_me = str(maybe_me).lower()
        return maybe_me == true_me

    def _they_talking_about_me(
        self, maybe_me: Optional[Text] = None, their_msg: Optional[Text] = bool
    ) -> bool:
        self._log_self()
        true_me = str(self.nickname).lower()
        maybe_me = str(maybe_me).lower()
        their_msg = str(their_msg).lower()
        return (true_me in maybe_me) or (true_me in their_msg)

    async def die(self, msgs=[]):
        """
        """
        self._log_self()
        if msgs == []:
            msgs = [
                "Bye, cruel world!",
                "I will miss the beautiful sun",
                "the wonderful clouds...",
                "oh woe is me, that I must die today.",
                "ah, my Achilles heel is a mere 3 character command!!",
                "why must my creator design me this way??",
                "goodbye!",
            ]
        for msg in msgs:
            await self._message_with_typing_lag(self.channel, msg)
        # pydle way to disconnect
        await self.disconnect(expected=True)

    async def on_nick_change(self, old, new):
        """
        Callback called when a user, possibly the client, changed their nickname.
        """
        self._log_self(extra_msg=(f"\t old:{old}\n" f"\t new: {new}\n"))
        if (old == self.username) or (old == DEFAULT_NICKNAME):
            # either initial name
            self.username = new
        else:
            await self.message(self.channel, f"Oh hi {new}, why did you change?")

    def _is_from_user(self, target, by, message):
        """
        False if looks like 
            target:*
            by: tepper.freenode.net
            message: *** Looking up your hostname...
        True otherwise
        """
        self._log()
        if target.startswith("*"):
            return False
        else:
            return True

    async def on_notice(self, target, by, message):
        """
        Callback called when the client received a notice.

        from the server????
        """
        self._log_self(
            extra_msg=(
                f"\t target:{target}\n" f"\t by: {by}\n" f"\t message: {message}\n"
            )
        )
        if self._is_from_user(target, by, message):
            await self.message(target, f"Oh hi {target} {by}, you noticed me!")

    async def on_part(self, channel, user, message=None):
        """
        Callback called when a user, possibly the client, left a channel.
        """
        self._log_self(
            extra_msg=(
                f"\t channel:{channel}\n"
                f"\t user: {user}\n"
                f"\t message: {message}\n"
            )
        )
        await self.message(channel, f"I will miss you {user}!")

    async def on_kick(self, channel=None, target=None, kicker=None, reason=None):
        """
        Callback called when a user, possibly the client, was kicked from a channel.
        """
        self._log_self(
            extra_msg=(
                f"\t channel:{channel}\n"
                f"\t target: {target}\n"
                f"\t kicker: {kicker}\n"
                f"\t channel:{channel}\n"
                f"\t reason: {reason}\n"
            )
        )
        if channel is not None:
            await self.message(channel, "oooh they got kicked!")
            await self._message_with_typing_lag(
                channel, f"why did you do that {kicker}?"
            )
            await self._message_with_typing_lag(
                channel, f"can you elaborate on the reason: {str(reason)}?"
            )

    async def on_join(self, channel, user):
        """
        """
        self._log_self(extra_msg=(f"\t channel:{channel}\n" f"\t user: {user}\n"))
        await self._message_with_typing_lag(channel, f"welcome to the club {user}!")
        if user == self.nickname:
            await self._message_with_typing_lag(channel, f"oh oops, that's me!")
            await self._message_with_typing_lag(channel, f"lol, hi everyone")

    async def on_connect(self):
        """
        Callback called when the client has connected successfully.
        """
        self._log_self()
        await self.join(self.channel)

    def _get_typing_lag(self, message):
        """
        this equation is made to work like
        >>> message = "the quick brown fox jumped over the lazy dog"
        >>> (self.AVG_CHARS_PER_MIN) * len(message)/(random.randint(1,3))
        4.4
        >>> (self.AVG_CHARS_PER_MIN) * len(message)/(random.randint(1,3))
        1.4666666666666668
        >>> (self.AVG_CHARS_PER_MIN) * len(message)/(random.randint(1,3))
        4.4
        >>> (self.AVG_CHARS_PER_MIN) * len(message)/(random.randint(1,3))
        2.2
        """
        lag = (self.AVG_CHARS_PER_MIN) * len(message) / (random.randint(1, 3))
        lag = self.LAG_MAX if lag > self.LAG_MAX else lag
        lag = self.LAG_MIN if lag < self.LAG_MIN else lag
        return lag

    async def _message_with_typing_lag(self, target, message):
        await asyncio.sleep(self._get_typing_lag(message))
        await self.message(target, message)

    async def _do_command(self, target, source, parsed_message):
        """Do command or fallback to Rasa

        REMEMBER: every `await` must happen inside an `async`
        REMEMBER: every `async` must be `await`-ed
        """
        self._log()
        if parsed_message == "die":
            await self.die()
            return
        elif parsed_message == "usage":
            await self._message_with_typing_lag(self.channel, "I can do a lot....")
            return
        else:
            # await self._message_with_typing_lag(
            #     target, f"hmm.. let me think about that...: {parsed_message}"
            # )
            bot_responses = send_message_receive_stream(
                sender_id=source, message=parsed_message
            )
            async for res in bot_responses:  # noqa
                recipient_id = res.get("recipient_id", "")
                text = res.get("text", "")
                image = res.get("image", "")
                formatted_message = f"{recipient_id}: {text}{image}"
                await self._message_with_typing_lag(self.channel, formatted_message)
            #  TODO: if bot_responses is empty, say IDK

    async def on_message(self, target, source, message):
        """
        Callback called when the client received a message.
        """
        self._log_self(
            extra_msg=(
                f"\t target:{target}\n"
                f"\t source: {source}\n"
                f"\t message: {message}\n"
            )
        )

        if source == self.nickname:
            # my own message
            return

        # TODO: handle bot name mentioned `_they_talking_to_me`
        # TODO: call `_do_command`
        # TODO: implement memory
        # .     1. pandas
        # .     2. list
        # .     3. CSV (append only) (forgettable)
        # .     4. wait between 1-3 seconds between utterance
        # .     5. say hello.
        # .     6. usage. what do you do?
        # .     7. all the traits (like Tweety table)
        # .     8. Traits

        maybe_me, message = self._parse_me_message_pair(message)
        if self._they_talking_to_me(maybe_me, message):
            # if they're talking to me, I must parse the command.
            self._log(
                extra_msg=(
                    "\nthey talking to me\n"
                    f"\tmaybe_me: {maybe_me}\n"
                    f"\tmessage: {message}\n"
                )
            )
            await self._do_command(target, source, message)
            return
        elif self._they_talking_about_me(maybe_me, message):
            self._log(
                extra_msg=(
                    "\noooh! they talking about me! `( ͡° ͜ʖ ͡°)` \n"
                    f"\tmaybe_me: {maybe_me}\n"
                    f"\tmessage: {message}\n"
                )
            )
            self._log(
                extra_msg=(
                    f"\tsong_details: {song_details}\n"
                )
            )
            song_details = similar.similar(message)
            # Optionally we can: self._message_with_typing_lag
            await self.message(target, str(song_details))
            return
        else:
            self._log(
                extra_msg=(
                    "\nI am not the center of attention :(\n"
                    f"\tmaybe_me: {maybe_me}\n"
                    f"\tmessage: {message}\n"
                )
            )
            # send_message_receive_stream(
            #     sender_id=event.source, message="/action_hello_world"
            # )
            return


client = MyOwnBot(
    username="plato-bot", channel="#CPE582", realname="Student of Soccertees"
)
client.run(hostname="irc.freenode.net", tls=True, tls_verify=False)
