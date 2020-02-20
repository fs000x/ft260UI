"""
Wrapper for LibFT260 using ctypes
"""

from ctypes import *
from enum import *


class FTlib():
    def __init__(self, libpath):
        self.ftlib = windll.LoadLibrary(libpath)
        # FT260 General Functions
        self.ftCreateDeviceList = self.ftlib.FT260_CreateDeviceList
        self.ftCreateDeviceList.argtypes = [POINTER(c_ulong)]
        self.ftCreateDeviceList.restype = c_int

        self.ftGetDevicePath = self.ftlib.FT260_GetDevicePath
        self.ftGetDevicePath.argtypes = [POINTER(c_wchar), c_ulong, c_ulong]
        self.ftGetDevicePath.restype = c_int

        self.ftOpen = self.ftlib.FT260_Open
        self.ftOpen.argtypes = [c_int, POINTER(c_void_p)]
        self.ftOpen.restype = c_int

        self.ftOpenByVidPid = self.ftlib.FT260_OpenByVidPid
        self.ftOpenByVidPid.argtypes = [c_ushort, c_ushort, c_ulong, POINTER(c_void_p)]
        self.ftOpenByVidPid.restype = c_int

        self.ftOpenByDevicePath = self.ftlib.FT260_OpenByDevicePath
        self.ftOpenByDevicePath.argtypes = [POINTER(c_wchar), POINTER(c_void_p)]
        self.ftOpenByDevicePath.restype = c_int

        self.ftClose = self.ftlib.FT260_Close
        self.ftClose.argtypes = [c_void_p]
        self.ftClose.restype = c_int

        self.ftSetClock = self.ftlib.FT260_SetClock
        self.ftSetClock.argtypes = [c_void_p, FT260_Clock_Rate]
        self.ftSetClock.restype = c_int

        self.ftSetWakeupInterrupt = self.ftlib.FT260_SetWakeupInterrupt
        self.ftSetWakeupInterrupt.argtypes = [c_void_p, c_int]
        self.ftSetWakeupInterrupt.restype = c_int

        self.ftSetInterruptTriggerType = self.ftlib.FT260_SetInterruptTriggerType
        self.ftSetInterruptTriggerType.argtypes = [c_void_p, FT260_Interrupt_Trigger_Type, FT260_Interrupt_Level_Time_Delay]
        self.ftSetInterruptTriggerType.restype = c_int

        self.ftSelectGpio2Function = self.ftlib.FT260_SelectGpio2Function
        self.ftSelectGpio2Function.argtypes = [c_void_p, FT260_GPIO2_Pin]
        self.ftSelectGpio2Function.restype = c_int

        self.ftSelectGpioAFunction = self.ftlib.FT260_SelectGpioAFunction
        self.ftSelectGpioAFunction.argtypes = [c_void_p, FT260_GPIOA_Pin]
        self.ftSelectGpioAFunction.restype = c_int

        self.ftSelectGpioGFunction = self.ftlib.FT260_SelectGpioGFunction
        self.ftSelectGpioGFunction.argtypes = [c_void_p, FT260_GPIOG_Pin]
        self.ftSelectGpioGFunction.restype = c_int

        self.ftSetSuspendOutPolarity = self.ftlib.FT260_SetSuspendOutPolarity
        self.ftSetSuspendOutPolarity.argtypes = [c_void_p, FT260_Suspend_Out_Polarity]
        self.ftSetSuspendOutPolarity.restype = c_int

        self.ftSetParam_U8 = self.ftlib.FT260_SetParam_U8
        self.ftSetParam_U8.argtypes = [c_void_p, FT260_PARAM_1, c_uint8]
        self.ftSetParam_U8.restype = c_int

        self.ftSetParam_U16 = self.ftlib.FT260_SetParam_U16
        self.ftSetParam_U16.argtypes = [c_void_p, FT260_PARAM_2, c_uint16]
        self.ftSetParam_U16.restype = c_int

        self.ftGetChipVersion = self.ftlib.FT260_GetChipVersion
        self.ftGetChipVersion.argtypes = [c_void_p, POINTER(c_ulong)]
        self.ftGetChipVersion.restype = c_int

        self.ftGetLibVersion = self.ftlib.FT260_GetLibVersion
        self.ftGetLibVersion.argtypes = [POINTER(c_ulong)]
        self.ftGetLibVersion.restype = c_int

        self.ftEnableI2CPin = self.ftlib.FT260_EnableI2CPin
        self.ftEnableI2CPin.argtypes = [c_void_p, c_int]
        self.ftEnableI2CPin.restype = c_int

        self.ftSetUartToGPIOPin = self.ftlib.FT260_SetUartToGPIOPin
        self.ftSetUartToGPIOPin.argtypes = [c_void_p]
        self.ftSetUartToGPIOPin.restype = c_int

        self.ftEnableDcdRiPin = self.ftlib.FT260_EnableDcdRiPin
        self.ftEnableDcdRiPin.argtypes = [c_void_p, c_int]
        self.ftEnableDcdRiPin.restype = c_int

        # FT260 I2C Functions
        self.ftI2CMaster_Init = self.ftlib.FT260_I2CMaster_Init
        self.ftI2CMaster_Init.argtypes = [c_void_p, c_uint32]
        self.ftI2CMaster_Init.restype = c_int

        self.ftI2CMaster_Read = self.ftlib.FT260_I2CMaster_Read
        self.ftI2CMaster_Read.argtypes = [c_void_p, c_uint8, FT260_I2C_FLAG, c_void_p, c_ulong, POINTER(c_ulong)]
        self.ftI2CMaster_Read.restype = c_int

        self.ftI2CMaster_Write = self.ftlib.FT260_I2CMaster_Write
        self.ftI2CMaster_Write.argtypes = [c_void_p, c_uint8, FT260_I2C_FLAG, c_void_p, c_ulong, POINTER(c_ulong)]
        self.ftI2CMaster_Write.restype = c_int

        self.ftI2CMaster_GetStatus = self.ftlib.FT260_I2CMaster_GetStatus
        self.ftI2CMaster_GetStatus.argtypes = [c_void_p, POINTER(c_uint8)]
        self.ftI2CMaster_GetStatus.restype = c_int

        self.ftI2CMaster_Reset = self.ftlib.FT260_I2CMaster_Reset
        self.ftI2CMaster_Reset.argtypes = [c_void_p]
        self.ftI2CMaster_Reset.restype = c_int

        # FT260 UART Functions
        self.ftUART_Init = self.ftlib.FT260_UART_Init
        self.ftUART_Init.argtypes = [c_void_p]
        self.ftUART_Init.restype = c_int

        self.self.ftUART_SetBaudRate = self.ftlib.FT260_UART_SetBaudRate
        self.ftUART_SetBaudRate.argtypes = [c_void_p, c_ulong]
        self.ftUART_SetBaudRate.restype = c_int

        self.ftUART_SetFlowControl = self.ftlib.FT260_UART_SetFlowControl
        self.ftUART_SetFlowControl.argtypes = [c_void_p, FT260_UART_Mode]
        self.ftUART_SetFlowControl.restype = c_int

        self.ftUART_SetDataCharacteristics = self.ftlib.FT260_UART_SetDataCharacteristics
        self.ftUART_SetDataCharacteristics.argtypes = [c_void_p, FT260_Data_Bit, FT260_Stop_Bit, FT260_Parity]
        self.ftUART_SetDataCharacteristics.restype = c_int

        self.ftUART_SetBreakOn = self.ftlib.FT260_UART_SetBreakOn
        self.ftUART_SetBreakOn.argtypes = [c_void_p]
        self.ftUART_SetBreakOn.restype = c_int

        self.ftUART_SetBreakOff = self.ftlib.FT260_UART_SetBreakOff
        self.ftUART_SetBreakOff.argtypes = [c_void_p]
        self.ftUART_SetBreakOff.restype = c_int

        self.ftUART_SetXonXoffChar = self.ftlib.FT260_UART_SetXonXoffChar
        self.ftUART_SetXonXoffChar.argtypes = [c_void_p, c_ubyte, c_ubyte]
        self.ftUART_SetXonXoffChar.restype = c_int

        self.ftUART_GetConfig = self.ftlib.FT260_UART_GetConfig
        self.ftUART_GetConfig.argtypes = [c_void_p, POINTER(UartConfig)]
        self.ftUART_GetConfig.restype = c_int

        self.ftUART_GetQueueStatus = self.ftlib.FT260_UART_GetQueueStatus
        self.ftUART_GetQueueStatus.argtypes = [c_void_p, POINTER(c_ulong)]
        self.ftUART_GetQueueStatus.restype = c_int

        self.ftUART_Read = self.ftlib.FT260_UART_Read
        self.ftUART_Read.argtypes = [c_void_p, c_void_p, c_ulong, c_ulong, POINTER(c_ulong)]
        self.ftUART_Read.restype = c_int

        self.ftUART_Write = self.ftlib.FT260_UART_Write
        self.ftUART_Write.argtypes = [c_void_p, c_void_p, c_ulong, c_ulong, POINTER(c_ulong)]
        self.ftUART_Write.restype = c_int

        self.ftUART_Reset = self.ftlib.FT260_UART_Reset
        self.ftUART_Reset.argtypes = [c_void_p]
        self.ftUART_Reset.restype = c_int

        self.ftUART_GetDcdRiStatus = self.ftlib.FT260_UART_GetDcdRiStatus
        self.ftUART_GetDcdRiStatus.argtypes = [c_void_p, POINTER(c_uint8)]
        self.ftUART_GetDcdRiStatus.restype = c_int

        self.ftUART_EnableRiWakeup = self.ftlib.FT260_UART_EnableRiWakeup
        self.ftUART_EnableRiWakeup.argtypes = [c_void_p, c_int]
        self.ftUART_EnableRiWakeup.restype = c_int

        self.ftUART_SetRiWakeupConfig = self.ftlib.FT260_UART_SetRiWakeupConfig
        self.ftUART_SetRiWakeupConfig.argtypes = [c_void_p, FT260_RI_Wakeup_Type]
        self.ftUART_SetRiWakeupConfig.restype = c_int

        # Interrupt is transmitted by UART interface
        self.ftGetInterruptFlag = self.ftlib.FT260_GetInterruptFlag
        self.ftGetInterruptFlag.argtypes = [c_void_p, POINTER(c_int)]
        self.ftGetInterruptFlag.restype = c_int

        self.ftCleanInterruptFlag = self.ftlib.FT260_CleanInterruptFlag
        self.ftCleanInterruptFlag.argtypes = [c_void_p, POINTER(c_int)]
        self.ftCleanInterruptFlag.restype = c_int

        # FT260 GPIO Functions
        self.ftGPIO_Set = self.ftlib.FT260_GPIO_Set
        self.ftGPIO_Set.argtypes = [c_void_p, FT260_GPIO_Report]
        self.ftGPIO_Set.restype = c_int

        self.ftGPIO_Get = self.ftlib.FT260_GPIO_Get
        self.ftGPIO_Get.argtypes = [c_void_p, POINTER(FT260_GPIO_Report)]
        self.ftGPIO_Get.restype = c_int

        self.ftGPIO_SetDir = self.ftlib.FT260_GPIO_SetDir
        self.ftGPIO_SetDir.argtypes = [c_void_p, c_ushort, c_ubyte]
        self.ftGPIO_SetDir.restype = c_int

        self.ftGPIO_Read = self.ftlib.FT260_GPIO_Read
        self.ftGPIO_Read.argtypes = [c_void_p, c_ushort, POINTER(c_ubyte)]
        self.ftGPIO_Read.restype = c_int

        self.ftGPIO_Write = self.ftlib.FT260_GPIO_Write
        self.ftGPIO_Write.argtypes = [c_void_p, c_ushort, c_ubyte]
        self.ftGPIO_Write.restype = c_int


