from ft_function import *
# Tkinter GUI import
try:
    import Tkinter
    import ttk
except ImportError:  # Python 3
    import tkinter as Tkinter
    import tkinter.ttk as ttk

import time
import struct
from multiprocessing import Queue, Process


# If log is enabled then the Queue will be initialized
_logQueue = None


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


def openFtAsI2c(Vid, Pid, cfgRate):
    """
    Tries to open FY260 device by its VID and PID. Also initialize it with I2C speed defined by rate.
    Returns device handle.
    :param Vid: Vendor ID of the USB chip. For FT260 it is 0x0403
    :param Pid: Product ID of the USB chip. For FT260_it is 0x6030
    :param cfgRate: speed of connection in kbots. 100 and 400 are mostly used in I2C devices, though higher values are
    also possible.
    :return: handle for opened device. Handle must be stored for future use.
    """
    handle = c_void_p()

    # mode 0 is I2C, mode 1 is UART
    # Opening first device of possibly many available is used by providing indev 0 as third parameter.
    ftStatus = ftOpenByVidPid(Vid, Pid, 0, byref(handle))
    if not ftStatus == FT260_STATUS.FT260_OK.value:
        print("Open device Failed, status: %s\r\n" % FT260_STATUS(ftStatus))
        return 0
    else:
        print("Open device OK")

    ftStatus = ftI2CMaster_Init(handle, cfgRate)
    if not ftStatus == FT260_STATUS.FT260_OK.value:
        ftClose(handle)
        ftStatus = ftOpenByVidPid(Vid, Pid, 1, byref(handle))
        if not ftStatus == FT260_STATUS.FT260_OK.value:
            print("ReOpen device Failed, status: %s\r\n" % FT260_STATUS(ftStatus))
            return 0
        else:
            print("ReOpen device OK")
        ftStatus = ftI2CMaster_Init(handle, cfgRate)
        if not ftStatus == FT260_STATUS.FT260_OK.value:
            print("I2c Init Failed, status: %s\r\n" % FT260_STATUS(ftStatus))
            return 0

    print("I2c Init OK")

    return handle

def I2C_Mode_Name(flag :FT260_I2C_FLAG):
    Dict = {FT260_I2C_FLAG.FT260_I2C_NONE: 'None',
            FT260_I2C_FLAG.FT260_I2C_REPEATED_START: 'Repeated start',
            FT260_I2C_FLAG.FT260_I2C_START_AND_STOP: 'Start&stop',
            FT260_I2C_FLAG.FT260_I2C_START: 'Start',
            FT260_I2C_FLAG.FT260_I2C_STOP: 'Stop'
            }
    return Dict[flag]

def ftI2cConfig(handle, cfgRate):
    """
    Sets I2C speed (rate). Standard values are 100 and 400 kbods. Higher values are also possible.
    :param handle: Device handle from previous openFtAsI2c calls.
    :param cfgRate: Rate in kbods. Example: 100
    :return: None
    """
    ftI2CMaster_Reset(handle)
    ftStatus = ftI2CMaster_Init(handle, cfgRate)
    if not ftStatus == FT260_STATUS.FT260_OK.value:
        print("I2c Init Failed, status: %s\r\n" % FT260_STATUS(ftStatus))
        return 0
    else:
        print("I2c Init OK")


def ftI2cWrite(handle, i2cDev, flag, data):
    # Write data
    dwRealAccessData = c_ulong(0)
    status = c_uint8(0)  # To store status after operation
    buffer = create_string_buffer(data)
    buffer_void = cast(buffer, c_void_p)
    ftStatus = ftI2CMaster_Write(handle, i2cDev, flag, buffer_void, len(data), byref(dwRealAccessData))
    ftI2CMaster_GetStatus(handle, byref(status))
    if not ftStatus == FT260_STATUS.FT260_OK.value:
        print("I2c Write NG : %s\r\n" % FT260_STATUS(ftStatus))
    else:
        # Logging block. If enabled and there is data
        if _logQueue is not None and dwRealAccessData.value > 0:
            unpackstr = "<" + "B" * dwRealAccessData.value
            writetuple = struct.unpack(unpackstr, buffer.raw[:dwRealAccessData.value])
            msg =""
            for i in writetuple:
                msg += hex(i) + " "
            if not _logQueue.full():
                _logQueue.put(['Write', hex(i2cDev), msg, I2C_Mode_Name(flag), status.value])
            else:
                raise Exception("Interprocess communication Queue is full. Can't put new message.")

    return ftStatus, dwRealAccessData.value, buffer.raw


