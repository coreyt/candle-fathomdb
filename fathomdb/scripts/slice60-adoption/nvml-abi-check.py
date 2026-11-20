import ctypes,subprocess,sys
p=subprocess.run([sys.argv[1]],capture_output=True,check=True);print('C_HEADER',p.stderr.decode().strip());print('fixture_bytes',len(p.stdout))
class Old(ctypes.Structure):_fields_=[('pid',ctypes.c_uint),('used',ctypes.c_ulonglong),('gpu',ctypes.c_uint),('compute',ctypes.c_uint),('protected',ctypes.c_ulonglong)]
class New(ctypes.Structure):_fields_=[('pid',ctypes.c_uint),('used',ctypes.c_ulonglong),('gpu',ctypes.c_uint),('compute',ctypes.c_uint)]
expected=[(101,1001,11,12),(202,2002,21,22)]
a=(Old*2).from_buffer_copy(p.stdout+b'\0'*16);got=[(x.pid,x.used,x.gpu,x.compute) for x in a];print('OLD RED',got);assert got!=expected
a=(New*2).from_buffer_copy(p.stdout);got=[(x.pid,x.used,x.gpu,x.compute) for x in a];print('NEW GREEN',got);assert got==expected and ctypes.sizeof(New)==24 and [getattr(New,n).offset for n,_ in New._fields_]==[0,8,16,20]
