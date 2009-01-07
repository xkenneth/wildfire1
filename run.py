import sys
import os
from wildfire import run

#NOT USELESS!
sys.path.append(os.getcwd())

#I'm sure we'll have more options later, but this will do for now
try:
    run(sys.argv[1])
except IndexError:
    print "You didn't specify a WFX file!"
