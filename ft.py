from ft_function import *

FT260_Vid = 0x0403
FT260_Pid = 0x6030


createDeviceList = ftlib.FT260_CreateDeviceList
createDeviceList.argtypes = [POINTER(c_ulong)]
createDeviceList.restype = c_int

getDevicePath = ftlib.FT260_GetDevicePath
getDevicePath.argtypes = (POINTER(c_wchar), c_ulong, c_ulong)
getDevicePath.restype = c_int



def ListAllDevicePaths():
    devNum = c_ulong(0)
    pathBuf = c_wchar_p('\0'*128)

    createDeviceList(byref(devNum))

    for i in range(devNum.value):
        ftlib.FT260_GetDevicePath(pathBuf, 128, i)
        print"Index:%d\r\nPath:%s\r\n\r\n" %(i, pathBuf.value)


def openTest():
    ListAllDevicePaths()
    devNum = c_ulong(0)
    ftStatus = c_int(0)
    handle = c_void_p()

    ftlib.FT260_CreateDeviceList(byref(devNum))
    print "devNum is %d" % devNum.value
    if devNum.value < 1:
        return 0
    '''
    ftStatus = ftlib.FT260_Open(0, byref(handle))
    if not ftStatus == FT260_STATUS.FT260_OK:
        print "Open device Failed, status: %d\r\n" % (ftStatus)
        return 0
    else:
        print "Open device OK"
        ftlib.FT260_Close(handle.value);
    '''
    # mode 0 is I2C, mode 1 is UART
    ftStatus = ftlib.FT260_OpenByVidPid(FT260_Vid, FT260_Pid, 1, byref(handle))
    if not ftStatus == FT260_STATUS.FT260_OK:
        print "Open device Failed, status: %d\r\n" % (ftStatus)
        return 0
    else:
        print "Open device OK"
        ftlib.FT260_Close(handle.value);

openTest()