# bits mask
BIT0 = 0x01
BIT1 = 0x02
BIT2 = 0x04
BIT3 = 0x08
BIT4 = 0x10
BIT5 = 0x20
BIT6 = 0x40
BIT7 = 0x80

# I2C master status bit masks
FT260_I2C_STATUS_CONTROLLER_BUSY = BIT0
FT260_I2C_STATUS_ERROR_CONDITION = BIT1
FT260_I2C_STATUS_SLAVE_NACK = BIT2
FT260_I2C_STATUS_DATA_NACK = BIT3
FT260_I2C_STATUS_ARBITRATION_LOST = BIT4
FT260_I2C_STATUS_CONTROLLER_IDLE = BIT5
FT260_I2C_STATUS_BUS_BUSY = BIT6

class CtypesEnum(IntEnum):
    """A ctypes-compatible IntEnum superclass."""

    @classmethod
    def from_param(cls, obj):
        return int(obj)


class FT260_STATUS(CtypesEnum):
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


class FT260_GPIO2_Pin(CtypesEnum):
    FT260_GPIO2_GPIO = 0
    FT260_GPIO2_SUSPOUT = 1
    FT260_GPIO2_PWREN = 2
    FT260_GPIO2_TX_LED = 4


class FT260_GPIOA_Pin(CtypesEnum):
    FT260_GPIOA_GPIO = 0
    FT260_GPIOA_TX_ACTIVE = 3
    FT260_GPIOA_TX_LED = 4


