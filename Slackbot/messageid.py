def is_hi(message):
    tokens = [word.lower() for word in message.strip().split()]
    return any(g in tokens for g in ['hello', 'bonjour', 'hey', 'hi', 'sup', 'morning', 'gm', 'good morning', 'hola', 'yo', 'ሰላም', 'ሀይ'])

def is_bye(message):
    tokens = [word.lower() for word in message.strip().split()]
    return any(g in tokens for g in ['bye', 'goodbye', 'revoir', 'adios', 'ቻው'])

def is_help(message):
    tokens = [word.lower() for word in message.strip().split()]
    return any(g in tokens for g in ['help', '--help'])

def is_build_request(message):
    result = build_key.search(message)
    return result is not None and len(result.group()) > 0 
