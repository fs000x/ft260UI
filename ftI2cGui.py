import PySimpleGUI as sg

from ft_function import *
import signal
import struct


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
            print("find OpenDevice Name: %s\r\n" % pathBuf.value)
            ret = True
        print("Index:%d\r\nPath:%s\r\n\r\n" %(i, pathBuf.value))

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


def ftI2cConfig(handle, cfgRate=i2cCfgDef['rate']):
    # config i2cRateDef
    ftI2CMaster_Reset(handle)
    ftStatus = ftI2CMaster_Init(handle, cfgRate)
    if not ftStatus == FT260_STATUS.FT260_OK.value:
        print("I2c Init Failed, status: %s\r\n" % FT260_STATUS(ftStatus))
        return 0
    else:
        print("I2c Init OK")


def ftI2cWrite(handle, i2cDev=i2cDevDef, flag=i2cCfgDef['flag'], data=b''):
    # Write data
    dwRealAccessData = c_ulong(0)
    bufferData = c_char_p(bytes(data))
    buffer = cast(bufferData, c_void_p)
    ftStatus = ftI2CMaster_Write(handle, i2cDev, flag, buffer, len(data), byref(dwRealAccessData))
    if not ftStatus == FT260_STATUS.FT260_OK.value:
        print("I2c Write NG : %s\r\n" % FT260_STATUS(ftStatus))
    else:
        print("Write bytes : %d\r\n" % dwRealAccessData.value)


def ftI2cRead(handle, i2cDev=i2cDevDef, flag=i2cCfgDef['flag'], readLen=1):
    # Read data
    dwRealAccessData = c_ulong(0)
    bufferBytes = b'\0'*readLen
    buffer2Data = c_char_p(b'\0'*readLen)

    buffer2 = cast(buffer2Data, c_void_p)
    ftStatus = ftI2CMaster_Read(handle, i2cDev, flag, buffer2, readLen, byref(dwRealAccessData))
    if not ftStatus == FT260_STATUS.FT260_OK.value:
        print("UART Read NG : %s\r\n" % FT260_STATUS(ftStatus))
    else:
        bufferBytes = b'\0'
        print("Read bytes : %d\r\n" % dwRealAccessData.value)
        print(len(buffer2Data.value), buffer2Data, buffer2Data.value)
        print(bufferBytes)

    return buffer2Data.value




is_sigInt_up = False
def sigint_handler(sig, frame):
    print("SIGINT")
    global is_sigInt_up
    is_sigInt_up = True


def main():
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
                [sg.Text('Clock Rate', size=(10, 1)), sg.InputText(str(i2cCfgDef['rate']), size=(5,1), key="rate", do_not_clear=True)],
                    ]

    rwReg_lay = [
                [sg.Text('DevAddr', size=(10, 1)),sg.InputText(hex(i2cDevDef), size=(5,1), key="regDev", do_not_clear=True)],
                [sg.Text('Reg Bits', size=(10, 1)),sg.InputCombo([8, 16], default_value = 8, size=(2,1), key="regBits")],
                [sg.Text('Reg', size=(10, 1)),sg.InputText(hex(0), size=(5,1), key="reg", do_not_clear=True)],
                [sg.Text('Value Bits', size=(10, 1)),sg.InputCombo([8, 16, 32], default_value = 8, size=(2,1), key="valueBits")],
                [sg.Text('Value', size=(5, 1)),sg.InputText(hex(0), size=(12,1), key="regValue", do_not_clear=True)],
                [sg.ReadButton('RegRead', size=(8,1)), sg.ReadButton('RegWrite', size=(8,1))]
                ]
    rwData_lay = [
                [sg.Text('DevAddr', size=(10, 1)),sg.InputText(hex(i2cDevDef), size=(5,1), key="dataDev", do_not_clear=True)],
                [sg.Text('R/W Len', size=(10, 1)),sg.InputText('1', size=(5,1), key="dataLen", do_not_clear=True)],
                [sg.Text('Data', size=(5, 1)),sg.Multiline(hex(0), size=(12,1), key="data", do_not_clear=True)],
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
            print("Close i2c Handle")
            ftClose(i2cHandle)
            break # exit button clicked
        elif button == 'RegWrite':
            packstr = ['>', 'B', 'B']
            if int(value['regBits']) == 16:
                packstr[1] = 'H'
            if int(value['valueBits']) == 16:
                packstr[2] = 'H'
            elif int(value['valueBits']) == 32:
                packstr[2] = 'I'
            ftI2cWrite(i2cHandle, int(value["regDev"],16), FT260_I2C_FLAG[value["flag"]], struct.pack("".join(packstr), int(value['reg'],16), int(value['regValue'],16)))
        elif button == 'RegRead':
            packstr = ['>', 'B']
            unpackstr = ['>', 'B']
            readLen = 1
            if int(value['regBits']) == 16:
                packstr[1] = 'H'
            if int(value['valueBits']) == 16:
                readLen = 2
                unpackstr[1] = 'H'
            elif int(value['valueBits']) == 32:
                readLen = 4
                unpackstr[1] = 'I'
            ftI2cWrite(i2cHandle, int(value["regDev"],16), FT260_I2C_FLAG[value["flag"]], struct.pack("".join(packstr), int(value['reg'],16)))
            readData = ftI2cRead(i2cHandle, int(value["regDev"],16), FT260_I2C_FLAG[value["flag"]], readLen)
            print(len(readData), readData, unpackstr)
            if not len(readData) == 0:
                window.FindElement("regValue").Update("%#x" % struct.unpack("".join(unpackstr), readData))
            else:
                window.FindElement("regValue").Update("0x00")

        elif button == 'DataRead':
            updateStr = ""
            readData = ftI2cRead(i2cHandle, int(value["dataDev"],16), FT260_I2C_FLAG[value["flag"]], int(value['dataLen']))
            readLen = len(readData)
            unpackstr = "<"+"B"*readLen
            print(readLen, readData, unpackstr)
            if readLen == 0:
                updateStr = "0x00"
            else:
                for i in struct.unpack(unpackstr, readData):
                    updateStr = updateStr + " " + hex(i)
            window.FindElement("data").Update(updateStr)

        elif button == 'DataWrite':
            sg.Popup('The button clicked was "{}"'.format(button), 'The values are', value)



main()
