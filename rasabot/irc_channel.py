import logging
import sys
from typing import Any, Awaitable, Callable, Dict, Iterable, List, Optional, Text
import os

# pip install irc
import irc.bot
import irc.dict
import irc.strings
from irc.client import ip_numstr_to_quad, ip_quad_to_numstr
from irc.client_aio import AioSimpleIRCClient, AioReactor
import more_itertools
import itertools
import warnings

# rasa
from rasa.core.channels.channel import (
    RestInput,
    InputChannel,
    OutputChannel,
    UserMessage,
)

# sanic
from sanic import Blueprint, response
from sanic.request import Request
from sanic.response import HTTPResponse

logger = logging.getLogger(__name__)

IRC_CHANNEL = os.environ.get("RASA_IRC_CHANNEL", "#CPE582")
IRC_SERVER = os.environ.get("RASA_IRC_SERVER", "irc.freenode.net")
IRC_PORT = os.environ.get("RASA_IRC_PORT", 6667)

# class IRCBot(irc.bot.SingleServerIRCBot):
#     """
#     A bot that uses IRC to communicate.

#     Author: Joel Rosdahl <joel@rosdahl.net>
#         slight modifications by Foaad Khosmood
#         further modifications by Michael Fekadu

#     Original Source: https://github.com/jaraco/irc

#     NOTE: The SimpleIRCClient._dispatcher will seek functions named "on_<event_type>"
#         * Event Types:
#             * https://github.com/jaraco/irc/blob/1331ba85b5d093f06304d316a03a832959eaf4da/irc/events.py#L1-L201
#         * Source:
#             * https://github.com/jaraco/irc/blob/1331ba85b5d093f06304d316a03a832959eaf4da/irc/client.py#L1119
#     """

#     # # from AioSimpleIRCClient
#     # # https://github.com/jaraco/irc/blob/1331ba85b5d093f06304d316a03a832959eaf4da/irc/client_aio.py#L281-L295
#     # reactor_class = AioReactor

#     # def connect(self, *args, **kwargs):
#     #     # from AioSimpleIRCClient
#     #     # https://github.com/jaraco/irc/blob/1331ba85b5d093f06304d316a03a832959eaf4da/irc/client_aio.py#L281-L295
#     #     self.reactor.loop.run_until_complete(self.connection.connect(*args, **kwargs))

#     @classmethod
#     def name(cls) -> Text:
#         return "irc"

#     def __init__(self, channel, nickname, server, port=6667):
#         irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
#         self.channel = channel

#     def get_version(self):
#         """
#         https://github.com/jaraco/irc/blob/1331ba85b5d093f06304d316a03a832959eaf4da/irc/bot.py#L310-L315
#         """
#         logger.debug("function called: get_version...")
#         super(IRCBot, self).get_version()
#         logger.debug("completed: get_version...")

#     def die(self, msg="Bye, cruel world!"):
#         """
#         https://github.com/jaraco/irc/blob/1331ba85b5d093f06304d316a03a832959eaf4da/irc/bot.py#L288-L297
#         """
#         logger.debug("function called: die...")
#         super(IRCBot, self).die(msg=msg)
#         logger.debug("completed: die...")

#     def disconnect(self, msg="I'll be back!"):
#         """
#         https://github.com/jaraco/irc/blob/1331ba85b5d093f06304d316a03a832959eaf4da/irc/bot.py#L299-L308
#         """
#         logger.debug("function called: disconnect...")
#         super(IRCBot, self).disconnect(msg=msg)
#         logger.debug("completed: disconnect...")

#     def jump_server(self, msg="Changing servers"):
#         """
#         https://github.com/jaraco/irc/blob/1331ba85b5d093f06304d316a03a832959eaf4da/irc/bot.py#L317-L327
#         """
#         logger.debug("function called: jump_server...")
#         super(IRCBot, self).jump_server(msg=msg)
#         logger.debug("completed: jump_server...")

