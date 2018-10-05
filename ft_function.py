from ctypes import *
from enum import *

ftdll = "lib/LibFT260.dll"

ftlib = windll.LoadLibrary(ftdll)


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


class FT260_GPIO2_Pin(Enum):
    FT260_GPIO2_GPIO    = 0
    FT260_GPIO2_SUSPOUT = 1
    FT260_GPIO2_PWREN   = 2
    FT260_GPIO2_TX_LED  = 4

class FT260_GPIOA_Pin(Enum):
    FT260_GPIOA_GPIO      = 0
    FT260_GPIOA_TX_ACTIVE = 3
    FT260_GPIOA_TX_LED    = 4

class FT260_GPIOG_Pin(Enum):
    FT260_GPIOG_GPIO     = 0
    FT260_GPIOG_PWREN    = 2
    FT260_GPIOG_RX_LED   = 5
    FT260_GPIOG_BCD_DET  = 6

class FT260_Clock_Rate(Enum):
    FT260_SYS_CLK_12M = 0
    FT260_SYS_CLK_24M = 1
    FT260_SYS_CLK_48M = 2

class FT260_Interrupt_Trigger_Type(Enum):
    FT260_INTR_RISING_EDGE = 0
    FT260_INTR_LEVEL_HIGH = 1
    FT260_INTR_FALLING_EDGE = 2
    FT260_INTR_LEVEL_LOW = 3

class FT260_Interrupt_Level_Time_Delay(Enum):
    FT260_INTR_DELY_1MS = 1
    FT260_INTR_DELY_5MS = 2
    FT260_INTR_DELY_30MS = 3

class FT260_Suspend_Out_Polarity(Enum):
    FT260_SUSPEND_OUT_LEVEL_HIGH = 0
    FT260_SUSPEND_OUT_LEVEL_LOW = 1

class FT260_UART_Mode(Enum):
    FT260_UART_OFF = 0
    FT260_UART_RTS_CTS_MODE = 1        # hardware flow control RTS, CTS mode
    FT260_UART_DTR_DSR_MODE = 2        # hardware flow control DTR, DSR mode
    FT260_UART_XON_XOFF_MODE = 3       # software flow control mode
    FT260_UART_NO_FLOW_CTRL_MODE = 4    # no flow control mode

class FT260_Data_Bit(Enum):
    FT260_DATA_BIT_7 = 7
    FT260_DATA_BIT_8 = 8

class FT260_Stop_Bit(Enum):
    FT260_STOP_BITS_1 = 0
    FT260_STOP_BITS_2 = 2

class FT260_Parity(Enum):
    FT260_PARITY_NONE = 0
    FT260_PARITY_ODD = 1
    FT260_PARITY_EVEN = 2
    FT260_PARITY_MARK = 3
    FT260_PARITY_SPACE = 4

class FT260_RI_Wakeup_Type(Enum):
    FT260_RI_WAKEUP_RISING_EDGE = 0
    FT260_RI_WAKEUP_FALLING_EDGE = 1

'''
struct FT260_GPIO_Report
{
    WORD value;       # GPIO0~5 values
    WORD dir;         # GPIO0~5 directions
    WORD gpioN_value; # GPIOA~H values
    WORD gpioN_dir;   # GPIOA~H directions
};
'''
class FT260_GPIO_Report(Structure):
    _pack_ = 1
    _fields_ = [
                ('value', c_ushort),
                ('dir', c_ushort),
                ('gpioN_value', c_ushort),
                ('gpioN_dir', c_ushort),
                ]



class FT260_GPIO_DIR(Enum):
    FT260_GPIO_IN = 0
    FT260_GPIO_OUT = 1

class FT260_GPIO(Enum):
    FT260_GPIO_0 = 1 << 0
    FT260_GPIO_1 = 1 << 1
    FT260_GPIO_2 = 1 << 2
    FT260_GPIO_3 = 1 << 3
    FT260_GPIO_4 = 1 << 4
    FT260_GPIO_5 = 1 << 5
    FT260_GPIO_A = 1 << 6
    FT260_GPIO_B = 1 << 7
    FT260_GPIO_C = 1 << 8
    FT260_GPIO_D = 1 << 9
    FT260_GPIO_E = 1 << 10
    FT260_GPIO_F = 1 << 11
    FT260_GPIO_G = 1 << 12
    FT260_GPIO_H = 1 << 13

