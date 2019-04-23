import random
from collections import Counter
import logging

class Logging(object):

    def debuglog(self, msg):
        self.logger.debug(msg)
    def infolog(self, msg):
        self.logger.info(msg)
    def warninglog(self, msg):
        self.logger.warning(msg)
    def errorlog(self, msg):
        self.logger.error(msg)
    def criticallog(self, msg):
        self.logger.critical(msg)

    def __init__(self, name, level=logging.ERROR, file=None, format=None):
        self.logger = logging.getLogger(name)
        handler = None
        if not file == None:
           handler = logging.FileHandler(file)
        else:
           handler = logging.StreamHandler()
        handler.setLevel(level)
        if format == None:
            format = '[%(process0d] %(asctime)s) - %(message)s'
        handler.setFormatter(format)
        self.logger.addHandler(handler)

def bimodal(low1, high1, mode1, low2, high2, mode2):
#coin flip between the low range and the high range, then
#return a random floating point number N such that low <= N <= high and with the specified mode between 
#those bounds. 
#The low and high bounds default to zero and one. 
#The mode argument defaults to the midpoint between the bounds, giving a symmetric distribution.
    toss = random.choice((1, 2))
    if toss == 1:
        return random.triangular(low1, high1, mode1)
    else:
        return random.triangular(low2, high2, mode2)


def is_float(input):
    try:
        num = float(input)
    except ValueError:
        return False
    return True