#     def _connect(self):
#         logger.debug("function called: _connect...")
#         super(IRCBot, self)._connect()
#         logger.debug("completed: _connect...")

#     def _on_disconnect(self, connection, event):
#         logger.debug(
#             (
#                 "function called: _on_disconnect...\n"
#                 f"connection: {connection}\n"
#                 f"event: {event}\n"
#             )
#         )
#         super(IRCBot, self)._on_disconnect(connection, event)
#         logger.debug("completed: _on_disconnect...")

#     def _on_join(self, connection, event):
#         logger.debug(
#             (
#                 "function called: _on_join...\n"
#                 f"connection: {connection}\n"
#                 f"event: {event}\n"
#             )
#         )
#         super(IRCBot, self)._on_join(connection, event)
#         logger.debug("completed: _on_join...")

#     def _on_kick(self, connection, event):
#         logger.debug(
#             (
#                 "function called: _on_kick...\n"
#                 f"connection: {connection}\n"
#                 f"event: {event}\n"
#             )
#         )
#         super(IRCBot, self)._on_kick(connection, event)
#         logger.debug("completed: _on_kick...")

#     def _on_mode(self, connection, event):
#         logger.debug(
#             (
#                 "function called: _on_mode...\n"
#                 f"connection: {connection}\n"
#                 f"event: {event}\n"
#             )
#         )
#         super(IRCBot, self)._on_mode(connection, event)
#         logger.debug("completed: _on_mode...")

#     def _on_namreply(self, connection, event):
#         logger.debug(
#             (
#                 "function called: _on_namreply...\n"
#                 f"connection: {connection}\n"
#                 f"event: {event}\n"
#             )
#         )
#         super(IRCBot, self)._on_namreply(connection, event)
#         logger.debug("completed: _on_namreply...")

#     def _on_nick(self, connection, event):
#         logger.debug(
#             (
#                 "function called: _on_nick...\n"
#                 f"connection: {connection}\n"
#                 f"event: {event}\n"
#             )
#         )
#         super(IRCBot, self)._on_nick(connection, event)
#         logger.debug("completed: _on_nick...")

#     def _on_part(self, connection, event):
#         logger.debug(
#             (
#                 "function called: _on_part...\n"
#                 f"connection: {connection}\n"
#                 f"event: {event}\n"
#             )
#         )
#         super(IRCBot, self)._on_part(connection, event)
#         logger.debug("completed: _on_part...")

#     def _on_quit(self, connection, event):
#         logger.debug(
#             (
#                 "function called: _on_quit...\n"
#                 f"connection: {connection}\n"
#                 f"event: {event}\n"
#             )
#         )
#         super(IRCBot, self)._on_quit(connection, event)
#         logger.debug("completed: _on_quit...")

#     def on_ctcp(self, connection, event):
#         """
#         https://github.com/jaraco/irc/blob/1331ba85b5d093f06304d316a03a832959eaf4da/irc/bot.py#L329-L345
#         """
#         logger.debug(
#             (
#                 "handler called: on_ctcp...\n"
#                 f"connection: {connection}\n"
#                 f"event: {event}\n"
#             )
#         )
#         super(IRCBot, self).on_ctcp(connection, event)
#         logger.debug("completed: on_ctcp...")

#     def on_dccchat(self, connection, event):
#         """
#         https://github.com/jaraco/irc/blob/1331ba85b5d093f06304d316a03a832959eaf4da/irc/bot.py#L347-L348
#         """
#         logger.debug(
#             (
#                 "handler called: on_dccchat...\n"
#                 f"connection: {connection}\n"
#                 f"event: {event}\n"
#             )
#         )
#         super(IRCBot, self).on_dccchat(connection, event)
#         logger.debug("completed: super on_dccchat...")
#         logger.debug("doing IRCBot.on_dccchat...")
#         if len(event.arguments) != 2:
#             return
#         args = event.arguments[1].split()
#         if len(args) == 4:
#             try:
#                 address = ip_numstr_to_quad(args[2])
#                 port = int(args[3])
#             except ValueError:
#                 return
#             self.dcc_connect(address, port)
#         logger.debug("compelted on_dccchat...")

