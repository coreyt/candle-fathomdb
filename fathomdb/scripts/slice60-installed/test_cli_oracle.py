"""Check the revised oracle using an actual retained SDK DB and CLI diagnosis."""
import argparse
import copy
import os
import pathlib
import subprocess
import sys
import tempfile
from check_cli_database import db_facts,verify_integrity,_distinct_inputs
import json
parser=argparse.ArgumentParser();parser.add_argument('--database',required=True);parser.add_argument('--integrity',required=True);args=parser.parse_args()
facts=db_facts(args.database);report=json.loads(pathlib.Path(args.integrity).read_text());verify_integrity(report,facts)
for field,bad in [('cause','physical_erasure'),('phase','complete'),('source_id','unredacted')]:
    wrong=copy.deepcopy(report);wrong['logical']['findings'][0][field]=bad
    try:verify_integrity(wrong,facts)
    except AssertionError:pass
    else:raise AssertionError('unexpected logical finding accepted')
with tempfile.TemporaryDirectory(prefix='slice60-cli-inputs-') as folder:
    a=pathlib.Path(folder)/'a';b=pathlib.Path(folder)/'b';a.write_text('first');b.write_text('second');_distinct_inputs([a,b])
    for alias in [a,pathlib.Path(folder)/'symlink',pathlib.Path(folder)/'hardlink']:
        if alias.name=='symlink':alias.symlink_to(a)
        if alias.name=='hardlink':os.link(a,alias)
        try:_distinct_inputs([a,alias])
        except AssertionError:pass
        else:raise AssertionError('duplicate evidence input accepted')
result=subprocess.run([sys.executable,'-O',str(pathlib.Path(__file__).with_name('check_cli_database.py')),'--help'],text=True,capture_output=True,check=False)
assert result.returncode!=0 and 'optimized execution refused' in result.stderr
print('PASS actual retained-terms diagnosis/raw DB; wrong cause/phase/redaction, duplicate aliases and optimized execution refused')
