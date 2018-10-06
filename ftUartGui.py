import PySimpleGUI as sg
import subprocess

from ft_function import *
from threading import Thread
import time


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
    return handle


def ftUartWrite(handle, data):
    # Write data
    dwRealAccessData = c_ulong(0)
    bufferData = c_char_p(bytes(data,'utf-8'))
    buffer = cast(bufferData, c_void_p)
    ftStatus = ftUART_Write(handle, buffer, len(data), len(data), byref(dwRealAccessData))
    if not ftStatus == FT260_STATUS.FT260_OK.value:
        print("UART Write NG : %s\r\n" % FT260_STATUS(ftStatus))
    else:
        print("Write bytes : %d\r\n" % dwRealAccessData.value)



class ftUartReadLoop:

    def __init__(self, handle):
        self._handle = handle
        self._running = True

    def stop(self):
        self._running = False

    def run(self):
        while self._running:
            # Read data
            dwRealAccessData = c_ulong(0)
            dwAvailableData = c_ulong(0)
            buffer2Data = c_char_p(b'\0'*200)
            memset(buffer2Data, 0, 200)
            buffer2 = cast(buffer2Data, c_void_p)
            ftUART_GetQueueStatus(self._handle, byref(dwAvailableData))
            if dwAvailableData.value == 0:
                continue
            print("dwAvailableData : %d\r\n" % dwAvailableData.value)

            ftStatus = ftUART_Read(self._handle, buffer2, 50, dwAvailableData, byref(dwRealAccessData))
            if not ftStatus == FT260_STATUS.FT260_OK.value:
                print("UART Read NG : %s\r\n" % FT260_STATUS(ftStatus))
            else:
                buffer2Data = cast(buffer2, c_char_p)
                print("Read bytes : %d\r\n" % dwRealAccessData.value)
                if dwAvailableData.value > 0:
                    print("buffer : %s\r\n" % buffer2Data.value.decode("utf-8"))

        time.sleep(1)



if not findDeviceInPaths(FT260_Vid, FT260_Vid):
    sg.Popup("No FT260 Device")
    exit()

uartHandle = openFtAsUart(FT260_Vid, FT260_Pid)
print(uartHandle)
if not uartHandle:
    sg.Popup("open uartHandle error")
    exit()

ftUartR = ftUartReadLoop(uartHandle)
tr = Thread(target=ftUartR.run)
tr.start()


layout = [
    [sg.Text('Uart output....', size=(40, 1))],
    [sg.Output(size=(88, 20))],
    [sg.Text('Uart Input', size=(15, 1)), sg.InputText(focus=True), sg.ReadButton('Send', bind_return_key=True)]
        ]


window = sg.Window('FT260 UART').Layout(layout)

# ---===--- Loop taking in user input and using it to call scripts --- #
while True:
  (button, value) = window.Read()
  if button is None:
      print("Close Uart Handle")
      ftUartR.stop()
      ftClose(uartHandle)
      #time.sleep(1)
      tr.join()
      break # exit button clicked
  elif button == 'Send':
      ftUartWrite(uartHandle, value[0])