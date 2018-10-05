from ft_function import *



FT260_Vid = 0x0403
FT260_Pid = 0x6030


def ListAllDevicePaths():
    devNum = c_ulong(0)
    pathBuf = c_wchar_p('/0'*128)

    ftCreateDeviceList(byref(devNum))

    for i in range(devNum.value):
        ftGetDevicePath(pathBuf, 128, i)
        print("Index:%d\r\nPath:%s\r\n\r\n" %(i, pathBuf.value))


def openTest():
    ListAllDevicePaths()
    devNum = c_ulong(0)
    ftStatus = c_int(0)
    handle = c_void_p()

    ftCreateDeviceList(byref(devNum))
    print("devNum is %d" % devNum.value)
    if devNum.value < 1:
        return 0
    '''
    ftStatus = ftOpen(0, byref(handle))
    if not ftStatus == FT260_STATUS.FT260_OK.value:
        print("Open device Failed, status: %d\r\n" % FT260_STATUS(ftStatus))
        return 0
    else:
        print("Open device OK")
        print("Close status %s\r\n" % FT260_STATUS(ftClose(handle)))
    '''
    # mode 0 is I2C, mode 1 is UART
    ftStatus = ftOpenByVidPid(FT260_Vid, FT260_Pid, 1, byref(handle))
    if not ftStatus == FT260_STATUS.FT260_OK.value:
        print("Open device Failed, status: %s\r\n" % FT260_STATUS(ftStatus))
        return 0
    else:
        print("Open device OK")
        print("Close status %s\r\n" % FT260_STATUS(ftClose(handle)))
    #'''

openTest()