#     def start(self):
#         """
#         https://github.com/jaraco/irc/blob/1331ba85b5d093f06304d316a03a832959eaf4da/irc/bot.py#L350-L353
#         """
#         logger.debug("starting bot...")
#         super(IRCBot, self).start()
#         logger.debug("started bot...")

#     def on_nicknameinuse(self, connection, event):
#         logger.debug(
#             (
#                 "handler called: on_nicknameinuse...\n"
#                 f"connection: {connection}\n"
#                 f"event: {event}\n"
#             )
#         )
#         connection.nick(connection.get_nickname() + "_")

#     def on_welcome(self, connection, event):
#         logger.debug(
#             (
#                 "handler called: on_welcome...\n"
#                 f"connection: {connection}\n"
#                 f"event: {event}\n"
#             )
#         )
#         connection.join(self.channel)

#     def on_privmsg(self, connection, event):
#         logger.debug(
#             (
#                 "handler called: on_privmsg...\n"
#                 f"connection: {connection}\n"
#                 f"event: {event}\n"
#             )
#         )
#         self.do_command(event, event.arguments[0])

#     def on_pubmsg(self, connection, event):
#         logger.debug(
#             (
#                 "handler called: on_pubmsg...\n"
#                 f"connection: {connection}\n"
#                 f"event: {event}\n"
#             )
#         )
#         a = event.arguments[0].split(":", 1)
#         if len(a) > 1 and irc.strings.lower(a[0]) == irc.strings.lower(
#             self.connection.get_nickname()
#         ):
#             self.do_command(event, a[1].strip())
#         return

#     def on_dccmsg(self, connection, event):
#         logger.debug(
#             (
#                 "handler called: on_dccmsg...\n"
#                 f"connection: {connection}\n"
#                 f"event: {event}\n"
#             )
#         )
#         # non-chat DCC messages are raw bytes; decode as text
#         text = event.arguments[0].decode("utf-8")
#         connection.privmsg("You said: " + text)

#     def do_command(self, event, command):
#         logger.debug(
#             (
#                 "function called: do_command...\n"
#                 f"command: {command}\n"
#                 f"event: {event}\n"
#             )
#         )
#         nick = event.source.nick
#         c = self.connection

#         if command == "disconnect":
#             self.disconnect()
#         elif command == "die":
#             self.die()
#         elif command == "stats":
#             for chname, chobj in self.channels.items():
#                 c.notice(nick, "--- Channel statistics ---")
#                 c.notice(nick, "Channel: " + chname)
#                 users = sorted(chobj.users())
#                 c.notice(nick, "Users: " + ", ".join(users))
#                 opers = sorted(chobj.opers())
#                 c.notice(nick, "Opers: " + ", ".join(opers))
#                 voiced = sorted(chobj.voiced())
#                 c.notice(nick, "Voiced: " + ", ".join(voiced))
#         elif command == "dcc":
#             dcc = self.dcc_listen()
#             c.ctcp(
#                 "DCC",
#                 nick,
#                 "CHAT chat %s %d"
#                 % (ip_quad_to_numstr(dcc.localaddress), dcc.localport),
#             )
#         elif command == "hello":  # Foaad: change this
#             c.privmsg(self.channel, "well double hello to you too!")
#         elif command == "about":  # Foaad: add your name
#             c.privmsg(
#                 self.channel,
#                 "I was made by Dr. Foaad Khosmood for the CPE 466 class in Spring 2016. I was furthere modified by _____",
#             )
#         elif command == "usage":
#             # Foaad: change this
#             c.privmsg(self.channel, "I can answer questions like this: ....")
#         else:
#             c.notice(nick, "Not understood: " + command)


