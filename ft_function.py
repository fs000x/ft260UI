
# FT260 General Functions
ftCreateDeviceList = ftlib.FT260_CreateDeviceList
ftCreateDeviceList.argtypes = (POINTER(c_ulong))
ftCreateDeviceList.restype = c_int

ftGetDevicePath = ftlib.FT260_GetDevicePath
ftGetDevicePath.argtypes = (POINTER(c_wchar), c_ulong, c_ulong)
ftGetDevicePath.restype = c_int

ftOpen = ftlib.FT260_Open
ftOpen.argtypes = (c_int, POINTER(c_void_p))
ftOpen.restype = c_int

ftOpenByVidPid = ftlib.FT260_OpenByVidPid
ftOpenByVidPid.argtypes = (c_ushort, c_ushort, c_ulong, POINTER(c_void_p))
ftOpenByVidPid.restype = c_int

ftOpenByDevicePath = ftlib.FT260_OpenByDevicePath
ftOpenByDevicePath.argtypes = (POINTER(c_wchar), POINTER(c_void_p))
ftOpenByDevicePath.restype = c_int

ftClose = ftlib.FT260_Close
ftClose.argtypes = (c_void_p)
ftClose.restype = c_int


ftSetClock = ftlib.FT260_SetClock
ftSetClock.argtypes = (c_void_p, FT260_Clock_Rate clk)
ftSetClock.restype = c_int

ftSetWakeupInterrupt = ftlib.FT260_SetWakeupInterrupt
ftSetWakeupInterrupt.argtypes = (c_void_p, BOOL enable)
ftSetWakeupInterrupt.restype = c_int

ftSetInterruptTriggerType = ftlib.FT260_SetInterruptTriggerType
ftSetInterruptTriggerType.argtypes = (c_void_p, FT260_Interrupt_Trigger_Type type, FT260_Interrupt_Level_Time_Delay delay)
ftSetInterruptTriggerType.restype = c_int

ftSelectGpio2Function = ftlib.FT260_SelectGpio2Function
ftSelectGpio2Function.argtypes = (c_void_p, FT260_GPIO2_Pin gpio2Function)
ftSelectGpio2Function.restype = c_int

ftSelectGpioAFunction = ftlib.FT260_SelectGpioAFunction
ftSelectGpioAFunction.argtypes = (c_void_p, FT260_GPIOA_Pin gpioAFunction)
ftSelectGpioAFunction.restype = c_int

ftSelectGpioGFunction = ftlib.FT260_SelectGpioGFunction
ftSelectGpioGFunction.argtypes = (c_void_p, FT260_GPIOG_Pin gpioGFunction)
ftSelectGpioGFunction.restype = c_int

ftSetSuspendOutPolarity = ftlib.FT260_SetSuspendOutPolarity
ftSetSuspendOutPolarity.argtypes = (c_void_p, FT260_Suspend_Out_Polarity polarity)
ftSetSuspendOutPolarity.restype = c_int


ftSetParam_U8 = ftlib.FT260_SetParam_U8
ftSetParam_U8.argtypes = (c_void_p, FT260_PARAM_1 param, uint8 value)
ftSetParam_U8.restype = c_int

ftSetParam_U16 = ftlib.FT260_SetParam_U16
ftSetParam_U16.argtypes = (c_void_p, FT260_PARAM_2 param, uint16 value)
ftSetParam_U16.restype = c_int


ftGetChipVersion = ftlib.FT260_GetChipVersion
ftGetChipVersion.argtypes = (c_void_p, POINTER(c_ulong))
ftGetChipVersion.restype = c_int

ftGetLibVersion = ftlib.FT260_GetLibVersion
ftGetLibVersion.argtypes = (POINTER(c_ulong))
ftGetLibVersion.restype = c_int


ftEnableI2CPin = ftlib.FT260_EnableI2CPin
ftEnableI2CPin.argtypes = (c_void_p, BOOL enable)
ftEnableI2CPin.restype = c_int

ftSetUartToGPIOPin = ftlib.FT260_SetUartToGPIOPin
ftSetUartToGPIOPin.argtypes = (c_void_p)
ftSetUartToGPIOPin.restype = c_int

ftEnableDcdRiPin = ftlib.FT260_EnableDcdRiPin
ftEnableDcdRiPin.argtypes = (c_void_p, BOOL enable)
ftEnableDcdRiPin.restype = c_int


# FT260 I2C Functions
ftI2CMaster_Init = ftlib.FT260_I2CMaster_Init
ftI2CMaster_Init.argtypes = (c_void_p, uint32 kbps)
ftI2CMaster_Init.restype = c_int

ftI2CMaster_Read = ftlib.FT260_I2CMaster_Read
ftI2CMaster_Read.argtypes = (c_void_p, uint8 deviceAddress, FT260_I2C_FLAG flag, LPVOID lpBuffer, c_ulong, POINTER(c_ulong))
ftI2CMaster_Read.restype = c_int

ftI2CMaster_Write = ftlib.FT260_I2CMaster_Write
ftI2CMaster_Write.argtypes = (c_void_p, uint8 deviceAddress, FT260_I2C_FLAG flag, LPVOID lpBuffer, c_ulong, POINTER(c_ulong))
ftI2CMaster_Write.restype = c_int

