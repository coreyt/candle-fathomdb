"""Compare real CLI reports with the authored SDK DB and its native debt state."""
if not __debug__:
    raise RuntimeError('qualification requires assertions enabled; optimized execution refused')
import argparse
from contextlib import closing
import hashlib
import json
import pathlib
import sqlite3

NAMES=['canonical_nodes','canonical_edges','operational_collections','operational_mutations','operational_state']
ROWS=[('coordinate-france','France has its capital in Paris.'),('coordinate-paris','Paris is the capital of France.')]


def db_facts(database):
    """Read the closed qualification DB; refuse WAL, unexpected debt or row drift."""
    db=pathlib.Path(database).resolve();assert db.is_file()
    wal=pathlib.Path(str(db)+'-wal');assert not wal.exists() or wal.stat().st_size==0,'do not ignore live WAL frames'
    with closing(sqlite3.connect(db.as_uri()+'?mode=ro&immutable=1',uri=True)) as connection:
        # Public canonical-table contract, independent of the CLI implementation.
        counts={name:connection.execute('SELECT COUNT(*) FROM '+name).fetchone()[0] for name in NAMES}
        rows=connection.execute("SELECT source_id,body FROM canonical_nodes WHERE kind='doc' AND state='active' ORDER BY source_id").fetchall()
        assert rows==ROWS and counts['canonical_nodes']==2,(rows,counts)
        assert connection.execute("SELECT COUNT(*) FROM _fathomdb_open_state WHERE key='_fathomdb_physical_erasure'").fetchone()[0]==0
        assert connection.execute('SELECT COUNT(*) FROM _fathomdb_dependency_closures').fetchone()[0]==0
        assert connection.execute('SELECT COUNT(*) FROM _fathomdb_erasure_requests').fetchone()[0]==0
        value=connection.execute("SELECT value FROM _fathomdb_open_state WHERE key='_fathomdb_fts_sanitation'").fetchone()
        assert value is not None,'current-format sanitation certificate required'
        sanitation=json.loads(value[0]);assert sanitation=={'version':1,'phase':'dirty','family':0,'started':False},sanitation
    return {'database':str(db),'counts':counts,'rows':rows,'sanitation':sanitation}


def verify_integrity(report,facts):
    """Require the exact documented dirty-terms diagnosis, rejecting other findings."""
    assert report['verb']=='check-integrity'
    for section in ['physical','semantic']:
        assert report[section]=={'status':'clean','findings':[]},report
    expected={'code':'E_ERASURE_INCOMPLETE','stage':'PhysicalErasure','locator':{'kind':'table_row','table':'_fathomdb_dependency_closures','rowid':0},'doc_anchor':'design/recovery.md#erasure-incomplete','detail':'Physical erasure remains owed. Stop the application before recovery.','closure_id':'retained-terms','cause':'retained_terms','phase':facts['sanitation']['phase'],'blocker':'wal_checkpoint','sequence':0,'wal_frames':0,'source_id':'[redacted]','remediation':{'argv':['fathomdb','recover','--accept-data-loss','--complete-erasures',facts['database']]}}
    assert report['logical']=={'status':'findings','findings':[expected]},report


def _distinct_inputs(paths):
    resolved=[path.resolve(strict=True) for path in paths]
    assert len(set(resolved))==len(resolved),'fresh CLI runs require distinct resolved inputs'
    identities={(path.stat().st_dev,path.stat().st_ino) for path in resolved}
    assert len(identities)==len(resolved),'hardlinked inputs do not prove two fresh runs'


def main():
    """Validate two reports of each verb against real DB facts and actual exits."""
    parser=argparse.ArgumentParser();parser.add_argument('--database',type=pathlib.Path,required=True);parser.add_argument('--integrity',type=pathlib.Path,nargs=2,required=True);parser.add_argument('--counts',type=pathlib.Path,nargs=2,required=True);parser.add_argument('--integrity-results',type=pathlib.Path,nargs=2,required=True);parser.add_argument('--counts-results',type=pathlib.Path,nargs=2,required=True);args=parser.parse_args()
    _distinct_inputs(args.integrity+args.counts+args.integrity_results+args.counts_results)
    facts=db_facts(args.database)
    for path,result in zip(args.integrity,args.integrity_results):
        record=json.loads(result.read_text());assert record['actual_exit']==65 and record.get('guard') is None
        verify_integrity(json.loads(path.read_text()),facts)
    for path,result in zip(args.counts,args.counts_results):
        record=json.loads(result.read_text());assert record['actual_exit']==0 and record.get('guard') is None
        report=json.loads(path.read_text());assert report['verb']=='dump-row-counts'
        assert [x['name'] for x in report['counts']]==NAMES
        assert {x['name']:x['rows'] for x in report['counts']}==facts['counts'],report
    print(json.dumps({'database_sha256':hashlib.sha256(args.database.read_bytes()).hexdigest(),'independent_raw_counts':facts['counts'],'authored_rows':2,'sanitation':facts['sanitation'],'exact_retained_terms_diagnoses':2,'integrity_actual_exits':[65,65],'matching_count_reports':2}))


if __name__=='__main__':main()
