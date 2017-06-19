import os
import slackclient
import time
import re
import config
import messageid
import bamboo
import queue
import random
import threading

""""""
my_response_is_limited = 'http://s2.quickmeme.com/img/fd/fd8203b8ac30c066f72af14c3fab9c6256640c5046a6555ff5d90aa8e2d5fe45.jpg'

assistant = None

pending_builds_queue = queue.Queue()
builds_in_progress_queue = queue.Queue()
build_requests = {}

def is_for_me(event):
    type = event.get('type')
    if type and type == 'message' and not(event.get('user') == config.bot_id):
        if is_private(event):
            return True

    return False

def am_i_mentioned(event):
    text = event.get('text')
    channel = event.get('channel')
    if text is None:
        return False

    if get_mention(config.bot_name) in text.strip().split():
        return true

    return False

def post_message(message, channel):
    assistant.api_call('chat.postMessage', channel=channel, text=message, as_user = True)

def is_private(event):
    return event.get('channel').startswith('D')

def get_mention(user):
    return '<@{user}>'.format(user=user)

def handle_message(message, user, channel):
    if messageid.is_hi(message):
        post_message(message='hi ' + get_mention(user), channel=channel)
    elif messageid.is_bye(message):
        post_message('bye ' + get_mention(user), channel=channel)
    elif messageid.is_dont_run(message):
        for d in build_requests:
            build_requests[d]['person'] = get_mention(user)
            build_requests[d]['should_run'] = False
        
        post_message(message='Ok', channel=channel)

    elif messageid.is_build_request(message):
        t = threading.Thread(name=message, target=attempt_build, args=(message, user, channel))
        build_requests.update({
                                message: {
                                            'should_run': True,
                                            'person': ''
                                        }
                            })
        t.start()
    else:
        post_message(my_response_is_limited, channel = channel)
    
should_build_go_ahead = False
time_stamp = time.time()

def attempt_build(message, user, channel):
    try:
        result = bamboo.should_i_build(message)
    except BaseException as ex:
        post_message('Hey ' + get_mention(user) + ", can't run build now.\n" + ex, channel=channel)
        return

    post_message("@channel I am about to initiate " + get_mention(user) + "'s build request. \n*If you want me to stop, MENTION ME AND TYPE STOP** You have 15 seconds", channel = channel)
    
    seconds_to_wait = 20
    while seconds_to_wait > 0:
        if build_requests.get(message) is not None:
            if not build_requests[message]['should_run']:
                post_message(build_requests[message]['person'] +  " is using the server so I can't build right now...sorry", channel=channel)
                return
        time.sleep(config.bot_sleep_delay)
    progress_token = bamboo.build(message)
    post_message("Build is queued. I will let you know when it finishes.\n" + progress_token['link'], channel= channel)

    while True:
        result = bamboo.get_build_status(progress_token['key'])
        if result['state'] == 'Successful':
            post_message("Build was successful", channel)
            break
        elif result['state'] == 'Failed':
            post_message("Build failed",  channel)
            break
        elif result['state'] == 'Stopped':
            post_message("Build was stopped", channel)
            break
        else:
            if(result['state'] != 'Unknown'):
                post_message(result['state'], channel)

        time.sleep(60)

def run():
    if assistant.rtm_connect():
        print("bot is online")
        
        while True:
            event_list = assistant.rtm_read()
            if len(event_list) > 0:
                for event in event_list:
                    print(event)
                    if is_for_me(event):
                        handle_message(event.get('text'), event.get('user'), event.get('channel'))
                    if am_i_mentioned(event):
                        if messageid.is_dont_run(event.get('message')):
                            for d in build_requests:
                                build_requests[d]['person'] = event.get('user')
                                build_requests[d]['should_run'] = False

                    time.sleep(config.bot_sleep_delay)
    else:
        print('bot is offline')
        time.sleep(10)
        run()

if __name__ == '__main__':
    if not config.initialized:
        config.init()
    
    assistant = slackclient.SlackClient(config.token)
    
    is_ok = assistant.api_call("users.list").get('ok')

    run()