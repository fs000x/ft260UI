# TODO - remove PysimpleGUI
import PySimpleGUI as sg

# import FT260_I2C_FLAG, FT260_STATUS, ftI2CMaster_Init, ftOpenByVidPid, ftI2CMaster_Write, ftI2CMaster_Read and more
from ft_function import *
import ft
import signal
import struct

# TODO - remove multiprocessing after PysimpleGUI is removed
import multiprocessing

FT260_Vid = 0x0403
FT260_Pid = 0x6030


is_sigInt_up = False


def sigint_handler(sig, frame):
    print("SIGINT")
    global is_sigInt_up
    is_sigInt_up = True


def main():
    if not ft.findDeviceInPaths(FT260_Vid, FT260_Pid):
        sg.Popup("No FT260 Device")
        exit()

    i2cHandle = ft.openFtAsI2c(FT260_Vid, FT260_Pid)
    if not i2cHandle:
        sg.Popup("open i2cHandle error")
        exit()

    signal.signal(signal.SIGINT, sigint_handler)

    leftFrame = [[sg.Output(size=(30, 30))]]

    cfgFrame_lay = [
        [sg.Text('I2C Flag', size=(10, 1)),
         sg.InputCombo([i.name for i in FT260_I2C_FLAG], default_value=FT260_I2C_FLAG.FT260_I2C_START_AND_STOP, size=(30, 1),
                       key="flag")],
        [sg.Text('Clock Rate', size=(10, 1)),
         sg.InputText(str(100), size=(5, 1), key="rate", do_not_clear=True)],
    ]

    rwReg_lay = [
        [sg.Text('DevAddr', size=(10, 1)), sg.InputText(hex(0), size=(5, 1), key="regDev", do_not_clear=True)],
        [sg.Text('Reg Bits', size=(10, 1)), sg.InputCombo([8, 16], default_value=8, size=(2, 1), key="regBits")],
        [sg.Text('Reg', size=(10, 1)), sg.InputText(hex(0), size=(5, 1), key="reg", do_not_clear=True)],
        [sg.Text('Value Bits', size=(10, 1)),
         sg.InputCombo([8, 16, 32], default_value=8, size=(2, 1), key="valueBits")],
        [sg.Text('Value', size=(5, 1)), sg.InputText(hex(0), size=(12, 1), key="regValue", do_not_clear=True)],
        [sg.ReadButton('RegRead', size=(8, 1)), sg.ReadButton('RegWrite', size=(8, 1))]
    ]
    rwData_lay = [
        [sg.Text('DevAddr', size=(10, 1)), sg.InputText(hex(0), size=(5, 1), key="dataDev", do_not_clear=True)],
        [sg.Text('Read length', size=(10, 1)), sg.InputText('1', size=(5, 1), key="dataLen", do_not_clear=True)],
        [sg.Text('Data', size=(5, 1)), sg.Multiline(hex(0), size=(12, 1), key="data", do_not_clear=True)],
        [sg.ReadButton('DataRead', size=(8, 1)), sg.ReadButton('DataWrite', size=(9, 1))]
    ]
    rightFrame = [
        [sg.Frame("Config", cfgFrame_lay, size=(50, 30))],
        [sg.Frame("Read&Write Reg", rwReg_lay, size=(50, 30)), sg.Frame("Read&Write Data", rwData_lay)]
    ]

    layout = [
        [sg.Frame('Log', leftFrame, size=(30, 30)), sg.Frame('', rightFrame, size=(130, 5))]
    ]

    window = sg.Window('FT260 I2C').Layout(layout)

    q = multiprocessing.Queue()
    process_comm_log = multiprocessing.Process(target=ft.run_log, args=[q,])
    process_comm_log.start()

    # ---===--- Loop taking in user input and using it to call scripts --- #
    while True:
        (button, value) = window.Read()
        # sg.Popup('The button clicked was "{}"'.format(button), 'The values are', value)
        global is_sigInt_up
        if is_sigInt_up or button is None:  # window.Read will block
            print("Close i2c Handle")
            ftClose(i2cHandle)
            break  # exit button clicked
        elif button == 'RegWrite':
            packstr = ['>', 'B', 'B']
            if int(value['regBits']) == 16:
                packstr[1] = 'H'
            if int(value['valueBits']) == 16:
                packstr[2] = 'H'
            elif int(value['valueBits']) == 32:
                packstr[2] = 'I'
            ft.ftI2cWrite(i2cHandle, int(value["regDev"], 16), FT260_I2C_FLAG[value["flag"]],
                       struct.pack("".join(packstr), int(value['reg'], 16), int(value['regValue'], 16)))
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
            ft.ftI2cWrite(i2cHandle, int(value["regDev"], 16), FT260_I2C_FLAG[value["flag"]],
                       struct.pack("".join(packstr), int(value['reg'], 16)))
            (status, data_real_read_len, readData) = ft.ftI2cRead(i2cHandle, int(value["regDev"], 16), FT260_I2C_FLAG[value["flag"]], readLen)
            print(len(readData), readData, unpackstr)
            if not len(readData) == 0:
                window.FindElement("regValue").Update("%#x" % struct.unpack("".join(unpackstr), readData))
            else:
                window.FindElement("regValue").Update("0x00")

        elif button == 'DataRead':
            updateStr = ""
            (status, data_real_read_len, readData) = ft.ftI2cRead(i2cHandle, int(value["dataDev"], 16), FT260_I2C_FLAG[value["flag"]],
                                 int(value['dataLen']))

            # Error checking
            if data_real_read_len != len(readData):
                print("Read {} bytes from ft260 lib, but {} bytes are in buffer".format(data_real_read_len, len(readData)))
            elif not status == FT260_STATUS.FT260_OK.value:
                print("Read error : %s\r\n" % status)

            unpackstr = "<" + "B" * len(readData)
            for i in struct.unpack(unpackstr, readData):
                updateStr = updateStr + " " + hex(i)
                if not q.full():
                    q.put(['Read', value["dataDev"], hex(i)])
            window.FindElement("data").Update(updateStr)

        elif button == 'DataWrite':
            updateStr = ""
            data_to_write = value["data"].split(' ')
            packstr = ['>']
            for i in range(0, len(data_to_write)):
                packstr.append('B')

            (status, data_real_read_len, readData) = ft.ftI2cWrite(i2cHandle,
                                                                int(value["dataDev"], 16),
                                                                FT260_I2C_FLAG[value["flag"]],
                                                                struct.pack("".join(packstr), int(value['reg'], 16),
                                                                            int(value['regValue'], 16))
                       #struct.pack("".join(packstr), int(value['reg'], 16), int(value['regValue'], 16))
                                                                )

            # Error checking
            if data_real_read_len != len(readData):
                print("Read {} bytes from ft260 lib, but {} bytes are in buffer".format(data_real_read_len,
                                                                                        len(readData)))
            elif not status == FT260_STATUS.FT260_OK.value:
                print("Read error : %s\r\n" % status)

            unpackstr = "<" + "B" * len(readData)
            for i in struct.unpack(unpackstr, readData):
                updateStr = updateStr + " " + hex(i)
                if not q.full():
                    q.put(['Read', value["dataDev"], hex(i)])
            window.FindElement("data").Update(updateStr)
            if not q.full():
                q.put(('From mainloop', 'Hello'))
            sg.Popup('The button clicked was "{}"'.format(button), 'The values are', value)
    q.put(None)

if __name__ == "__main__":
    # freeze_support is required for pyinstaller if multiprocessing is used
    multiprocessing.freeze_support()
    main()
