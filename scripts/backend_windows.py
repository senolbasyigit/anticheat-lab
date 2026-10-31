import ctypes
from ctypes import wintypes

PROCESS_VM_OPERATION = 0x0008
PROCESS_VM_READ = 0x0010
PROCESS_VM_WRITE = 0x0020
PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
MEM_COMMIT = 0x1000
PAGE_GUARD = 0x100
PAGE_NOACCESS = 0x01
READABLE = 0x02 | 0x04 | 0x08 | 0x20 | 0x40 | 0x80

k32 = ctypes.WinDLL("kernel32", use_last_error=True)


class MBI(ctypes.Structure):
    _fields_ = [
        ("BaseAddress", ctypes.c_void_p),
        ("AllocationBase", ctypes.c_void_p),
        ("AllocationProtect", wintypes.DWORD),
        ("PartitionId", wintypes.WORD),
        ("RegionSize", ctypes.c_size_t),
        ("State", wintypes.DWORD),
        ("Protect", wintypes.DWORD),
        ("Type", wintypes.DWORD),
    ]


k32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
k32.OpenProcess.restype = wintypes.HANDLE
k32.CloseHandle.argtypes = [wintypes.HANDLE]
k32.VirtualQueryEx.argtypes = [wintypes.HANDLE, ctypes.c_void_p, ctypes.POINTER(MBI), ctypes.c_size_t]
k32.VirtualQueryEx.restype = ctypes.c_size_t
k32.ReadProcessMemory.argtypes = [wintypes.HANDLE, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)]
k32.ReadProcessMemory.restype = wintypes.BOOL
k32.WriteProcessMemory.argtypes = [wintypes.HANDLE, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)]
k32.WriteProcessMemory.restype = wintypes.BOOL
k32.QueryFullProcessImageNameW.argtypes = [wintypes.HANDLE, wintypes.DWORD, wintypes.LPWSTR, ctypes.POINTER(wintypes.DWORD)]
k32.QueryFullProcessImageNameW.restype = wintypes.BOOL


def image_path(pid):
    handle = k32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
    if not handle:
        raise OSError(ctypes.get_last_error(), "OpenProcess failed")
    try:
        buf = ctypes.create_unicode_buffer(32768)
        size = wintypes.DWORD(len(buf))
        if not k32.QueryFullProcessImageNameW(handle, 0, buf, ctypes.byref(size)):
            raise OSError(ctypes.get_last_error(), "QueryFullProcessImageNameW failed")
        return buf.value
    finally:
        k32.CloseHandle(handle)


def open_process(pid, write=False):
    access = PROCESS_QUERY_INFORMATION | PROCESS_VM_READ
    if write:
        access |= PROCESS_VM_WRITE | PROCESS_VM_OPERATION
    handle = k32.OpenProcess(access, False, pid)
    if not handle:
        raise OSError(ctypes.get_last_error(), "OpenProcess failed")
    return handle


def close(handle):
    k32.CloseHandle(handle)


def regions(handle):
    address = 0
    mbi = MBI()
    while k32.VirtualQueryEx(handle, address, ctypes.byref(mbi), ctypes.sizeof(mbi)):
        base = mbi.BaseAddress or 0
        usable = (
            mbi.State == MEM_COMMIT
            and mbi.Protect & READABLE
            and not mbi.Protect & (PAGE_GUARD | PAGE_NOACCESS)
        )
        if usable:
            yield base, mbi.RegionSize
        following = base + mbi.RegionSize
        if following <= address:
            break
        address = following


def read(handle, address, size):
    buf = ctypes.create_string_buffer(size)
    done = ctypes.c_size_t(0)
    ok = k32.ReadProcessMemory(handle, address, buf, size, ctypes.byref(done))
    if not ok and not done.value:
        return None
    return buf.raw[: done.value]


def write(handle, address, data):
    buf = ctypes.create_string_buffer(data, len(data))
    done = ctypes.c_size_t(0)
    ok = k32.WriteProcessMemory(handle, address, buf, len(data), ctypes.byref(done))
    return bool(ok) and done.value == len(data)