# class IRCBlueprint(Blueprint):
#     """A custom IRC (internet relay chat) blueprint."""

#     def __init__(self, *args, **kwargs):
#         # sio: AsyncServer, socketio_path,
#         # self.sio = sio
#         # self.socketio_path = socketio_path
#         super().__init__(*args, **kwargs)

#     def register(self, app, options) -> None:
#         # self.sio.attach(app, self.socketio_path)
#         super().register(app, options)


class IRCInput(RestInput):
    """
    A custom IRC (internet relay chat) input channel.

    Inheriting RestInput gives us
        the required `blueprint(...)` for the `/webhooks/irc/webhook`
        https://github.com/RasaHQ/rasa/blob/cb25c31e2c6c3c36c768f2d4b442cd4cb6d1928c/rasa/core/channels/channel.py#L447-L500
    """

    @classmethod
    def name(cls) -> Text:
        return "irc"

    def __init__(
        self, nickname, channel=IRC_CHANNEL, server=IRC_SERVER, port=IRC_PORT,
    ):
        """
        Creates an IRC (internet relay chat) InputChannel.

        TODO: consider generating random nicknames

        Args:
            nickname: the name of the bot
            channel: the IRC channel to conenct to (default: rasa)
            server: the IRC server to connect to (default: irc.freenode.net)
            port: the port to use for IRC server
                (e.g. irc.freenode.net:<PORT>) (default: 6667).
        """
        self.channel = channel
        self.nickname = nickname
        self.server = server
        self.port = port or IRC_PORT
        # # FIXME: client instead of bot
        # self.bot = IRCBot(
        #     channel=self.channel,
        #     nickname=self.nickname,
        #     server=self.server,
        #     port=self.port,
        # )
        # # self.client =
        logger.info(
            (
                "initialized IRCInput with:\n"
                f"self.nickname = {self.nickname}\n"
                f"self.channel = {self.channel}\n"
                f"self.server = {self.server}\n"
                f"self.port = {self.port}\n"
                # f"self.client = {self.client}\n"
                # f"self.bot = {self.bot}\n"
            )
        )
        # # # TODO: reimplement using async client from irc package
        # # #       https://github.com/jaraco/irc
        # self.bot.start()
        # print("REACH THIS LINE OF CODE!!!!!!!!!!!!!!!!!!!!!!!!!!!")

    @classmethod
    def from_credentials(cls, credentials: Optional[Dict[Text, Any]]) -> InputChannel:
        """Return IRCInput initalized with the given input from the credentials.yml."""
        if not credentials:
            cls.raise_missing_credentials_exception()

        # pytype: disable=attribute-error
        return cls(
            channel=credentials.get("channel"),
            nickname=credentials.get("nickname"),
            server=credentials.get("server"),
            port=credentials.get("port") or IRC_PORT,
        )
        # pytype: enable=attribute-error

    # def blueprint(
    #     self, on_new_message: Callable[[UserMessage], Awaitable[Any]]
    # ) -> Blueprint:
    #     """Defines a Sanic blueprint.
    #     The blueprint will be attached to a running sanic server and handle
    #     incoming routes it registered for."""
    #     irc_webhook = IRCBlueprint("irc_webhook", __name__)

    #     @irc_webhook.route("/", methods=["GET"])
    #     async def health(_: Request) -> HTTPResponse:
    #         return response.json({"status": "ok"})

    #     @irc_webhook.route("/webhook", methods=["POST"])
    #     async def webhook(request: Request) -> HTTPResponse:
    #         """Respond to inbound webhook HTTP POST from IRC."""

    #         logger.debug("Received irc webhook call")
    #         # Get the POST data sent from Webex Teams
    #         json_data = request.json

    #         return response.text("received : {}".format(str(json_data)))

    #     return irc_webhook

    def get_output_channel(self) -> OutputChannel:
        logger.debug("called `get_output_channel`...")
        return None