def ftI2cRead(handle, i2cDev, flag, readLen):
    """
    Read data
    :param handle:
    :param i2cDev:
    :param flag:
    :param readLen:
    :return:
    """
    dwRealAccessData = c_ulong(0) # Create variable to store received bytes
    status = c_uint8(0) # To store status after operation
    buffer = create_string_buffer(readLen) # Create buffer to hold received data as string
    buffer_void = cast(buffer, c_void_p) # Convert the same buffer to void pointer

    ftStatus = ftI2CMaster_Read(handle, i2cDev, flag, buffer_void, readLen, byref(dwRealAccessData))
    ftI2CMaster_GetStatus(handle, byref(status))

    # Logging block. If enabled, data is valid and there is data
    if _logQueue is not None and ftStatus == FT260_STATUS.FT260_OK.value and dwRealAccessData.value > 0:
        unpackstr = "<" + "B" * dwRealAccessData.value
        readtuple = struct.unpack(unpackstr, buffer.raw[:dwRealAccessData.value])
        msg = ""
        for i in readtuple:
            msg += hex(i) + " "
        if not _logQueue.full():
            _logQueue.put(['Read', hex(i2cDev), msg, I2C_Mode_Name(flag), status.value])
        else:
            raise Exception("Interprocess communication Queue is full. Can't put new message.")

    return ftStatus, dwRealAccessData.value, buffer.raw


def openFtAsUart(Vid, Pid):
    ftStatus = c_int(0)
    handle = c_void_p()

    # mode 0 is I2C, mode 1 is UART
    ftStatus = ftOpenByVidPid(Vid, Pid, 1, byref(handle))
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


class _ConfigFrame(Tkinter.Frame):
    def __init__(self, parent):
        self.parent = parent
        super().__init__(self.parent)
        self.config(pady = 3)
        labelClock = Tkinter.Label(self, text="Clock rate [kbps]:")
        labelAddress = Tkinter.Label(self, text="I2C slave device address [hex]:")
        entryClock = Tkinter.Entry(self, width = 6)
        entryAddress = Tkinter.Entry(self, width = 6)
        labelClock.grid(row=0, column=0)
        entryClock.grid(row=0, column=1)
        labelAddress.grid(row=1, column=0)
        entryAddress.grid(row=1, column=1)

class _RegFrame(Tkinter.Frame):
    def write_button(self):
        pass

    def read_button(self):
        pass

    def __init__(self, parent):
        self.parent = parent
        super().__init__(self.parent)
        self.config(pady = 3)
        strRegBits = "Register address size:"
        labelRegBits = Tkinter.Label(self, text=strRegBits)
        comboRegBits = ttk.Combobox(self, values=["8 bits", "16 bits"], width = 6)
        comboRegBits.current(0)
        strAddress = "Register address:"
        labelAddress = Tkinter.Label(self, text=strAddress)
        entryAddress = Tkinter.Entry(self, width = 6)
        strValueBits = "Register value size:"
        labelValueBits = Tkinter.Label(self, text=strValueBits)
        comboValueBits = ttk.Combobox(self, values=["8 bits", "16 bits", "32 bits"], width=6)
        comboValueBits.current(0)
        strValue = "Register value:"
        labelValue = Tkinter.Label(self, text=strValue)
        entryValue = Tkinter.Entry(self, width = 10)
        buttonWrite = Tkinter.Button(self, text="Write", command=self.write_button)
        buttonRead = Tkinter.Button(self, text="Read", command=self.read_button)

        labelRegBits.grid(row=0, column=0, padx=(3, 0))
        comboRegBits.grid(row=0, column=1)
        labelAddress.grid(row=0, column=2, padx=(3, 0))
        entryAddress.grid(row=0, column=3)
        labelValueBits.grid(row=0, column=4, padx=(3, 0))
        comboValueBits.grid(row=0, column=5)
        labelValue.grid(row=0, column=6, padx=(3, 0))
        entryValue.grid(row=0, column=7)
        buttonWrite.grid(row=0, column=8)
        buttonRead.grid(row=0, column=9)

class _DataFrame(Tkinter.Frame):
    def write_button(self):
        pass

    def read_button(self):
        pass

    def __init__(self, parent):
        self.parent = parent
        super().__init__(self.parent)
        self.config(pady = 3)
        self.grid_columnconfigure(5, weight=1)
        label_data_size = Tkinter.Label(self, text="Data length:")
        entry_data_size = Tkinter.Entry(self, width = 6)
        label_word_size = Tkinter.Label(self, text="Data word size:")
        combo_word_size = ttk.Combobox(self, values=["8 bits", "16 bits", "32 bits"], width=6)
        combo_word_size.current(0)
        label_data = Tkinter.Label(self, text="Data [hex]:")
        entry_data = Tkinter.Entry(self, width = 30)
        buttonWrite = Tkinter.Button(self, text="Write", command=self.write_button)
        buttonRead = Tkinter.Button(self, text="Read", command=self.read_button)

        label_data_size.grid(row=0, column=0, padx=(3, 0))
        entry_data_size.grid(row=0, column=1)
        label_word_size.grid(row=0, column=2, padx=(3, 0))
        combo_word_size.grid(row=0, column=3)
        label_data.grid(row=0, column=4, padx=(3, 0))
        entry_data.grid(row=0, column=5, sticky = "we")
        buttonWrite.grid(row=0, column=6)
        buttonRead.grid(row=0, column=7)


