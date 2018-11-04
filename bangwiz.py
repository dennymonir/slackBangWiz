import logging
import time
from rtmbot.core import Plugin

from memedict import search

from bang.auth import (USERS_TOKENS, BOT_TOKEN)

logging.basicConfig(filename='rtmbotf.log',
                    format='%(asctime)s %(message)s')


class BangPlugin(Plugin):
    """Bang !shortcuts for slack.
    """

    def process_message(self, data):
        if 'text' in data:
            tokens = data['text'].split(' ')
            command = tokens[0]
            data['text'] = ' '.join(tokens[1:])
            if command == '!b':
                self._bomb(data)
            if command == '!k':
                self._kaomoji(data)
            elif command == '!kym':
                self._kym(data)
            elif command == '!h':
                self._help(data)

    def delete_line(self, data):
        # Delete command
        self.slack_client.api_call("chat.delete",
            token=USERS_TOKENS.get(data['user'], BOT_TOKEN),
            channel=data['channel'], ts=data['ts'], as_user=True)

    def react(self, data, emoji):
        return self.slack_client.api_call("reactions.add",
            token=BOT_TOKEN, as_user=False, name=emoji, icon_emoji=':slack-cli:',
            channel=data['channel'], timestamp=data['ts'])


    # Commands below

    def _help(self, data):
        """!h: show this help message.
        """
        commands = [x for x in dir(self) if x.startswith('_') and not x.startswith('__')]
        usage = ''.join([getattr(self, cmd).__doc__ for cmd in sorted(commands)])
        self.slack_client.api_call("chat.postMessage", icon_emoji=':bangbang:',
            token=BOT_TOKEN, as_user=False,
            username='Bang',
            text=usage,
            channel=data['user'])

    def _bomb(self, data):
        """!b: destruct message after 10 seconds.
        """
        self.delete_line(data)
        self.slack_client.api_call("chat.postMessage",
            token=USERS_TOKENS.get(data['user'], BOT_TOKEN),
            as_user=True, text=':bomb: %s' % data['text'][3:], channel=data['channel'])
        time.sleep(7)
        res = self.react(data, 'three')
        time.sleep(1)
        self.react(data, 'two')
        time.sleep(1)
        self.react(data, 'one')
        time.sleep(1)
        self.react(data, 'fire')
        self.delete_line(data)

    def _kaomoji(self, data):
        """!k: replace emoji with kaomoji.
        """
        from bang.rsrc.kaomoji import KAOMOJIS

        if data['text'] in KAOMOJIS:
            self.delete_line(data)
            self.slack_client.api_call("chat.postMessage",
                token=USERS_TOKENS.get(data['user'], BOT_TOKEN),
                as_user=True, text=KAOMOJIS[data['text']], channel=data['channel'])

    def _kym(self, data):
        """!kym: print description of given emoji.
        """
        emoji = data['text'].split(':')[1]
        term = ' '.join(emoji.split('_'))
        description = search(term)
        self.slack_client.api_call("chat.postMessage", icon_emoji=':%s:' % emoji,
            token=BOT_TOKEN, as_user=False,
            username=description.split('.')[0],
            text='.'.join(description.split('.')[1:]),
            channel=data['user'])