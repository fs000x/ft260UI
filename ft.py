from ft_function import *
import struct

_log_queue = None

def findDeviceInPaths(Vid, Pid):
    # Preparing paths list
    devNum = c_ulong(0)
    pathBuf = c_wchar_p('/0'*128)
    sOpenDeviceName = u"vid_{0:04x}&pid_{1:04x}".format(Vid, Pid)
    print("Searching for {} in paths".format(sOpenDeviceName))
    ret = False
    ftCreateDeviceList(byref(devNum))

    # For each path check that search string is within and list them
    valid_devices=list()
    for i in range(devNum.value):
        ftGetDevicePath(pathBuf, 128, i)
        if pathBuf.value.find(sOpenDeviceName) > 0:
            ret = True
            valid_devices.append(pathBuf.value)
        print("Index:%d\r\nPath:%s\r\n\r\n" % (i, pathBuf.value))

    # For each valid device try to use the composite device (with &mi_00)
    sOpenDeviceName += "&mi_00"
    for i in range(len(valid_devices)):
        if pathBuf.value.find(sOpenDeviceName) > 0:
            print("Composite FT260 device found on path {}\r\n".format(valid_devices[i]))
        else:
            print("Not composite FT260 device found on path {}\r\n".format(valid_devices[i]))
    return ret


def openFtAsI2c(Vid, Pid, cfgRate):
    """
    Tries to open FY260 device by its VID and PID. Also initialize it with I2C speed defined by rate.
    Returns device handle.
    :param Vid: Vendor ID of the USB chip. For FT260 it is 0x0403
    :param Pid: Product ID of the USB chip. For FT260_it is 0x6030
    :param cfgRate: speed of connection in kbots. 100 and 400 are mostly used in I2C devices, though higher values are
    also possible.
    :return: handle for opened device. Handle must be stored for future use.
    """
    handle = c_void_p()

    # mode 0 is I2C, mode 1 is UART
    # Opening first device of possibly many available is used by providing indev 0 as third parameter.
    ftStatus = ftOpenByVidPid(Vid, Pid, 0, byref(handle))
    if not ftStatus == FT260_STATUS.FT260_OK.value:
        print("Open device Failed, status: %s\r\n" % FT260_STATUS(ftStatus))
        return 0
    else:
        print("Open device OK")

    ftStatus = ftI2CMaster_Init(handle, cfgRate)
    if not ftStatus == FT260_STATUS.FT260_OK.value:
        ftClose(handle)
        ftStatus = ftOpenByVidPid(Vid, Pid, 1, byref(handle))
        if not ftStatus == FT260_STATUS.FT260_OK.value:
            print("ReOpen device Failed, status: %s\r\n" % FT260_STATUS(ftStatus))
            return 0
        else:
            print("ReOpen device OK")
        ftStatus = ftI2CMaster_Init(handle, cfgRate)
        if not ftStatus == FT260_STATUS.FT260_OK.value:
            print("I2c Init Failed, status: %s\r\n" % FT260_STATUS(ftStatus))
            return 0

    print("I2c Init OK")

    return handle

def I2C_Mode_Name(flag :FT260_I2C_FLAG):
    Dict = {FT260_I2C_FLAG.FT260_I2C_NONE: 'None',
            FT260_I2C_FLAG.FT260_I2C_REPEATED_START: 'Repeated start',
            FT260_I2C_FLAG.FT260_I2C_START_AND_STOP: 'Start&stop',
            FT260_I2C_FLAG.FT260_I2C_START: 'Start',
            FT260_I2C_FLAG.FT260_I2C_STOP: 'Stop'
            }
    return Dict[flag]

def ftI2cConfig(handle, cfgRate):
    """
    Sets I2C speed (rate). Standard values are 100 and 400 kbods. Higher values are also possible.
    :param handle: Device handle from previous openFtAsI2c calls.
    :param cfgRate: Rate in kbods. Example: 100
    :return: None
    """
    ftI2CMaster_Reset(handle)
    ftStatus = ftI2CMaster_Init(handle, cfgRate)
    if not ftStatus == FT260_STATUS.FT260_OK.value:
        print("I2c Init Failed, status: %s\r\n" % FT260_STATUS(ftStatus))
        return 0
    else:
        print("I2c Init OK")


def ftI2cWrite(handle, i2cDev, flag, data):
    global _log_queue

    # Write data
    dwRealAccessData = c_ulong(0)
    status = c_uint8(0)  # To store status after operation
    buffer = create_string_buffer(data)
    buffer_void = cast(buffer, c_void_p)
    ftStatus = ftI2CMaster_Write(handle, i2cDev, flag, buffer_void, len(data), byref(dwRealAccessData))
    ftI2CMaster_GetStatus(handle, byref(status))
    if not ftStatus == FT260_STATUS.FT260_OK.value:
        print("I2c Write NG : %s\r\n" % FT260_STATUS(ftStatus))
    else:
        # Logging block. If enabled and there is data
        if _log_queue is not None and dwRealAccessData.value > 0:
            unpackstr = "<" + "B" * dwRealAccessData.value
            writetuple = struct.unpack(unpackstr, buffer.raw[:dwRealAccessData.value])
            msg =""
            for i in writetuple:
                msg += hex(i) + " "
            if not _log_queue.full():
                _log_queue.put(['Write', hex(i2cDev), msg, I2C_Mode_Name(flag), status.value])
            else:
                raise Exception("Interprocess communication Queue is full. Can't put new message.")

    return ftStatus, dwRealAccessData.value, buffer.raw, status.value


