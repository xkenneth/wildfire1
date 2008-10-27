import sys
from wildfire import run
from gxml import gxml

t = gxml()

run(t.parse(sys.argv[1]))
