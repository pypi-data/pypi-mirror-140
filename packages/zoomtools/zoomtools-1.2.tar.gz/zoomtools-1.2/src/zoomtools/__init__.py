import re

def smart_int(value):
    result = ""
    i = 0
    for a in str(value):
        if i == 0 and a == '+' or a == '-' or a == ".": result += a
        if a.isdigit(): result += a
        i += 1
    return int(result) if result else 0
    
def int_input(text): return smart_int(input(text))

def safe(func):

    try: return func()
    except Exception as err: return err
    
class InvalidMode: pass

def date_parse(seconds, mode="string"):
    days = int(seconds//86400)
    hours = int((seconds-days*86400)//(60*60))
    minutes = int((seconds - (days*86400 + hours*60*60))//60)
    seconds = int((seconds - (days*86400 + hours*60*60 + minutes*60))//60)
    days = ("0" if days < 9 else "") + str(days)
    hours = ("0" if hours < 9 else "") + str(hours)
    minutes = ("0" if minutes <= 9 else "") + str(minutes)
    seconds = ("0" if seconds < 9 else "") + str(seconds)
    if mode == "string": return "%s:%s:%s:%s" % (days, hours, minutes, seconds)
    elif mode == "list": return [days, hours, minutes, seconds]
    elif mode == "tuple": return (days, hours, minutes, seconds)
    else: raise InvalidMode("Invalid date_parse result mode (string/list/tuple), not %s" % mode)
    
def value_parse(text, mode=1):
    numbers_values={"Qa": 10**18, "Qu": 10**15, "T": 10**12, "B": 10**9, "M": 10**6, "K": 10**3}
    if mode == 1: return re.sub(r'\d(?=(?:\d{3})+(?!\d))', r'\g<0> ', str(text))
    elif mode == 2: 
        for i in numbers_values:
            if smart_int(text) >= numbers_values[i]: return str(round(smart_int(text) / numbers_values[i], 1)) + i
        return text
    else: raise InvalidMode("Invalid value_parse result mode (1-2), not %s" % mode)