def ftI2cRead(handle, i2cDev, flag, readLen):
    """
    Read data
    :param handle:
    :param i2cDev:
    :param flag:
    :param readLen:
    :return:
    """
    global _log_queue

    dwRealAccessData = c_ulong(0) # Create variable to store received bytes
    status = c_uint8(0) # To store status after operation
    buffer = create_string_buffer(readLen) # Create buffer to hold received data as string
    buffer_void = cast(buffer, c_void_p) # Convert the same buffer to void pointer

    ftStatus = ftI2CMaster_Read(handle, i2cDev, flag, buffer_void, readLen, byref(dwRealAccessData))
    ftI2CMaster_GetStatus(handle, byref(status))

    # Logging block. If enabled, data is valid and there is data
    if _log_queue is not None and ftStatus == FT260_STATUS.FT260_OK.value and dwRealAccessData.value > 0:
        unpackstr = "<" + "B" * dwRealAccessData.value
        readtuple = struct.unpack(unpackstr, buffer.raw[:dwRealAccessData.value])
        msg = ""
        for i in readtuple:
            msg += hex(i) + " "
        if not _log_queue.full():
            _log_queue.put(['Read', hex(i2cDev), msg, I2C_Mode_Name(flag), status.value])
        else:
            raise Exception("Interprocess communication Queue is full. Can't put new message.")

    return ftStatus, dwRealAccessData.value, buffer.raw, status.value


def openFtAsUart(Vid, Pid):
    ftStatus = c_int(0)
    handle = c_void_p()

    # mode 0 is I2C, mode 1 is UART
    ftStatus = ftOpenByVidPid(Vid, Pid, 1, byref(handle))
    if not ftStatus == FT260_STATUS.FT260_OK.value:
        print("Open device Failed, status: %s\r\n" % FT260_STATUS(ftStatus))
        return 0
    else:
        print("Open device OK")

    ftStatus = ftUART_Init(handle)
    if not ftStatus == FT260_STATUS.FT260_OK.value:
        print("Uart Init Failed, status: %s\r\n" % FT260_STATUS(ftStatus))
        return 0
    else:
        print("Uart Init OK")

    # config TX_ACTIVE for UART 485
    ftStatus = ftSelectGpioAFunction(handle, FT260_GPIOA_Pin.FT260_GPIOA_TX_ACTIVE)
    if not ftStatus == FT260_STATUS.FT260_OK.value:
        print("Uart TX_ACTIVE Failed, status: %s\r\n" % FT260_STATUS(ftStatus))
        return 0
    else:
        print("Uart TX_ACTIVE OK")

    # config UART
    ftUART_SetFlowControl(handle, FT260_UART_Mode.FT260_UART_XON_XOFF_MODE)
    ulBaudrate = c_ulong(9600)
    ftUART_SetBaudRate(handle, ulBaudrate)
    ftUART_SetDataCharacteristics(handle, FT260_Data_Bit.FT260_DATA_BIT_8, FT260_Stop_Bit.FT260_STOP_BITS_1, FT260_Parity.FT260_PARITY_NONE)
    ftUART_SetBreakOff(handle)

    uartConfig = UartConfig()
    ftStatus = ftUART_GetConfig(handle, byref(uartConfig))
    if not ftStatus == FT260_STATUS.FT260_OK.value:
        print("UART Get config NG : %s\r\n" % FT260_STATUS(ftStatus))
    else:
        print("config baud:%ld, ctrl:%d, data_bit:%d, stop_bit:%d, parity:%d, breaking:%d\r\n" % (
            uartConfig.baud_rate, uartConfig.flow_ctrl, uartConfig.data_bit, uartConfig.stop_bit, uartConfig.parity, uartConfig.breaking))
    return handle


def ftUartWrite(handle):
    # Write data
    while True:
        str = input("> ")
        dwRealAccessData = c_ulong(0)
        bufferData = c_char_p(bytes(str,'utf-8'))
        buffer = cast(bufferData, c_void_p)
        ftStatus = ftUART_Write(handle, buffer, len(str), len(str), byref(dwRealAccessData))
        if not ftStatus == FT260_STATUS.FT260_OK.value:
            print("UART Write NG : %s\r\n" % FT260_STATUS(ftStatus))
        else:
            print("Write bytes : %d\r\n" % dwRealAccessData.value)



def ftUartReadLoop(handle):
    #print("Prepare to read data. Press Enter to continue.\r\n")

    while True:
        # Read data
        dwRealAccessData = c_ulong(0)
        dwAvailableData = c_ulong(0)
        buffer2Data = c_char_p(b'\0'*200)
        memset(buffer2Data, 0, 200)
        buffer2 = cast(buffer2Data, c_void_p)
        ftUART_GetQueueStatus(handle, byref(dwAvailableData))
        if dwAvailableData.value == 0:
            continue
        print("dwAvailableData : %d\r\n" % dwAvailableData.value)

        ftStatus = ftUART_Read(handle, buffer2, 50, dwAvailableData, byref(dwRealAccessData))
        if not ftStatus == FT260_STATUS.FT260_OK.value:
            print("UART Read NG : %s\r\n" % FT260_STATUS(ftStatus))
        else:
            buffer2Data = cast(buffer2, c_char_p)
            print("Read bytes : %d\r\n" % dwRealAccessData.value)
            if dwAvailableData.value > 0:
                print("buffer : %s\r\n" % buffer2Data.value.decode("utf-8"))
