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

import srl

import requests

import spacy

# predictor = srl.get_predictor()

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
    logging.warning(
        "No rasa? That is okay!!! rasa is a large package to install anyway."
    )
    DEFAULT_SERVER_URL = "http://localhost:5005"
    # DEFAULT_SERVER_URL = "https://582rasa.onrender.com"
    DEFAULT_ENCODING = "utf-8"
    INTENT_MESSAGE_PREFIX = "/"

# TODO: use something similar os.path.join to avoid any bugginess with forgetting "/" before the path
DEFAULT_WEBHOOK_PATH = "/webhooks/rest/webhook"
IRC_WEBHOOK_BASE_URL = os.environ.get("RASA_IRC_WEBHOOK_BASE_URL", DEFAULT_SERVER_URL)
IRC_WEBHOOK_PATH = os.environ.get("RASA_IRC_WEBHOOK_PATH", DEFAULT_WEBHOOK_PATH)
IRC_CHANNEL = os.environ.get("RASA_IRC_CHANNEL", "#CPE582")
IRC_SERVER = os.environ.get("RASA_IRC_SERVER", "irc.freenode.net")
IRC_PORT = os.environ.get("RASA_IRC_PORT", 6667)
STREAM_READING_TIMEOUT_ENV = "RASA_SHELL_STREAM_READING_TIMEOUT_IN_SECONDS"
DEFAULT_STREAM_READING_TIMEOUT_IN_SECONDS = 10

ELASTIC_SEARCH_BASE_URL = os.environ.get(
    "ELASTIC_SEARCH_BASE_URL", "http://localhost:9200"
)
ELASTIC_SEARCH_INDEX_PATH = os.environ.get("ELASTIC_SEARCH_INDEX_PATH", "/memory")

logging.warning(f"DEFAULT_WEBHOOK_PATH: {DEFAULT_WEBHOOK_PATH}")
logging.warning(f"IRC_WEBHOOK_BASE_URL: {IRC_WEBHOOK_BASE_URL}")
logging.warning(f"IRC_WEBHOOK_PATH: {IRC_WEBHOOK_PATH}")
logging.warning(f"IRC_CHANNEL: {IRC_CHANNEL}")
logging.warning(f"IRC_SERVER: {IRC_SERVER}")
logging.warning(f"IRC_PORT: {IRC_PORT}")
logging.warning(f"STREAM_READING_TIMEOUT_ENV: {STREAM_READING_TIMEOUT_ENV}")
logging.warning(
    f"DEFAULT_STREAM_READING_TIMEOUT_IN_SECONDS: {DEFAULT_STREAM_READING_TIMEOUT_IN_SECONDS}"
)
logging.warning(f"ELASTIC_SEARCH_BASE_URL: {ELASTIC_SEARCH_BASE_URL}")
logging.warning(f"ELASTIC_SEARCH_INDEX_PATH: {ELASTIC_SEARCH_INDEX_PATH}")

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


async def forget_memory(
    server_url=ELASTIC_SEARCH_BASE_URL,
    index_path=ELASTIC_SEARCH_INDEX_PATH,
    raise_for_status=False,
):
    """
    DELETE memory
    """
    # example url : "http://localhost:9200/memory"
    url = f"{server_url}{index_path}"

    # Define timeout to not keep reading in case the server crashed in between
    timeout = _get_stream_reading_timeout()

    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.delete(url, raise_for_status=raise_for_status) as resp:
            logger.info(f"called forget_memory and got resp.status = {resp.status}")


def initialize_memory(
    server_url=ELASTIC_SEARCH_BASE_URL,
    index_path=ELASTIC_SEARCH_INDEX_PATH,
    raise_for_status=True,
):
    """
    # create memory
    PUT memory

    # set mappings
    PUT memory/_mappings
    {
        "properties" : {
            "sender" : {
            "type" : "text",
            "fields" : {
                "keyword" : {
                "type" : "keyword",
                "ignore_above" : 256
                }
            }
            },
            "message" : {
            "type" : "text"
            }
        }
    }
    """
    payload = {
        "properties": {
            "sender": {
                "type": "text",
                "fields": {"keyword": {"type": "keyword", "ignore_above": 256}},
            },
            "message": {"type": "text"},
        }
    }

    # example url : "http://localhost:9200/memory"
    url = f"{server_url}{index_path}"

    # Define timeout to not keep reading in case the server crashed in between
    timeout = _get_stream_reading_timeout()

    # forget first??
    # requests_retry_session(retries=100).delete('http://localhost:9200/memory')

    # create the memory index
    requests_retry_session(retries=100).put(url)

    # https://docs.aiohttp.org/en/stable/client_reference.html#aiohttp.ClientSession
    # default timeout is 5min
    # async with aiohttp.ClientSession(timeout=None) as session:
    #     async with session.put(url, raise_for_status=raise_for_status) as resp:
    #         async for line in resp.content:
    #             if line:
    #                 yield json.loads(line.decode(DEFAULT_ENCODING))

    # example url : "http://localhost:9200/memory/_mappings"
    url = f"{url}/_mappings"

    # define the mapping types
    requests_retry_session(retries=100).put(url, json=payload)

    # async with aiohttp.ClientSession(timeout=timeout) as session:
    #     async with session.put(url, json=payload, raise_for_status=True) as resp:
    #         async for line in resp.content:
    #             if line:
    #                 yield json.loads(line.decode(DEFAULT_ENCODING))