ftI2CMaster_GetStatus = ftlib.FT260_I2CMaster_GetStatus
ftI2CMaster_GetStatus.argtypes = (c_void_p, uint8* status)
ftI2CMaster_GetStatus.restype = c_int

ftI2CMaster_Reset = ftlib.FT260_I2CMaster_Reset
ftI2CMaster_Reset.argtypes = (c_void_p)
ftI2CMaster_Reset.restype = c_int



# FT260 UART Functions
ftUART_Init = ftlib.FT260_UART_Init
ftUART_Init.argtypes = (c_void_p)
ftUART_Init.restype = c_int

ftUART_SetBaudRate = ftlib.FT260_UART_SetBaudRate
ftUART_SetBaudRate.argtypes = (c_void_p, ULONG baudRate)
ftUART_SetBaudRate.restype = c_int

ftUART_SetFlowControl = ftlib.FT260_UART_SetFlowControl
ftUART_SetFlowControl.argtypes = (c_void_p, FT260_UART_Mode flowControl)
ftUART_SetFlowControl.restype = c_int

ftUART_SetDataCharacteristics = ftlib.FT260_UART_SetDataCharacteristics
ftUART_SetDataCharacteristics.argtypes = (c_void_p, FT260_Data_Bit dataBits, FT260_Stop_Bit stopBits, FT260_Parity parity)
ftUART_SetDataCharacteristics.restype = c_int

ftUART_SetBreakOn = ftlib.FT260_UART_SetBreakOn
ftUART_SetBreakOn.argtypes = (c_void_p)
ftUART_SetBreakOn.restype = c_int

ftUART_SetBreakOff = ftlib.FT260_UART_SetBreakOff
ftUART_SetBreakOff.argtypes = (c_void_p)
ftUART_SetBreakOff.restype = c_int

ftUART_SetXonXoffChar = ftlib.FT260_UART_SetXonXoffChar
ftUART_SetXonXoffChar.argtypes = (c_void_p, UCHAR Xon, UCHAR Xoff)
ftUART_SetXonXoffChar.restype = c_int

ftUART_GetConfig = ftlib.FT260_UART_GetConfig
ftUART_GetConfig.argtypes = (c_void_p, UartConfig* pUartConfig)
ftUART_GetConfig.restype = c_int

ftUART_GetQueueStatus = ftlib.FT260_UART_GetQueueStatus
ftUART_GetQueueStatus.argtypes = (c_void_p, POINTER(c_ulong))
ftUART_GetQueueStatus.restype = c_int

ftUART_Read = ftlib.FT260_UART_Read
ftUART_Read.argtypes = (c_void_p, LPVOID lpBuffer, c_ulong, c_ulong, POINTER(c_ulong))
ftUART_Read.restype = c_int

ftUART_Write = ftlib.FT260_UART_Write
ftUART_Write.argtypes = (c_void_p, LPVOID lpBuffer, c_ulong, c_ulong, POINTER(c_ulong))
ftUART_Write.restype = c_int

ftUART_Reset = ftlib.FT260_UART_Reset
ftUART_Reset.argtypes = (c_void_p)
ftUART_Reset.restype = c_int


ftUART_GetDcdRiStatus = ftlib.FT260_UART_GetDcdRiStatus
ftUART_GetDcdRiStatus.argtypes = (c_void_p, uint8* value)
ftUART_GetDcdRiStatus.restype = c_int

ftUART_EnableRiWakeup = ftlib.FT260_UART_EnableRiWakeup
ftUART_EnableRiWakeup.argtypes = (c_void_p, BOOL enable)
ftUART_EnableRiWakeup.restype = c_int

ftUART_SetRiWakeupConfig = ftlib.FT260_UART_SetRiWakeupConfig
ftUART_SetRiWakeupConfig.argtypes = (c_void_p, FT260_RI_Wakeup_Type type)
ftUART_SetRiWakeupConfig.restype = c_int


# Interrupt is transmitted by UART interface
ftGetInterruptFlag = ftlib.FT260_GetInterruptFlag
ftGetInterruptFlag.argtypes = (c_void_p, BOOL* pbFlag)
ftGetInterruptFlag.restype = c_int

ftCleanInterruptFlag = ftlib.FT260_CleanInterruptFlag
ftCleanInterruptFlag.argtypes = (c_void_p, BOOL* pbFlag)
ftCleanInterruptFlag.restype = c_int



# FT260 GPIO Functions
ftGPIO_Set = ftlib.FT260_GPIO_Set
ftGPIO_Set.argtypes = (c_void_p, FT260_GPIO_Report report)
ftGPIO_Set.restype = c_int

ftGPIO_Get = ftlib.FT260_GPIO_Get
ftGPIO_Get.argtypes = (c_void_p, FT260_GPIO_Report *report)
ftGPIO_Get.restype = c_int

ftGPIO_SetDir = ftlib.FT260_GPIO_SetDir
ftGPIO_SetDir.argtypes = (c_void_p, c_ushort, BYTE dir)
ftGPIO_SetDir.restype = c_int

ftGPIO_Read = ftlib.FT260_GPIO_Read
ftGPIO_Read.argtypes = (c_void_p, c_ushort, BYTE* pValue)
ftGPIO_Read.restype = c_int

ftGPIO_Write = ftlib.FT260_GPIO_Write
ftGPIO_Write.argtypes = (c_void_p, c_ushort, BYTE value)
ftGPIO_Write.restype = c_int