class _CommLog(Tkinter.Frame):
    """
    Communication log for USB-I2C messages
    """

    def __init__(self, q: Queue, parent = None):
        """
        Constructor
        """
        if parent is None:
            self.parent = Tkinter.Tk()
            self.parent.title("Communication log")
            self.parent.config(background="lavender")
        else:
            self.parent = parent

        self.q = q
        super().__init__(self.parent)
        self.pack(fill = "both", expand = True)

        # Inside frame grid config
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Set the treeview
        self.tree = ttk.Treeview(self, columns=('Timestamp', 'Direction', 'Address', 'Message', 'Mode', 'Status'))
        self.tree.heading('#0', text='#')
        self.tree.heading('#1', text='Timestamp')
        self.tree.heading('#2', text='Direction')
        self.tree.heading('#3', text='Address')
        self.tree.heading('#4', text='Message')
        self.tree.heading('#5', text='Mode')
        self.tree.heading('#6', text='Status')
        self.tree.column('#0', minwidth=40, width=40, stretch=Tkinter.YES)
        self.tree.column('#1', minwidth=130, width=130, stretch=Tkinter.YES)
        self.tree.column('#2', minwidth=70, width=70, stretch=Tkinter.YES)
        self.tree.column('#3', minwidth=70, width=70, stretch=Tkinter.YES)
        self.tree.column('#4', minwidth=130, width=130, stretch=Tkinter.YES)
        self.tree.column('#5', minwidth=90, width=90, stretch=Tkinter.YES)
        self.tree.column('#6', minwidth=50, width=50, stretch=Tkinter.YES)

        # Scrollbar
        self.vsb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.vsb.set)

        # Layout
        self.tree.grid(row=0, column=0, sticky='nsew')
        self.vsb.grid(row=0, column=1, sticky='ns')

        # Initialize the counter
        self.message_number = 0

    def run(self):
        # Ask Tkinter to run message check in 100 ms
        self.parent.after(100,self.check_messages_and_show)
        self.parent.mainloop()

    def check_messages_and_show(self):
        """
        Check for messages in queue and add them all to treeview if there are any
        """
        # Start by asking Tkinter to run this check in next 100 ms, making check loop
        self.parent.after(100, self.check_messages_and_show)
        # While there are messages - process them
        item = None
        while not self.q.empty():
            next_in_queue = self.q.get()
            # Check for killbomb
            if next_in_queue is None:
                self.parent.quit()
                break
            v=list()
            v.append(time.strftime("%Y-%m-%d %H:%M:%S"))
            v.extend(next_in_queue)
            item = self.tree.insert('', 'end', text=str(self.message_number), values=v)
            self.message_number += 1
        if item is not None:
            self.tree.see(item)

def _run_log(q: Queue):
    """
    Creates Tkinter log window for all transactions in separate process.
    Process can be terminated with killbomb, sending None in message queue.
    :param q: multiprocessing Queue object for message queue
    :return: None
    """
    parent = Tkinter.Tk()
    parent.title("FT260 I2C")
    config = _ConfigFrame(parent)
    config.pack(fill = "x")
    separator = ttk.Separator(parent, orient=Tkinter.HORIZONTAL)
    separator.pack(fill="x")
    reg = _RegFrame(parent)
    reg.pack(fill="x")
    separator = ttk.Separator(parent, orient=Tkinter.HORIZONTAL)
    separator.pack(fill="x")
    data = _DataFrame(parent)
    data.pack(fill="x")
    comm_log = _CommLog(q, parent)
    comm_log.run()

def I2Clog(enable = False):
    """
    Creates or destroys log window existing in separate process. Uses multiprocessing, so you must call disabling
    of this log before interrupting main process.
    :param enable: If True the log is created. If False - destroyed.
    :return: None
    """
    global _logQueue
    if enable is True:
        if _logQueue is not None:
            raise Exception("Try do create log, but seems it is active already.")
        else:
            _logQueue = Queue()
            process_comm_log = Process(target=_run_log, args=[_logQueue, ])
            process_comm_log.start()
    else:
        if _logQueue is None:
            raise Exception("Try do disable log, but seems it is not active.")
        else:
            _logQueue.put(None)
            _logQueue = None
