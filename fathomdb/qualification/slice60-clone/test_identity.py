"""Prove the UUID prelude refuses before the original body using a synthetic ABI."""
import argparse
import os
import pathlib
import subprocess
import tempfile

parser=argparse.ArgumentParser();parser.add_argument('--binary',required=True);parser.add_argument('--cuda-include',default='/usr/local/cuda-12.6/include');args=parser.parse_args()
source=r'''
#include <cuda.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static void mark(const char *s) { FILE *f=fopen(getenv("QUALIFIER_TRACE"),"a"); if(!f)abort(); fprintf(f,"%s\n",s); fclose(f); }
CUresult cuInit(unsigned int f) { (void)f; mark("init"); return CUDA_SUCCESS; }
CUresult cuDeviceGetCount(int *n) { mark("count"); *n=1; return CUDA_SUCCESS; }
CUresult cuDeviceGet(CUdevice *d,int ordinal) { mark("device"); *d=ordinal; return CUDA_SUCCESS; }
CUresult cuDeviceGetUuid(CUuuid *u,CUdevice d) { (void)d; mark("uuid"); memset(u,0,sizeof(*u)); return CUDA_SUCCESS; }
'''
with tempfile.TemporaryDirectory(prefix='slice60-clone-identity-') as directory:
    root=pathlib.Path(directory);(root/'driver.c').write_text(source)
    subprocess.run(['gcc','-Wall','-Wextra','-Werror','-shared','-fPIC','-I'+args.cuda_include,str(root/'driver.c'),'-o',str(root/'libcuda.so')],check=True)
    symbols=subprocess.check_output(['nm','-D','--defined-only',str(root/'libcuda.so')],text=True)
    assert all(' '+name+'\n' in symbols for name in ['cuInit','cuDeviceGetCount','cuDeviceGet','cuDeviceGetUuid'])
    env=dict(os.environ,LD_LIBRARY_PATH=str(root),QUALIFIER_TRACE=str(root/'trace'),CUDA_VISIBLE_DEVICES='-1',FATHOMDB_REQUIRE_LIVE='1',FATHOMDB_SELECTED_UUID='GPU-11111111-0000-0000-0000-000000000000',FATHOMDB_COORDINATED_RESET='healthy')
    result=subprocess.run([str(pathlib.Path(args.binary).resolve()),'--ignored','--exact','prechecked_clone_checks_uuid_before_original_body','--nocapture','--test-threads=1'],env=env,text=True,capture_output=True,check=False)
    assert result.returncode==101,(result.returncode,result.stdout,result.stderr)
    assert 'GPU-00000000-0000-0000-0000-000000000000' in result.stderr,(result.stdout,result.stderr)
    assert 'GPU-11111111-0000-0000-0000-000000000000' in result.stderr
    assert 'tensor-last-clone: ready' not in result.stdout
    assert 'process-primary-reset-returned' not in result.stdout
    assert (root/'trace').read_text().splitlines()==['init','count','device','uuid']
    print('PASS synthetic ABI: UUID mismatch refused before original body; no context retain/reset/hardware claim')
