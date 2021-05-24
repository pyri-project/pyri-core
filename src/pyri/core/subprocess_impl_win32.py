import ctypes
import sys

if sys.platform == "win32":
    import ctypes.wintypes
    class JOBOBJECT_BASIC_LIMIT_INFORMATION(ctypes.Structure):
        _fields_ = [
                ('PerProcessUserTimeLimit', ctypes.wintypes.LARGE_INTEGER),
                ('PerJobUserTimeLimit', ctypes.wintypes.LARGE_INTEGER),
                ('LimitFlags', ctypes.wintypes.DWORD),
                ('MinimumWorkingSetSize', ctypes.c_size_t),
                ('MaximumWorkingSetSize', ctypes.c_size_t),
                ('ActiveProcessLimit', ctypes.wintypes.DWORD),  
                ('Affinity', ctypes.POINTER(ctypes.c_ulong)),
                ('PriorityClass', ctypes.wintypes.DWORD),
                ('SchedulingClass', ctypes.wintypes.DWORD)
            ]

    class IO_COUNTERS(ctypes.Structure):
        _fields_ = [
            ('ReadOperationCount',ctypes.c_ulonglong),
            ('WriteOperationCount',ctypes.c_ulonglong),
            ('OtherOperationCount',ctypes.c_ulonglong),
            ('ReadTransferCount',ctypes.c_ulonglong),
            ('WriteTransferCount',ctypes.c_ulonglong),
            ('OtherTransferCount',ctypes.c_ulonglong),
        ]

    class JOBOBJECT_EXTENDED_LIMIT_INFORMATION(ctypes.Structure):
        _fields_ = [
            ('BasicLimitInformation',JOBOBJECT_BASIC_LIMIT_INFORMATION),
            ('IoInfo', IO_COUNTERS),
            ('ProcessMemoryLimit', ctypes.c_size_t),
            ('JobMemoryLimit', ctypes.c_size_t),
            ('PeakProcessMemoryUsed', ctypes.c_size_t),
            ('PeakJobMemoryUsed', ctypes.c_size_t)
        ]

    class THREADENTRY32(ctypes.Structure):
        _fields_ = [
            ("dwSize", ctypes.c_ulong),
            ("cntUsage", ctypes.c_ulong),
            ("th32ThreadID", ctypes.c_ulong),
            ("th32OwnerProcessID", ctypes.c_ulong),
            ("tpBasePri", ctypes.c_ulong),
            ("tpDeltaPri", ctypes.c_ulong),
            ("dwFlags", ctypes.c_ulong)
        ]

    class JOBOBJECT_BASIC_PROCESS_ID_LIST(ctypes.Structure):
        _fields_ = [
            ("NumberOfAssignedProcesses", ctypes.wintypes.DWORD),
            ("NumberOfProcessIdsInList", ctypes.wintypes.DWORD),
            ("ProcessIdList", ctypes.c_size_t*16384)
        ]

    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.wintypes.BOOL,ctypes.wintypes.HWND,ctypes.wintypes.LPARAM)


    JobObjectBasicLimitInformation = 2
    JobObjectBasicProcessIdList = 3
    JobObjectExtendedLimitInformation = 9
    JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x00002000
    PROCESS_SET_QUOTA = 0x0100
    PROCESS_TERMINATE = 0x0001
    CREATE_SUSPENDED = 0x00000004

    TH32CS_SNAPTHREAD = 0x00000004
    THREAD_SUSPEND_RESUME = 0x0002

    HWND_MESSAGE = ctypes.wintypes.HWND(-3)
    WM_CLOSE = 16

    def win32_create_job_object():
        job = ctypes.windll.kernel32.CreateJobObjectW(None, None)
        job_limits = JOBOBJECT_EXTENDED_LIMIT_INFORMATION()
        res = ctypes.windll.kernel32.QueryInformationJobObject(job, JobObjectExtendedLimitInformation, ctypes.pointer(job_limits), ctypes.sizeof(job_limits), None)
        assert "Internal error, could not query win32 job object information"
        job_limits.BasicLimitInformation.LimitFlags |= JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        res = ctypes.windll.kernel32.SetInformationJobObject(job, JobObjectExtendedLimitInformation, ctypes.pointer(job_limits), ctypes.sizeof(job_limits))
        assert res, "Internal error, could not set win32 job object information"
        #current_process = ctypes.windll.kernel32.OpenProcess(PROCESS_SET_QUOTA | PROCESS_TERMINATE, False, ctypes.windll.kernel32.GetCurrentProcessId())
        #res = ctypes.windll.kernel32.AssignProcessToJobObject(job, current_process)
        #assert res, "Internal error, could not assign win32 process to job"
        return job

    def win32_attach_job_and_resume_process(asyncio_process, job):
        
        h = ctypes.windll.kernel32.OpenProcess(PROCESS_SET_QUOTA | PROCESS_TERMINATE, False, asyncio_process.pid)
        res = ctypes.windll.kernel32.AssignProcessToJobObject(job, h)
        assert res, "Internal error, could not assign win32 process to job"
        ctypes.windll.kernel32.CloseHandle(h)

        win32_resume_process(asyncio_process.pid)

    def win32_close_job_object(handle):
        if handle is None:
            return
        ctypes.windll.kernel32.CloseHandle(handle)

    def win32_get_thread_ids(pid):

        thread_ids = []

        hThreadSnap = ctypes.windll.kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD, pid)
        try:
            te32 = THREADENTRY32()
            te32.dwSize = ctypes.sizeof(THREADENTRY32)
            if ctypes.windll.kernel32.Thread32First(hThreadSnap, ctypes.byref(te32)) == 0:
                pass

            else:
                while True:
                    if pid == te32.th32OwnerProcessID:
                        thread_ids.append(te32.th32ThreadID)

                    if ctypes.windll.kernel32.Thread32Next(hThreadSnap, ctypes.byref(te32)) == 0:
                        break
        finally:
            ctypes.windll.kernel32.CloseHandle(hThreadSnap)
        return sorted(thread_ids)

    def win32_resume_process(pid):
        thread_ids = win32_get_thread_ids(pid)
        for thread_id in thread_ids:
            thread_h = ctypes.windll.kernel32.OpenThread(THREAD_SUSPEND_RESUME, False, thread_id)
            ctypes.windll.kernel32.ResumeThread(thread_h)
            ctypes.windll.kernel32.CloseHandle(thread_h)

    def win32_send_job_wm_close(job):
        win32_thread_info = JOBOBJECT_BASIC_PROCESS_ID_LIST()
        res = ctypes.windll.kernel32.QueryInformationJobObject(job, JobObjectBasicProcessIdList, ctypes.pointer(win32_thread_info), ctypes.sizeof(win32_thread_info), None)
        if not res:
            return
        pids = []
        for i in range(win32_thread_info.NumberOfProcessIdsInList):
            pids.append(win32_thread_info.ProcessIdList[i])

        for p in pids:
            win32_send_pid_wm_close(p)

    def win32_send_pid_wm_close(pid):
        _win32_send_pid_wm_close_hwnd_message(pid)
        _win32_send_pid_wm_close_hwnd_main(pid)

    def _win32_send_pid_wm_close_hwnd_message(pid):
        hWnd_child_after = 0

        while True:
            hWnd = ctypes.windll.user32.FindWindowExW(HWND_MESSAGE, hWnd_child_after, None, None)
            # print(hWnd)    
            if hWnd == 0:
                break
            process_id = ctypes.wintypes.DWORD()
            ctypes.windll.user32.GetWindowThreadProcessId(hWnd,ctypes.byref(process_id))
            if pid == process_id.value:
                ctypes.windll.user32.PostMessageW(hWnd,WM_CLOSE,0,0)
            hWnd_child_after = hWnd

    def _win32_send_pid_wm_close_hwnd_main(pid):
        

        def worker(hWnd, lParam):
            process_id = ctypes.wintypes.DWORD()
            ctypes.windll.user32.GetWindowThreadProcessId(hWnd,ctypes.byref(process_id))
            if lParam == process_id.value:
                ctypes.windll.user32.PostMessageW(hWnd,WM_CLOSE,0,0)
            return True

        cb_worker = WNDENUMPROC(worker)
        if not ctypes.windll.user32.EnumWindows(cb_worker, pid):
            return
        
        

