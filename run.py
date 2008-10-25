import sys
from wildfire import run
from xml.dom.minidom import parse

run(parse(sys.argv[1]))