class FT260_GPIOG_Pin(CtypesEnum):
    FT260_GPIOG_GPIO = 0
    FT260_GPIOG_PWREN = 2
    FT260_GPIOG_RX_LED = 5
    FT260_GPIOG_BCD_DET = 6


class FT260_Clock_Rate(CtypesEnum):
    FT260_SYS_CLK_12M = 0
    FT260_SYS_CLK_24M = 1
    FT260_SYS_CLK_48M = 2


class FT260_Interrupt_Trigger_Type(CtypesEnum):
    FT260_INTR_RISING_EDGE = 0
    FT260_INTR_LEVEL_HIGH = 1
    FT260_INTR_FALLING_EDGE = 2
    FT260_INTR_LEVEL_LOW = 3


class FT260_Interrupt_Level_Time_Delay(CtypesEnum):
    FT260_INTR_DELY_1MS = 1
    FT260_INTR_DELY_5MS = 2
    FT260_INTR_DELY_30MS = 3


class FT260_Suspend_Out_Polarity(CtypesEnum):
    FT260_SUSPEND_OUT_LEVEL_HIGH = 0
    FT260_SUSPEND_OUT_LEVEL_LOW = 1


class FT260_UART_Mode(CtypesEnum):
    FT260_UART_OFF = 0
    FT260_UART_RTS_CTS_MODE = 1  # hardware flow control RTS, CTS mode
    FT260_UART_DTR_DSR_MODE = 2  # hardware flow control DTR, DSR mode
    FT260_UART_XON_XOFF_MODE = 3  # software flow control mode
    FT260_UART_NO_FLOW_CTRL_MODE = 4  # no flow control mode


