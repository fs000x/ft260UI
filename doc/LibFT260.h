#ifndef _FTDI_LIB_FT260_H_
#define _FTDI_LIB_FT260_H_
//------------------------------------------------------------------------------
/**
 * Copyright © 2001-2015 Future Technology Devices International Limited
 *
 * THIS SOFTWARE IS PROVIDED BY FUTURE TECHNOLOGY DEVICES INTERNATIONAL LIMITED "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
 * OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL
 * FUTURE TECHNOLOGY DEVICES INTERNATIONAL LIMITED BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT
 * OF SUBSTITUTE GOODS OR SERVICES LOSS OF USE, DATA, OR PROFITS OR BUSINESS INTERRUPTION)
 * HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR
 * TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
 * EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 *
 * @file LibFT260.h
 *
 * @author FTDI
 * @date 2015-07-01
 *
 * Copyright © 2015 Future Technology Devices International Limited
 * Company Confidential
 *
 * Rivision History:
 * 1.0 - initial version
 *
 */

#include <stdio.h>
#include <windows.h>

#ifdef LIBFT260_EXPORTS
#define LIBFT260_API __declspec(dllexport)
#else
#define LIBFT260_API __declspec(dllimport)
#endif

typedef HANDLE FT260_HANDLE;

typedef unsigned char   uint8;
typedef unsigned short  uint16;
typedef unsigned long long uint64;

typedef unsigned char   u8;
typedef unsigned short  u16;
typedef unsigned long   u32;
typedef unsigned long long u64;

typedef signed char   int8;
typedef signed short  int16;
typedef signed long long int64;

#ifndef _MSC_VER
typedef unsigned char   BOOL;
#endif

#ifdef __x86_64__
typedef unsigned int uint32;
typedef signed int   int32;
#else
typedef unsigned long uint32;
typedef signed long   int32;
#endif

/* I2C Master Controller Status
 *   bit 0 = controller busy: all other status bits invalid
 *   bit 1 = error condition
 *   bit 2 = slave address was not acknowledged during last operation
 *   bit 3 = data not acknowledged during last operation
 *   bit 4 = arbitration lost during last operation
 *   bit 5 = controller idle
 *   bit 6 = bus busy
 */
#define I2CM_CONTROLLER_BUSY(status) (((status) & 0x01) != 0)
#define I2CM_DATA_NACK(status)       (((status) & 0x0A) != 0)
#define I2CM_ADDRESS_NACK(status)    (((status) & 0x06) != 0)
#define I2CM_ARB_LOST(status)        (((status) & 0x12) != 0)
#define I2CM_IDLE(status)            (((status) & 0x20) != 0)
#define I2CM_BUS_BUSY(status)        (((status) & 0x40) != 0)

enum FT260_STATUS
{
    FT260_OK,
    FT260_INVALID_HANDLE,
    FT260_DEVICE_NOT_FOUND,
    FT260_DEVICE_NOT_OPENED,
    FT260_DEVICE_OPEN_FAIL,
    FT260_DEVICE_CLOSE_FAIL,
    FT260_INCORRECT_INTERFACE,
    FT260_INCORRECT_CHIP_MODE,
    FT260_DEVICE_MANAGER_ERROR,
    FT260_IO_ERROR,
    FT260_INVALID_PARAMETER,
    FT260_NULL_BUFFER_POINTER,
    FT260_BUFFER_SIZE_ERROR,
    FT260_UART_SET_FAIL,
    FT260_RX_NO_DATA,
    FT260_GPIO_WRONG_DIRECTION,
    FT260_INVALID_DEVICE,
    FT260_OTHER_ERROR
};

enum FT260_GPIO2_Pin
{
    FT260_GPIO2_GPIO    = 0,
    FT260_GPIO2_SUSPOUT = 1,
    FT260_GPIO2_PWREN   = 2,
    FT260_GPIO2_TX_LED  = 4
};

enum FT260_GPIOA_Pin
{
    FT260_GPIOA_GPIO      = 0,
    FT260_GPIOA_TX_ACTIVE = 3,
    FT260_GPIOA_TX_LED    = 4
};

enum FT260_GPIOG_Pin
{
    FT260_GPIOG_GPIO     = 0,
    FT260_GPIOG_PWREN    = 2,
    FT260_GPIOG_RX_LED   = 5,
    FT260_GPIOG_BCD_DET  = 6
};

