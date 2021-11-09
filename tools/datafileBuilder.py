#!/usr/bin/env python3
import sys
import re
from enum import IntEnum,auto,unique
import numpy as np
from pathlib import Path
from lib import LaTeX,formats,dfbOptions
from lib.formats import getFormatHandlers
from TexSoup import TexSoup,TexNode,TexCmd,TexEnv
from lib.data import dataFileBase,DataType,state
from collections import defaultdict
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--file', type=argparse.FileType('r'))
parser.add_argument("--list","-l",action="store_true", help='List all available format')
parser.add_argument('--debug', action='store_true', help='Debug mode')
args = parser.parse_args()
if args.list:
  print("The list of avalable formats are:")
  for formatName,_ in getFormatHandlers():
    print(formatName)
elif args.file!=None:
  lines=args.file.readlines()
  soup=TexSoup(lines)
  opt=soup.dfbOptions
  if type(opt) is TexNode and type(opt.expr) is TexEnv:
    texOps=dfbOptions.readFromEnv(opt)
  else:
    texOps=dfbOptions()
  commands=[LaTeX.newCommand(cmd) for cmd in soup.find_all("newcommand")]
  dat=LaTeX.tabularToData(soup.tabular,commands,texOps.excludeColumns)
  scriptpath=Path(sys.argv[0]).resolve()
  datapath=scriptpath.parents[1]/"static"/"data"
  if args.debug:
    datapath=datapath/"test"
  if not datapath.exists():
    datapath.mkdir()
  datalst=dataFileBase.readFromTable(dat,texOps,commands=commands)
  for data in datalst:
    data.toFile(datapath,texOps.suffix)
else:
  parser.print_help()