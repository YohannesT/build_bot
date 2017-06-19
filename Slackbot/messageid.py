import config

def is_hi(message):
    if message is None:
        return False
    tokens = [word.lower() for word in message.strip().split()]
    return any(g in tokens for g in ['hello', 'bonjour', 'hey', 'hi', 'sup', 'morning', 'gm', 'good morning', 'hola', 'yo', 'ሰላም', 'ሀይ'])

def is_bye(message):
    if message is None:
        return False
    tokens = [word.lower() for word in message.strip().split()]
    return any(g in tokens for g in ['bye', 'goodbye', 'revoir', 'adios', 'ቻው'])

def is_help(message):
    if message is None:
        return False
    tokens = [word.lower() for word in message.strip().split()]
    return any(g in tokens for g in ['help', '--help'])

def is_build_request(message):
    if message is None:
        return False
    result = config.build_key_pattern.search(message)
    return result is not None and len(result.group()) > 0 

def is_dont_run(message):
    if message is None:
        return False
    tokens = [word.lower() for word in message.strip().split()]
    return any(g in tokens for g in ['stop', 'dont', 'don\'t', 'halt'])