enum FT260_Clock_Rate
{
    FT260_SYS_CLK_12M = 0,
    FT260_SYS_CLK_24M,
    FT260_SYS_CLK_48M,
};

enum FT260_Interrupt_Trigger_Type
{
    FT260_INTR_RISING_EDGE = 0,
    FT260_INTR_LEVEL_HIGH,
    FT260_INTR_FALLING_EDGE,
    FT260_INTR_LEVEL_LOW
};

enum FT260_Interrupt_Level_Time_Delay
{
    FT260_INTR_DELY_1MS = 1,
    FT260_INTR_DELY_5MS,
    FT260_INTR_DELY_30MS
};

enum FT260_Suspend_Out_Polarity
{
    FT260_SUSPEND_OUT_LEVEL_HIGH = 0,
    FT260_SUSPEND_OUT_LEVEL_LOW
};

enum FT260_UART_Mode
{
    FT260_UART_OFF = 0,
    FT260_UART_RTS_CTS_MODE,        // hardware flow control RTS, CTS mode
    FT260_UART_DTR_DSR_MODE,        // hardware flow control DTR, DSR mode
    FT260_UART_XON_XOFF_MODE,       // software flow control mode
    FT260_UART_NO_FLOW_CTRL_MODE    // no flow control mode
};

enum FT260_Data_Bit
{
    FT260_DATA_BIT_7 = 7,
    FT260_DATA_BIT_8 = 8
};

enum FT260_Stop_Bit
{
    FT260_STOP_BITS_1 = 0,
    FT260_STOP_BITS_2 = 2
};

enum FT260_Parity
{
    FT260_PARITY_NONE = 0,
    FT260_PARITY_ODD,
    FT260_PARITY_EVEN,
    FT260_PARITY_MARK,
    FT260_PARITY_SPACE
};

enum FT260_RI_Wakeup_Type
{
    FT260_RI_WAKEUP_RISING_EDGE = 0,
    FT260_RI_WAKEUP_FALLING_EDGE,
};

struct FT260_GPIO_Report
{
    WORD value;       // GPIO0~5 values
    WORD dir;         // GPIO0~5 directions
    WORD gpioN_value; // GPIOA~H values
    WORD gpioN_dir;   // GPIOA~H directions
};

enum FT260_GPIO_DIR
{
    FT260_GPIO_IN = 0,
    FT260_GPIO_OUT
};

enum FT260_GPIO
{
    FT260_GPIO_0 = 1 << 0,
    FT260_GPIO_1 = 1 << 1,
    FT260_GPIO_2 = 1 << 2,
    FT260_GPIO_3 = 1 << 3,
    FT260_GPIO_4 = 1 << 4,
    FT260_GPIO_5 = 1 << 5,
    FT260_GPIO_A = 1 << 6,
    FT260_GPIO_B = 1 << 7,
    FT260_GPIO_C = 1 << 8,
    FT260_GPIO_D = 1 << 9,
    FT260_GPIO_E = 1 << 10,
    FT260_GPIO_F = 1 << 11,
    FT260_GPIO_G = 1 << 12,
    FT260_GPIO_H = 1 << 13
};

enum FT260_I2C_FLAG
{
    FT260_I2C_NONE  = 0,
    FT260_I2C_START = 0x02,
    FT260_I2C_REPEATED_START = 0x03,
    FT260_I2C_STOP  = 0x04,
    FT260_I2C_START_AND_STOP = 0x06
};

enum FT260_PARAM_1
{
    FT260_DS_CTL0 = 0x50,
    FT260_DS_CTL3 = 0x51,
    FT260_DS_CTL4 = 0x52,
    FT260_SR_CTL0 = 0x53,
    FT260_GPIO_PULL_UP    = 0x61,
    FT260_GPIO_OPEN_DRAIN = 0x62,
    FT260_GPIO_PULL_DOWN  = 0x63,
    FT260_GPIO_GPIO_SLEW_RATE = 0x65
};

enum FT260_PARAM_2
{
    FT260_GPIO_GROUP_SUSPEND_0 = 0x10, // for gpio 0 ~ gpio 5
    FT260_GPIO_GROUP_SUSPEND_A = 0x11, // for gpio A ~ gpio H
    FT260_GPIO_DRIVE_STRENGTH = 0x64
};

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

