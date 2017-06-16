import os, slackclient, time, re, globals, messageid, bamboo
import random

assistant = slackclient.SlackClient(constants.token)

is_ok = assistant.api_call("users.list").get('ok')

slack_mention = '<@{name}>'.format(name = constants.bot_name)

def is_for_me(event):
    type = event.get('type')
    if type and type == 'message' and not(event.get('user') == constants.bot_id):
        if is_private(event):
            return True

        text = event.get('text')
        channel = event.get('channel')

        if slack_mention in text.strip().split():
            return true

def post_message(message, channel):
    assistant.api_call('chat.postMessage', channel=channel, text=message, as_user = True)

def is_private(event):
    return event.get('channel').startswith('D')

def get_mention(user):
    return '<@{user}>'.format(user=user);

def handle_message(message, user, channel):
    if messageid.is_hi(message):
        post_message(message='hi ' + get_mention(user), channel=channel)
    elif messageid.is_bye(message):
        post_message('bye ' + get_mention(user), channel=channel)
    elif messageid.is_build_request(message):
        post_message('building... ' + get_mention(user), channel=channel)
    else:
        post_message('http://s2.quickmeme.com/img/fd/fd8203b8ac30c066f72af14c3fab9c6256640c5046a6555ff5d90aa8e2d5fe45.jpg', channel = channel)


def run():
    if assistant.rtm_connect():
        print("assistant bot is online")
        
        while True:
            event_list = assistant.rtm_read()
            if len(event_list) > 0:
                for event in event_list:
                    print(event)
                    if is_for_me(event):
                        handle_message(event.get('text'), event.get('user'), event.get('channel'))
                    time.sleep(constants.bot_sleep_delay)
    else:
        print('assistant bot is offline')

if __name__ == '__main__':
    run()