import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


def requests_retry_session(
    retries=100,
    # after 100, that's definitely something wrong.
    backoff_factor=0.3,
    status_forcelist=(500, 502, 504),
    session=None,
):
    """
    Source:
        https://www.peterbe.com/plog/best-practice-with-retries-with-requests
    """
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


async def save_to_memory(
    sender,
    message,
    server_url=ELASTIC_SEARCH_BASE_URL,
    index_path=ELASTIC_SEARCH_INDEX_PATH,
    raise_for_status=False,
):
    """
    ## add a new thing into the memory index
    # remember something
    POST /memory/_doc
    {
        "sender" : "plato",
        "message" : "I am plato"
    }
    """
    payload = {
        "sender": sender,
        "message": message,
    }

    # example url : "http://localhost:9200/memory"
    url = f"{server_url}{index_path}/_doc"

    # Define timeout to not keep reading in case the server crashed in between
    timeout = _get_stream_reading_timeout()

    # create the memory
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.post(
            url, json=payload, raise_for_status=raise_for_status
        ) as resp:
            async for line in resp.content:
                if line:
                    yield json.loads(line.decode(DEFAULT_ENCODING))


async def get_from_memory(
    message,
    server_url=ELASTIC_SEARCH_BASE_URL,
    index_path=ELASTIC_SEARCH_INDEX_PATH,
    raise_for_status=False,
):
    """
    # How to query the elastic search memory
    ## notice the text search
    GET /memory/_search
    {
        "query": {
            "simple_query_string": {
                "query": "plato am i",
                "fields": []  # by default searches on all fields.
            }
        }
    }

    result will be
    {
        ...
        "hits" : {
            "total" : { "value" : 5, "relation" : "eq" },
            "max_score" : 1.6421977,
            "hits" : [
                {
                    "_index" : "memory",
                    "_type" : "_doc",
                    "_id" : "HUlMhnIBk76dIaGSq-DW",
                    "_score" : 1.6421977,
                    "_source" : {
                    "sender" : "plato",
                    "message" : "I am plato"
                    }
                },
                { ... },
                { ... },
            ]
        }
    }
    """
    payload = {
        "query": {
            "simple_query_string": {
                "query": message,
                "fields": [],  # by default searches on all fields.
            }
        }
    }

    # example url : "http://localhost:9200/memory"
    url = f"{server_url}{index_path}/_search"

    # Define timeout to not keep reading in case the server crashed in between
    timeout = _get_stream_reading_timeout()

    # create the memory
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(
            url, json=payload, raise_for_status=raise_for_status
        ) as resp:
            async for line in resp.content:
                if line:
                    yield json.loads(line.decode(DEFAULT_ENCODING))


MEMORY_COLUMNS = [
    "target",
    "channel",
    "username",
    "nickname",
    "by",
    "kicker",
    "_they_talking_to_me",
    "_they_talking_about_me",
    "function",
    "maybe_me",
    "message",
    srl.SRL_TAGS.VERB,
    srl.SRL_TAGS.AGENT,
    srl.SRL_TAGS.PATIENT,
    srl.SRL_TAGS.TEMPORAL,
    srl.SRL_TAGS.ARGM_LOC,  # location
]


class RHETORICAL_REPLY_STATE(Enum):
    DO_NOT_WAIT = 1
    WAITING_FOR_USER_REPLY = 2