#ifdef __cplusplus
extern "C" {
#endif


// FT260 General Functions
LIBFT260_API FT260_STATUS WINAPI FT260_CreateDeviceList(LPDWORD lpdwNumDevs);
LIBFT260_API FT260_STATUS WINAPI FT260_GetDevicePath(WCHAR* pDevicePath, DWORD bufferLength, DWORD deviceIndex);
LIBFT260_API FT260_STATUS WINAPI FT260_Open(int iDevice, FT260_HANDLE* pFt260Handle);
LIBFT260_API FT260_STATUS WINAPI FT260_OpenByVidPid(WORD vid, WORD pid, DWORD deviceIndex, FT260_HANDLE* pFt260Handle);
LIBFT260_API FT260_STATUS WINAPI FT260_OpenByDevicePath(WCHAR* pDevicePath, FT260_HANDLE* pFt260Handle);
LIBFT260_API FT260_STATUS WINAPI FT260_Close(FT260_HANDLE ft260Handle);

LIBFT260_API FT260_STATUS WINAPI FT260_SetClock(FT260_HANDLE ft260Handle, FT260_Clock_Rate clk);
LIBFT260_API FT260_STATUS WINAPI FT260_SetWakeupInterrupt(FT260_HANDLE ft260Handle, BOOL enable);
LIBFT260_API FT260_STATUS WINAPI FT260_SetInterruptTriggerType(FT260_HANDLE ft260Handle, FT260_Interrupt_Trigger_Type type, FT260_Interrupt_Level_Time_Delay delay);
LIBFT260_API FT260_STATUS WINAPI FT260_SelectGpio2Function(FT260_HANDLE ft260Handle, FT260_GPIO2_Pin gpio2Function);
LIBFT260_API FT260_STATUS WINAPI FT260_SelectGpioAFunction(FT260_HANDLE ft260Handle, FT260_GPIOA_Pin gpioAFunction);
LIBFT260_API FT260_STATUS WINAPI FT260_SelectGpioGFunction(FT260_HANDLE ft260Handle, FT260_GPIOG_Pin gpioGFunction);
LIBFT260_API FT260_STATUS WINAPI FT260_SetSuspendOutPolarity(FT260_HANDLE ft260Handle, FT260_Suspend_Out_Polarity polarity);

LIBFT260_API FT260_STATUS WINAPI FT260_SetParam_U8(FT260_HANDLE ft260Handle, FT260_PARAM_1 param, uint8 value);
LIBFT260_API FT260_STATUS WINAPI FT260_SetParam_U16(FT260_HANDLE ft260Handle, FT260_PARAM_2 param, uint16 value);

LIBFT260_API FT260_STATUS WINAPI FT260_GetChipVersion(FT260_HANDLE ft260Handle, LPDWORD lpdwChipVersion);
LIBFT260_API FT260_STATUS WINAPI FT260_GetLibVersion(LPDWORD lpdwLibVersion);

LIBFT260_API FT260_STATUS WINAPI FT260_EnableI2CPin(FT260_HANDLE ft260Handle, BOOL enable);
LIBFT260_API FT260_STATUS WINAPI FT260_SetUartToGPIOPin(FT260_HANDLE ft260Handle);
LIBFT260_API FT260_STATUS WINAPI FT260_EnableDcdRiPin(FT260_HANDLE ft260Handle, BOOL enable);

// FT260 I2C Functions
LIBFT260_API FT260_STATUS WINAPI FT260_I2CMaster_Init(FT260_HANDLE ft260Handle, uint32 kbps);
LIBFT260_API FT260_STATUS WINAPI FT260_I2CMaster_Read(FT260_HANDLE ft260Handle, uint8 deviceAddress, FT260_I2C_FLAG flag, LPVOID lpBuffer, DWORD dwBytesToRead, LPDWORD lpdwBytesReturned);
LIBFT260_API FT260_STATUS WINAPI FT260_I2CMaster_Write(FT260_HANDLE ft260Handle, uint8 deviceAddress, FT260_I2C_FLAG flag, LPVOID lpBuffer, DWORD dwBytesToWrite, LPDWORD lpdwBytesWritten);
LIBFT260_API FT260_STATUS WINAPI FT260_I2CMaster_GetStatus(FT260_HANDLE ft260Handle, uint8* status);
LIBFT260_API FT260_STATUS WINAPI FT260_I2CMaster_Reset(FT260_HANDLE ft260Handle);


// FT260 UART Functions
LIBFT260_API FT260_STATUS WINAPI FT260_UART_Init(FT260_HANDLE ft260Handle);
LIBFT260_API FT260_STATUS WINAPI FT260_UART_SetBaudRate(FT260_HANDLE ft260Handle, ULONG baudRate);
LIBFT260_API FT260_STATUS WINAPI FT260_UART_SetFlowControl(FT260_HANDLE ft260Handle, FT260_UART_Mode flowControl);
LIBFT260_API FT260_STATUS WINAPI FT260_UART_SetDataCharacteristics(FT260_HANDLE ft260Handle, FT260_Data_Bit dataBits, FT260_Stop_Bit stopBits, FT260_Parity parity);
LIBFT260_API FT260_STATUS WINAPI FT260_UART_SetBreakOn(FT260_HANDLE ft260Handle);
LIBFT260_API FT260_STATUS WINAPI FT260_UART_SetBreakOff(FT260_HANDLE ft260Handle);
LIBFT260_API FT260_STATUS WINAPI FT260_UART_SetXonXoffChar(FT260_HANDLE ft260Handle, UCHAR Xon, UCHAR Xoff);
LIBFT260_API FT260_STATUS WINAPI FT260_UART_GetConfig(FT260_HANDLE ft260Handle, UartConfig* pUartConfig);
LIBFT260_API FT260_STATUS WINAPI FT260_UART_GetQueueStatus(FT260_HANDLE ft260Handle, LPDWORD lpdwAmountInRxQueue);
LIBFT260_API FT260_STATUS WINAPI FT260_UART_Read(FT260_HANDLE ft260Handle, LPVOID lpBuffer, DWORD dwBufferLength, DWORD dwBytesToRead, LPDWORD lpdwBytesReturned);
LIBFT260_API FT260_STATUS WINAPI FT260_UART_Write(FT260_HANDLE ft260Handle, LPVOID lpBuffer, DWORD dwBufferLength, DWORD dwBytesToWrite, LPDWORD lpdwBytesWritten);
LIBFT260_API FT260_STATUS WINAPI FT260_UART_Reset(FT260_HANDLE ft260Handle);

LIBFT260_API FT260_STATUS WINAPI FT260_UART_GetDcdRiStatus(FT260_HANDLE ft260Handle, uint8* value);
LIBFT260_API FT260_STATUS WINAPI FT260_UART_EnableRiWakeup(FT260_HANDLE ft260Handle, BOOL enable);
LIBFT260_API FT260_STATUS WINAPI FT260_UART_SetRiWakeupConfig(FT260_HANDLE ft260Handle, FT260_RI_Wakeup_Type type);

// Interrupt is transmitted by UART interface
LIBFT260_API FT260_STATUS WINAPI FT260_GetInterruptFlag(FT260_HANDLE ft260Handle, BOOL* pbFlag);
LIBFT260_API FT260_STATUS WINAPI FT260_CleanInterruptFlag(FT260_HANDLE ft260Handle, BOOL* pbFlag);


// FT260 GPIO Functions
LIBFT260_API FT260_STATUS WINAPI FT260_GPIO_Set(FT260_HANDLE ft260Handle, FT260_GPIO_Report report);
LIBFT260_API FT260_STATUS WINAPI FT260_GPIO_Get(FT260_HANDLE ft260Handle, FT260_GPIO_Report *report);
LIBFT260_API FT260_STATUS WINAPI FT260_GPIO_SetDir(FT260_HANDLE ft260Handle, WORD pinNum, BYTE dir);
LIBFT260_API FT260_STATUS WINAPI FT260_GPIO_Read(FT260_HANDLE ft260Handle, WORD pinNum, BYTE* pValue);
LIBFT260_API FT260_STATUS WINAPI FT260_GPIO_Write(FT260_HANDLE ft260Handle, WORD pinNum, BYTE value);

#ifdef __cplusplus
}
#endif


//------------------------------------------------------------------------------
#endif //_FTDI_LIB_FT260_H_