class FT260_Data_Bit(CtypesEnum):
    FT260_DATA_BIT_7 = 7
    FT260_DATA_BIT_8 = 8


class FT260_Stop_Bit(CtypesEnum):
    FT260_STOP_BITS_1 = 0
    FT260_STOP_BITS_2 = 2


class FT260_Parity(CtypesEnum):
    FT260_PARITY_NONE = 0
    FT260_PARITY_ODD = 1
    FT260_PARITY_EVEN = 2
    FT260_PARITY_MARK = 3
    FT260_PARITY_SPACE = 4


class FT260_RI_Wakeup_Type(CtypesEnum):
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


class FT260_GPIO_DIR(CtypesEnum):
    FT260_GPIO_IN = 0
    FT260_GPIO_OUT = 1


class FT260_GPIO(CtypesEnum):
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


class FT260_I2C_FLAG(CtypesEnum):
    FT260_I2C_NONE = 0
    FT260_I2C_START = 0x02
    FT260_I2C_REPEATED_START = 0x03
    FT260_I2C_STOP = 0x04
    FT260_I2C_START_AND_STOP = 0x06


class FT260_PARAM_1(CtypesEnum):
    FT260_DS_CTL0 = 0x50
    FT260_DS_CTL3 = 0x51
    FT260_DS_CTL4 = 0x52
    FT260_SR_CTL0 = 0x53
    FT260_GPIO_PULL_UP = 0x61
    FT260_GPIO_OPEN_DRAIN = 0x62
    FT260_GPIO_PULL_DOWN = 0x63
    FT260_GPIO_GPIO_SLEW_RATE = 0x65


class FT260_PARAM_2(CtypesEnum):
    FT260_GPIO_GROUP_SUSPEND_0 = 0x10  # for gpio 0 ~ gpio 5
    FT260_GPIO_GROUP_SUSPEND_A = 0x11  # for gpio A ~ gpio H
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

