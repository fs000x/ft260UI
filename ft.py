from ft_function import *



FT260_Vid = 0x0403
FT260_Pid = 0x6030


def findDeviceInPaths(Vid, Pid):
    devNum = c_ulong(0)
    pathBuf = c_wchar_p('/0'*128)
    sOpenDeviceName = u"vid_{0:04x}&pid_{1:04x}&mi_00".format(Vid, Pid)
    #print(sOpenDeviceName)
    ret = False

    ftCreateDeviceList(byref(devNum))
    for i in range(devNum.value):
        ftGetDevicePath(pathBuf, 128, i)
        if pathBuf.value.find(sOpenDeviceName):
            ret = True
        print("Index:%d\r\nPath:%s\r\n\r\n" %(i, pathBuf.value))

    return ret


    '''
    ftStatus = ftOpen(0, byref(handle))
    if not ftStatus == FT260_STATUS.FT260_OK.value:
        print("Open device Failed, status: %d\r\n" % FT260_STATUS(ftStatus))
        return 0
    else:
        print("Open device OK")
        print("Close status %s\r\n" % FT260_STATUS(ftClose(handle)))
    '''
def openTest(Vid, Pid):
    ftStatus = c_int(0)
    handle = c_void_p()

    if not findDeviceInPaths(Vid, Pid):
        return 0

    # mode 0 is I2C, mode 1 is UART
    ftStatus = ftOpenByVidPid(FT260_Vid, FT260_Pid, 1, byref(handle))
    if not ftStatus == FT260_STATUS.FT260_OK.value:
        print("Open device Failed, status: %s\r\n" % FT260_STATUS(ftStatus))
        return 0
    else:
        print("Open device OK")
        #print("Close status %s\r\n" % FT260_STATUS(ftClose(handle)))
        #return handle

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
    ftUART_SetFlowControl(handle, FT260_UART_Mode.FT260_UART_XON_XOFF_MODE);
    ulBaudrate = c_ulong(9600)
    ftUART_SetBaudRate(handle, ulBaudrate);
    ftUART_SetDataCharacteristics(handle, FT260_Data_Bit.FT260_DATA_BIT_8, FT260_Stop_Bit.FT260_STOP_BITS_1, FT260_Parity.FT260_PARITY_NONE);
    ftUART_SetBreakOff(handle);

    uartConfig = UartConfig()
    ftStatus = ftUART_GetConfig(handle, byref(uartConfig))
    if not ftStatus == FT260_STATUS.FT260_OK.value:
        print("UART Get config NG : %s\r\n" % FT260_STATUS(ftStatus))
    else:
        print("config baud:%ld, ctrl:%d, data_bit:%d, stop_bit:%d, parity:%d, breaking:%d\r\n" % (
            uartConfig.baud_rate, uartConfig.flow_ctrl, uartConfig.data_bit, uartConfig.stop_bit, uartConfig.parity, uartConfig.breaking))


    # Write data
    dwRealAccessData = c_ulong(0)
    bufferData = c_char_p(b"abcdefghij")
    buffer = cast(bufferData, c_void_p)
    ftStatus = ftUART_Write(handle, buffer, 10, 5, byref(dwRealAccessData))
    if not ftStatus == FT260_STATUS.FT260_OK.value:
        print("UART Write NG : %s\r\n" % FT260_STATUS(ftStatus))
    else:
        print("Write bytes : %d\r\n" % dwRealAccessData.value)


    print("Prepare to read data. Press Enter to continue.\r\n")


    while not input("getchar:") == 'c':
        # Read data
        dwAvailableData = c_ulong(0)
        buffer2Data = c_char_p(b'\0'*200)
        buffer2 = cast(buffer2Data, c_void_p)
        ftUART_GetQueueStatus(handle, byref(dwAvailableData))
        print("dwAvailableData : %d\r\n" % dwAvailableData.value)

        ftStatus = ftUART_Read(handle, buffer2, 50, dwAvailableData, byref(dwRealAccessData))
        if not ftStatus == FT260_STATUS.FT260_OK.value:
            print("UART Read NG : %s\r\n" % FT260_STATUS(ftStatus))
        else:
            buffer2Data = cast(buffer2, c_char_p)
            print("Read bytes : %d\r\n" % dwRealAccessData.value)
            if dwAvailableData.value > 0:
                print("buffer : %s\r\n" % buffer2Data.value)


    # Get UART DCD RI status
    value = c_uint8(0x00)
    ftEnableDcdRiPin(handle, 1);
    ftUART_GetDcdRiStatus(handle, byref(value))
    print("\r\nStatus DCD:%d, RI:%d\r\n" % (1 if (value.value&BIT0) else 0, 1 if (value.value&BIT1) else 0))


    # Set UART RI Wakeup - Rising edge
    ftEnableDcdRiPin(handle, 1);
    ftUART_EnableRiWakeup(handle, 1);
    ftSetWakeupInterrupt(handle, 0);
    ftUART_SetRiWakeupConfig(handle, FT260_RI_Wakeup_Type.FT260_RI_WAKEUP_RISING_EDGE);


    print("\r\nMake PC enter suspend, and then make RI Pin rise.\r\n");
    tmpstr = input("getchar:")


    ftClose(handle);


openTest(FT260_Vid, FT260_Pid)