class FT260_I2C_FLAG(Enum):
    FT260_I2C_NONE  = 0
    FT260_I2C_START = 0x02
    FT260_I2C_REPEATED_START = 0x03
    FT260_I2C_STOP  = 0x04
    FT260_I2C_START_AND_STOP = 0x06

class FT260_PARAM_1(Enum):
    FT260_DS_CTL0 = 0x50
    FT260_DS_CTL3 = 0x51
    FT260_DS_CTL4 = 0x52
    FT260_SR_CTL0 = 0x53
    FT260_GPIO_PULL_UP    = 0x61
    FT260_GPIO_OPEN_DRAIN = 0x62
    FT260_GPIO_PULL_DOWN  = 0x63
    FT260_GPIO_GPIO_SLEW_RATE = 0x65

class FT260_PARAM_2(Enum):
    FT260_GPIO_GROUP_SUSPEND_0 = 0x10 # for gpio 0 ~ gpio 5
    FT260_GPIO_GROUP_SUSPEND_A = 0x11 # for gpio A ~ gpio H
    FT260_GPIO_DRIVE_STRENGTH = 0x64

'''
#pragma pack(push, 1)
typedef struct
{
    u8 flow_ctrl;
    u32 baud_rate;
    u8 data_bit;
    u8 parity;
    u8 stop_bit;
    u8 breaking;
} UartConfig;
#pragma pack(pop)
'''
class UartConfig(Structure):
    _pack_ = 1
    _fields_ = [
                ('flow_ctrl', c_uint8),
                ('baud_rate', c_uint32),
                ('data_bit', c_uint8),
                ('parity', c_uint8),
                ('stop_bit', c_uint8),
                ('breaking', c_uint8),
                ]



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
ftSetWakeupInterrupt.argtypes = (c_void_p, c_int)
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
ftEnableI2CPin.argtypes = (c_void_p, c_int)
ftEnableI2CPin.restype = c_int

ftSetUartToGPIOPin = ftlib.FT260_SetUartToGPIOPin
ftSetUartToGPIOPin.argtypes = (c_void_p)
ftSetUartToGPIOPin.restype = c_int

ftEnableDcdRiPin = ftlib.FT260_EnableDcdRiPin
ftEnableDcdRiPin.argtypes = (c_void_p, c_int)
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
ftI2CMaster_GetStatus.argtypes = (c_void_p, c_uint8_p)
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
ftUART_GetDcdRiStatus.argtypes = (c_void_p, c_uint8_p)
ftUART_GetDcdRiStatus.restype = c_int

ftUART_EnableRiWakeup = ftlib.FT260_UART_EnableRiWakeup
ftUART_EnableRiWakeup.argtypes = (c_void_p, c_int)
ftUART_EnableRiWakeup.restype = c_int

ftUART_SetRiWakeupConfig = ftlib.FT260_UART_SetRiWakeupConfig
ftUART_SetRiWakeupConfig.argtypes = (c_void_p, FT260_RI_Wakeup_Type type)
ftUART_SetRiWakeupConfig.restype = c_int


# Interrupt is transmitted by UART interface
ftGetInterruptFlag = ftlib.FT260_GetInterruptFlag
ftGetInterruptFlag.argtypes = (c_void_p, c_int_p)
ftGetInterruptFlag.restype = c_int

ftCleanInterruptFlag = ftlib.FT260_CleanInterruptFlag
ftCleanInterruptFlag.argtypes = (c_void_p, c_int_p)
ftCleanInterruptFlag.restype = c_int



# FT260 GPIO Functions
ftGPIO_Set = ftlib.FT260_GPIO_Set
ftGPIO_Set.argtypes = (c_void_p, FT260_GPIO_Report report)
ftGPIO_Set.restype = c_int

ftGPIO_Get = ftlib.FT260_GPIO_Get
ftGPIO_Get.argtypes = (c_void_p, FT260_GPIO_Report *report)
ftGPIO_Get.restype = c_int

ftGPIO_SetDir = ftlib.FT260_GPIO_SetDir
ftGPIO_SetDir.argtypes = (c_void_p, c_ushort, c_uchar)
ftGPIO_SetDir.restype = c_int

ftGPIO_Read = ftlib.FT260_GPIO_Read
ftGPIO_Read.argtypes = (c_void_p, c_ushort, c_uchar_p)
ftGPIO_Read.restype = c_int

ftGPIO_Write = ftlib.FT260_GPIO_Write
ftGPIO_Write.argtypes = (c_void_p, c_ushort, c_uchar)
ftGPIO_Write.restype = c_int

