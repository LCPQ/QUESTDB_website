#!/usr/bin/env python3
import argparse
import json
import os
import re
import sys
from pathlib import Path
from shutil import copyfile
import crossref_commons.retrieval
parser = argparse.ArgumentParser()
parser.add_argument("--DOI",type=str,required=True)
parser.add_argument('--abstract', type=Path,help="The html abstract text file",required=False)
parser.add_argument('--picture', type=Path,help="The jpeg picture for the graphical abstact",required=False)
args=parser.parse_args()
scriptpath=Path(sys.argv[0]).resolve()
publipath=scriptpath.parents[1]/"static"/"data"/"publis"
result=crossref_commons.retrieval.get_publication_as_json(args.DOI)
mydir=publipath.joinpath(*re.split("/|\.",args.DOI))
metadata=mydir/"metadata.json"
if not mydir.exists():
  os.makedirs(str(mydir))
with open(str(metadata),"w") as f:
  json.dump(result,f, indent=2)
if args.abstract!=None:
  abstract=mydir/"abstract.html"
  copyfile(args.abstract,abstract)
if args.picture!=None:
  picture=mydir/"picture.jpeg"
  copyfile(args.picture,picture)