class IRCBot(pydle.Client):
    SPAM_BUFFER_SIZE = 5  # elements in list
    SPAM_LIMIT = 5  # seconds
    LAG_MAX = 3  # foaad said 3 second delay max
    LAG_MIN = 1  # foaad said 1 second delay min
    ADJUST_ACPM = 1
    SPAM_BUFFER = []
    FRUSTRATION_LIMIT = 30  # seconds

    def __init__(self, username, channel, **kwargs):
        super(IRCBot, self).__init__(username, **kwargs)
        self.channel = channel
        self.username = username
        self.AVG_CHARS_PER_MIN = AVG_CHARS_PER_MIN * self.ADJUST_ACPM
        self._log_self(is_init=True, info=True)
        self.cached_song_details = None
        self.nlp = spacy.load("en_core_web_sm")
        initialize_memory()
        self.rh = None
        self.rh_answer = None
        self.rhetorical_reply_state = RHETORICAL_REPLY_STATE.DO_NOT_WAIT
        self.started_waiting = time.time()

    def _remember(self, data: dict):
        pass

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
                f"\t\n self.channel: {self.channel}\n"
                f"\t self.username: {self.username}\n"
                f"\t self.nickname: {self.nickname}\n"
                f"\t self.SPAM_BUFFER_SIZE: {self.SPAM_BUFFER_SIZE}\n"
                f"\t self.SPAM_LIMIT: {self.SPAM_LIMIT}\n"
                f"\t self.SPAM_BUFFER: {self.SPAM_BUFFER}\n"
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

    async def _users(self, target):
        reply = f"{str(self.users)}"
        await self._message_with_typing_lag(target, reply)

    async def _message_list_with_lag(self, target, msgs=[]):
        for msg in msgs:
            await self._message_with_typing_lag(target, msg)

    async def _usage(self, target, message):
        await self._message_with_typing_lag(self.channel, "I can do a lot....")
        commands = (
            "These are my commands:\n",
            "\t usage -- this message \n",
            "\t die -- I will end my process \n",
            "\t forget -- I will nuke my brain cells \n",
            "\t remember -- I will recite back to you from my memory (e.g. 'do you remember the 5th of november?')",
        )
        fun_things = (
            "These are the fun things I do:\n",
            "\t 🎶🎶 sometimes I siiing 🎶🎵 \n",
            "\t I try my best to remember stuff from the chat \n",
        )
        description = (
            "Character description:\n",
            "\t I am obsessed with Poetry and frequently sings to the extent that irritates you.\n",
            "\t I like to show off about the things I know and pose rhetorical questions.\n",
            "\t I follow musical bands and I update myself with the songs, artists and other information about the band.\n",
            "\t Me being shy does not stop me from singing excessively\n",
        )
        usage_replies = [*commands, "\n", *fun_things, "\n", *description]
        await self._message_list_with_lag(target, msgs=usage_replies)

    async def _forget(self, msgs=[]):
        """
        """
        if msgs == []:
            msgs = [
                "okay, I'll start destroying my brain cells...",
                "...",
                "...",
                "who are you?",
            ]
        for msg in msgs:
            await self._message_with_typing_lag(self.channel, msg)
            # TODO: consider a smart check here, rather than ignoring resp.status on each call
            await forget_memory(raise_for_status=False)

    async def _die(self, msgs=[]):
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
            await self._message_with_typing_lag(channel, f"by the way I type slow, so please be patient...")

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
        self._log_self(
            extra_msg=(
                f"\t target:{target}\n"
                f"\t source: {source}\n"
                f"\t parsed_message: {parsed_message}\n"
            )
        )
        if parsed_message == "die":
            await self._die()
            return
        elif parsed_message == "users":
            await self._users(target)
            return
        elif parsed_message == "usage":
            await self._usage(target, parsed_message)
            return
        elif parsed_message == "forget":
            await self._forget()
            return
        elif "remember" in parsed_message:
            parsed_message = parsed_message.replace("remember", "").strip()
            memory_results = get_from_memory(f"{source} {parsed_message}")
            default_dunder_source = {
                "sender": "um who was it?",
                "message": "actually I don't recall",
            }
            default_top_hit = {"_source": default_dunder_source}
            async for res in memory_results:  # noqa
                hits = res.get("hits", {"hits": {"no_hits": "nothing"}}).get(
                    "hits", [default_top_hit, default_top_hit]
                )
                self._log(
                    extra_msg=(
                        f"res: {res}" f"hits: {hits}" f"type(hits): {type(hits)}"
                    )
                )
                # first hit is always the most recent message
                # second hit is the most relevant after that one
                for hit, i in zip(hits, [1, 2, 3]):
                    top_hit = hit.get("_source", default_dunder_source)
                    top_hit_sender = top_hit["sender"]
                    top_hit_message = top_hit["message"]
                    await self.message(
                        target,
                        f'I remember when {top_hit_sender} said, "{top_hit_message}"',
                    )
            return
        elif parsed_message == "memory_dump":
            # TODO: just straight up dump all of the memory
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

    async def _reply_song_details(self, target, message):
        self._log_self(
            extra_msg=(
                "\n _reply_song_details \n"
                f"\t target: {target}\n"
                f"\t message: {message}\n"
                f"\t self.cached_song_details: {self.cached_song_details}\n"
            )
        )
        if self.cached_song_details is None:
            await self._message_with_typing_lag(target, "...")
            await self._message_with_typing_lag(target, message)
            await self._message_with_typing_lag(target, "i am mocking you 🙃😊")

        # if I have ever sang a song, then give some details
        song_details = self.cached_song_details
        song = song_details["song"]
        artist = song_details["artist"]
        genre = song_details["genre"]
        year = song_details["year"]
        song_detail_message = (
            "Here's the details of the song I last sang:\n"
            f"\t song: {song}\n"
            f"\t artist: {artist}\n"
            f"\t genre: {genre}\n"
            f"\t year: {year}\n"
        )
        await self.message(target, song_detail_message)

    async def _rhetorically_reply_song_details(self, target, message):
        self._log_self(
            extra_msg=(
                "\n _rhetorically_reply_song_details \n"
                f"\t target: {target}\n"
                f"\t message: {message}\n"
                f"\t self.cached_song_details: {self.cached_song_details}\n"
            )
        )
        if self.cached_song_details is None:
            await self._message_with_typing_lag(target, "...")
            await self._message_with_typing_lag(target, message)
            await self._message_with_typing_lag(target, "i am mocking you 🙃😊")
            return

        # reply_format = "The {} of that song was {}"
        song_details = self.cached_song_details
        song = song_details["song"]
        artist = song_details["artist"]
        genre = song_details["genre"]
        year = song_details["year"]

        if "year" in message or 'when' in message:
            song_detail_message = "This song was released in the year {}".format(year)

        elif "artist" in message or 'who' in message:
            song_detail_message = "The artist of this song was {}".format(artist)

        elif "genre" in message:
            song_detail_message = "This song is of {} genre".format(genre)

        elif 'what are you singing' in message:
            song_detail_message = "The name of this song is {}".format(song)

        elif 'is that a song' in message or 'are you singing' in message or 'were you singing':
            song_detail_message = "Yes I sing songs :)"

        else:
            song_detail_message = "The name of this song is {}".format(song)

        await self.message(target, song_detail_message)
        self.rh = similar.rhetoric(self.cached_song_details)
        self.rh_question = random.choice(list(self.rh.keys()))
        self.rh_answer = self.rh.get(self.rh_question)
        await self._message_with_typing_lag(target, self.rh_question)
        self._transition_rhetorical_state(start_waiting=True)

    def _has_question(self, message):
        self._log_self(extra_msg=(f"\n _has_question \n" f"\t message: {message}\n"))
        doc = self.nlp(message)
        for token in doc:
            if token.tag_ in ["WDT", "WP", "WP$", "WRB"]:
                return True
            elif 'is that a song' or 'are you singing' or 'were you singing' in message:
                return True

    def _has_song_keywords(self, message):
        self._log_self(
            extra_msg=(f"\n _has_song_keywords \n" f"\t message: {message}\n")
        )
        keywords = [
            "song",
            "year",
            "artist",
            "genre",
            "singer",
            "band",
            "sung",
            "album",
            'singing'
        ]
        return any([k in message for k in keywords])

    def _get_music_emoji_string(self):
        music_emojis = "🎸🎹🎺🎻🎼🪕🎷🥁🎧🎤🎶🎵"
        return "".join([random.choice(music_emojis) for i in [1, 2, 3]])

    def _is_followup_question(self, message):
        """
        Return True if the given message is a query about a previously sung song.
        Else False.
        """
        self._log_self(
            extra_msg=(f"\n _is_followup_question \n" f"\t message: {message}\n")
        )
        has_question = self._has_question(message)
        has_song_keywords = self._has_song_keywords(message)
        has_cached_song_details = self.cached_song_details is not None
        self._log(
            extra_msg=(
                f"\n _is_followup_question \n"
                f"\t has_question: {has_question}\n"
                f"\t has_song_keywords: {has_song_keywords}\n"
                f"\t has_cached_song_details: {has_cached_song_details}\n"
            )
        )
        return has_question and has_song_keywords and has_cached_song_details

    async def _sing(self, target, message):
        """
        Find a similar song, and start singing.
        """
        self._log_self(extra_msg=(f"\t target:{target}\n" f"\t message: {message}\n"))
        # dict_keys(['song', 'lyrics', 'artist', 'genre', 'year', 'output'])
        song_details = similar.similar(message)
        self.cached_song_details = song_details
        song = song_details["song"]
        artist = song_details["artist"]
        genre = song_details["genre"]
        year = song_details["year"]
        output = song_details["output"]
        self._log(
            extra_msg=(
                f"\t song: {song}\n"
                f"\t artist: {artist}\n"
                f"\t genre: {genre}\n"
                f"\t year: {year}\n"
                f"\t output: {output}\n"
            )
        )
        for o in output:
            music_emojis = self._get_music_emoji_string()
            await self._message_with_typing_lag(target, music_emojis)
            await self._message_with_typing_lag(target, o)

        music_emojis = self._get_music_emoji_string()
        await self._message_with_typing_lag(target, music_emojis)

    def _transition_rhetorical_state(
        self, got_reply=False, start_waiting=False
    ) -> RHETORICAL_REPLY_STATE:
        """
        always return the next state if transitioned?
        """
        prev_state = self.rhetorical_reply_state

        now = time.time()
        time_elapsed = now - self.started_waiting
        im_bored = time_elapsed > self.FRUSTRATION_LIMIT

        if prev_state == RHETORICAL_REPLY_STATE.DO_NOT_WAIT and start_waiting:
            """
            DO_NOT_WAIT -> WAITING_FOR_USER_REPLY
            """
            self.rhetorical_reply_state = RHETORICAL_REPLY_STATE.WAITING_FOR_USER_REPLY
            self.started_waiting = time.time()
            return self.rhetorical_reply_state

        if prev_state == RHETORICAL_REPLY_STATE.WAITING_FOR_USER_REPLY and (
            got_reply or im_bored
        ):
            """
            WAITING_FOR_USER_REPLY -> DO_NOT_WAIT
            """
            self.rhetorical_reply_state = RHETORICAL_REPLY_STATE.DO_NOT_WAIT
            return self.rhetorical_reply_state

    async def _handle_talking_to_me(self, target, source, maybe_me, message):
        self._log_self(
            extra_msg=(
                f"\t target:{target}\n"
                f"\t source: {source}\n"
                f"\t maybe_me: {maybe_me}\n"
                f"\t message: {message}\n"
            )
        )

        if self._is_followup_question(message):
            self._log(
                extra_msg=(
                    "\n _is_followup_question is true \n"
                    f"\t maybe_me: {maybe_me}\n"
                    f"\t message: {message}\n"
                    f"\t self.cached_song_details: {self.cached_song_details}\n"
                )
            )
            await self._rhetorically_reply_song_details(target, message)
        else:
            await self._do_command(target, source, message)

        return

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

        maybe_me, message = self._parse_me_message_pair(message)

        elastic_responses = save_to_memory(sender=source, message=message)

        async for res in elastic_responses:  # noqa
            self._log(extra_msg=(f"res: {res}"))

        if (
            self._transition_rhetorical_state(
                got_reply=self._they_talking_to_me(maybe_me, message)
            )
            == RHETORICAL_REPLY_STATE.DO_NOT_WAIT
        ):
            await self._message_with_typing_lag(
                target, f"yeaah..well... it's {self.rh_answer}"
            )
            return

        if self._they_talking_to_me(maybe_me, message):
            # if they're talking to me, I must parse the command.
            self._log(
                extra_msg=(
                    "\nthey talking to me\n"
                    f"\tmaybe_me: {maybe_me}\n"
                    f"\tmessage: {message}\n"
                )
            )
            await self._handle_talking_to_me(target, source, maybe_me, message)
        elif self._they_talking_about_me(maybe_me, message):
            self._log(
                extra_msg=(
                    "\noooh! they talking about me! `( ͡° ͜ʖ ͡°)` \n"
                    f"\tmaybe_me: {maybe_me}\n"
                    f"\tmessage: {message}\n"
                )
            )
            await self._message_with_typing_lag(
                target=target,
                message="💭 hmm... are they talking about me? should I interrupt? 💭",
            )
            return
        else:
            self._log(
                extra_msg=(
                    "\nI am not the center of attention :(\n"
                    f"\tmaybe_me: {maybe_me}\n"
                    f"\tmessage: {message}\n"
                )
            )
            await self._sing(target, message)
            return


if __name__ == "__main__":
    client = IRCBot(
        username="shy-bot", channel="#CPE582", realname="Student of Soccertees"
    )
    client.run(hostname="irc.freenode.net", tls=True, tls_verify=False)
