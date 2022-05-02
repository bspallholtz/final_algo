import datetime
def write_log(level, message):
    """A simple logger"""
    now = str(datetime.datetime.now())
    message = now + " - " + str(level) + ' - ' + str(message) + '\n'
    print(message)
    log_file = 'algo.log'
    with open(log_file, 'a+') as f:
        f.write(message)
        f.close()
    return True