from ctypes import *
from enum import *

ftdll = "LibFT260.dll"

ftlib = windll.LoadLibrary(ftdll)
msvcrt = cdll.msvcrt

FT260_Vid = 0x0403
FT260_Pid = 0x6030


createDeviceList = ftlib.FT260_CreateDeviceList
createDeviceList.argtypes = [POINTER(c_ulong)]
createDeviceList.restype = c_int

getDevicePath = ftlib.FT260_GetDevicePath
getDevicePath.argtypes = (POINTER(c_wchar), c_ulong, c_ulong)
getDevicePath.restype = c_int

class FT260_STATUS(Enum):
    FT260_OK = 0
    FT260_INVALID_HANDLE = 1
    FT260_DEVICE_NOT_FOUND = 2
    FT260_DEVICE_NOT_OPENED = 3
    FT260_DEVICE_OPEN_FAIL = 4
    FT260_DEVICE_CLOSE_FAIL = 5
    FT260_INCORRECT_INTERFACE = 6
    FT260_INCORRECT_CHIP_MODE = 7
    FT260_DEVICE_MANAGER_ERROR = 8
    FT260_IO_ERROR = 9
    FT260_INVALID_PARAMETER = 10
    FT260_NULL_BUFFER_POINTER = 11
    FT260_BUFFER_SIZE_ERROR = 12
    FT260_UART_SET_FAIL = 13
    FT260_RX_NO_DATA = 14
    FT260_GPIO_WRONG_DIRECTION = 15
    FT260_INVALID_DEVICE = 16
    FT260_OTHER_ERROR = 17



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