import PySimpleGUI as sg
import subprocess
import logging

from ft_function import *
from threading import Thread
import time
import signal


FT260_Vid = 0x0403
FT260_Pid = 0x6030

i2cCfgDef = {
    'flag': FT260_I2C_FLAG.FT260_I2C_START_AND_STOP,
    'rate': 100
}
i2cDevDef = 0x1E

def findDeviceInPaths(Vid, Pid):
    devNum = c_ulong(0)
    pathBuf = c_wchar_p('/0'*128)
    sOpenDeviceName = u"vid_{0:04x}&pid_{1:04x}&mi_00".format(Vid, Pid)
    ret = False

    ftCreateDeviceList(byref(devNum))
    for i in range(devNum.value):
        ftGetDevicePath(pathBuf, 128, i)
        if pathBuf.value.find(sOpenDeviceName) > 0:
            logging.info("find OpenDevice Name: %s\r\n" % pathBuf.value)
            ret = True
        logging.info("Index:%d\r\nPath:%s\r\n\r\n" %(i, pathBuf.value))

    return ret


def openFtAsI2c(Vid, Pid):
    ftStatus = c_int(0)
    handle = c_void_p()

    # mode 0 is I2C, mode 1 is UART
    ftStatus = ftOpenByVidPid(FT260_Vid, FT260_Pid, 0, byref(handle))
    if not ftStatus == FT260_STATUS.FT260_OK.value:
        logging.warning("Open device Failed, status: %s\r\n" % FT260_STATUS(ftStatus))
        return 0
    else:
        logging.info("Open device OK")

    ftStatus = ftI2CMaster_Init(handle, i2cCfgDef['rate'])
    if not ftStatus == FT260_STATUS.FT260_OK.value:
        logging.error("I2c Init Failed, status: %s\r\n" % FT260_STATUS(ftStatus))
        return 0
    else:
        logging.info("I2c Init OK")

    return handle


def ftI2cConfig(handle, cfgRate=i2cCfgDef['rate']):
    # config i2cRateDef
    ftI2CMaster_Reset(handle)
    ftStatus = ftI2CMaster_Init(handle, cfgRate)
    if not ftStatus == FT260_STATUS.FT260_OK.value:
        logging.error("I2c Init Failed, status: %s\r\n" % FT260_STATUS(ftStatus))
        return 0
    else:
        logging.info("I2c Init OK")


def ftI2cWrite(handle, i2cDev=i2cDevDef, flag=i2cCfgDef['flag'], data=''):
    # Write data
    dwRealAccessData = c_ulong(0)
    bufferData = c_char_p(bytes(data,'ascii'))
    buffer = cast(bufferData, c_void_p)
    ftStatus = ftI2CMaster_Write(handle, i2cDev, flag, buffer, len(data), byref(dwRealAccessData))
    if not ftStatus == FT260_STATUS.FT260_OK.value:
        logging.warning("I2c Write NG : %s\r\n" % FT260_STATUS(ftStatus))
    else:
        logging.info("Write bytes : %d\r\n" % dwRealAccessData.value)


def ftI2cRead(handle, i2cDev=i2cDevDef, flag=i2cCfgDef['flag'], readLen=0):
    # Read data
    dwRealAccessData = c_ulong(0)
    buffer2Data = c_char_p(b'\0'*200)
    buffer2 = cast(buffer2Data, c_void_p)
    ftStatus = ftI2CMaster_Read(handle, i2cDev, flag, buffer2, readLen, byref(dwRealAccessData))
    if not ftStatus == FT260_STATUS.FT260_OK.value:
        logging.warning("UART Write NG : %s\r\n" % FT260_STATUS(ftStatus))
    else:
        logging.info("Write bytes : %d\r\n" % dwRealAccessData.value)




is_sigInt_up = False
def sigint_handler(sig, frame):
    logging.info("SIGINT")
    global is_sigInt_up
    is_sigInt_up = True


def main():
    logging.basicConfig(filename='ftI2c.log', level=logging.INFO)
    if not findDeviceInPaths(FT260_Vid, FT260_Pid):
        sg.Popup("No FT260 Device")
        exit()

    i2cHandle = openFtAsI2c(FT260_Vid, FT260_Pid)
    if not i2cHandle:
        sg.Popup("open i2cHandle error")
        exit()

    signal.signal(signal.SIGINT, sigint_handler)

    leftFrame = [[sg.Output(size=(30, 30))]]

    cfgFrame_lay = [
                [sg.Text('I2C Flag', size=(10, 1)), sg.InputCombo([i.name for i in FT260_I2C_FLAG], default_value = i2cCfgDef['flag'].name, size=(30,1), key="flag")],
                [sg.Text('Clock Rate', size=(10, 1)), sg.InputText(str(i2cCfgDef['rate']), size=(5,1), key="rate")],
                    ]

    rwReg_lay = [
                [sg.Text('DevAddr', size=(10, 1)),sg.InputText(size=(5,1), key="regDev", do_not_clear=True)],
                [sg.Text('Reg Bits', size=(10, 1)),sg.InputCombo([8, 16], default_value = 8, size=(2,1), key="regBits")],
                [sg.Text('Reg', size=(10, 1)),sg.InputText(size=(5,1), key="reg", do_not_clear=True)],
                [sg.Text('Value Bits', size=(10, 1)),sg.InputCombo([8, 16, 32], default_value = 8, size=(2,1), key="valueBits")],
                [sg.Text('Value', size=(5, 1)),sg.InputText(size=(12,1), key="regValue", do_not_clear=True)],
                [sg.ReadButton('RegRead', size=(8,1)), sg.ReadButton('RegWrite', size=(8,1))]
                ]
    rwData_lay = [
                [sg.Text('DevAddr', size=(10, 1)),sg.InputText(size=(5,1), key="dataDev", do_not_clear=True)],
                [sg.Text('R/W Len', size=(10, 1)),sg.InputText(size=(5,1), key="dataLen", do_not_clear=True)],
                [sg.Text('Data', size=(5, 1)),sg.Multiline(size=(12,1), key="data", do_not_clear=True)],
                [sg.ReadButton('DataRead', size=(8,1)), sg.ReadButton('DataWrite', size=(9,1))]
                ]
    rightFrame = [
                [sg.Frame("Config", cfgFrame_lay, size=(50, 30))],
                [sg.Frame("Read&Write Reg", rwReg_lay, size=(50, 30)), sg.Frame("Read&Write Data", rwData_lay)]
                ]

    layout = [
        [sg.Frame('Log', leftFrame, size=(30, 30)), sg.Frame('', rightFrame, size=(130, 5))]
            ]


    window = sg.Window('FT260 I2C').Layout(layout)

    # ---===--- Loop taking in user input and using it to call scripts --- #
    while True:
        (button, value) = window.Read()
        #sg.Popup('The button clicked was "{}"'.format(button), 'The values are', value)
        global is_sigInt_up
        if is_sigInt_up or button is None: # window.Read will block
            logging.info("Close i2c Handle")
            ftClose(i2cHandle)
            break # exit button clicked
        elif button == 'Send':
            ftI2cWrite(i2cHandle, int(value["dev"]), FT260_I2C_FLAG[value["flag"]], value["value"])
        #elif button in [ i for i in i2cCfgDef]:
        #    ftUartConfig(i2cHandle, cfgDit=uartCfg)



main()
