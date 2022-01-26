import sys
import requests
import urllib.parse

INFILE = sys.argv[1]
GNQL = open(INFILE,'r').read()

print(GNQL)