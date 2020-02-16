from ft_function import *
import time

FT260_Vid = 0x0403
FT260_Pid = 0x6030


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


def openFtAsI2c(Vid, Pid):
    ftStatus = c_int(0)
    handle = c_void_p()

    # mode 0 is I2C, mode 1 is UART
    ftStatus = ftOpenByVidPid(FT260_Vid, FT260_Pid, 0, byref(handle))
    if not ftStatus == FT260_STATUS.FT260_OK.value:
        print("Open device Failed, status: %s\r\n" % FT260_STATUS(ftStatus))
        return 0
    else:
        print("Open device OK")

    ftStatus = ftI2CMaster_Init(handle, i2cCfgDef['rate'])
    if not ftStatus == FT260_STATUS.FT260_OK.value:
        ftClose(handle)
        ftStatus = ftOpenByVidPid(FT260_Vid, FT260_Pid, 1, byref(handle))
        if not ftStatus == FT260_STATUS.FT260_OK.value:
            print("ReOpen device Failed, status: %s\r\n" % FT260_STATUS(ftStatus))
            return 0
        else:
            print("ReOpen device OK")
        ftStatus = ftI2CMaster_Init(handle, i2cCfgDef['rate'])
        if not ftStatus == FT260_STATUS.FT260_OK.value:
            print("I2c Init Failed, status: %s\r\n" % FT260_STATUS(ftStatus))
            return 0

    print("I2c Init OK")

    return handle


def ftI2cConfig(handle, cfgRate):
    # config i2cRateDef
    ftI2CMaster_Reset(handle)
    ftStatus = ftI2CMaster_Init(handle, cfgRate)
    if not ftStatus == FT260_STATUS.FT260_OK.value:
        print("I2c Init Failed, status: %s\r\n" % FT260_STATUS(ftStatus))
        return 0
    else:
        print("I2c Init OK")


def ftI2cWrite(handle, i2cDev, flag, data=b''):
    # Write data
    dwRealAccessData = c_ulong(0)
    bufferData = c_char_p(bytes(data))
    buffer = cast(bufferData, c_void_p)
    ftStatus = ftI2CMaster_Write(handle, i2cDev, flag, buffer, len(data), byref(dwRealAccessData))
    if not ftStatus == FT260_STATUS.FT260_OK.value:
        print("I2c Write NG : %s\r\n" % FT260_STATUS(ftStatus))
    else:
        print("Write bytes : %d\r\n" % dwRealAccessData.value)


def ftI2cRead(handle, i2cDev, flag, readLen=1):
    # Read data
    dwRealAccessData = c_ulong(0) # Create variable to store received bytes
    buffer = create_string_buffer(readLen + 1) # Create buffer to hold received data as string
    buffer_void = cast(buffer, c_void_p) # Convert the same buffer to void pointer

    ftStatus = ftI2CMaster_Read(handle, i2cDev, flag, buffer_void, readLen, byref(dwRealAccessData))

    return ftStatus, dwRealAccessData.value, buffer.value


def openFtAsUart(Vid, Pid):
    ftStatus = c_int(0)
    handle = c_void_p()

    # mode 0 is I2C, mode 1 is UART
    ftStatus = ftOpenByVidPid(FT260_Vid, FT260_Pid, 1, byref(handle))
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

    time.sleep(1)