from ft_function import *
import ft
import time
import struct
from multiprocessing import Queue

import tkinter as tk
import tkinter.ttk as ttk

FT260_Vid = 0x0403
FT260_Pid = 0x6030
config = None


class _ConfigFrame(tk.Frame):
    @property
    def clock(self):
        return self.entry_clock.get()

    @clock.setter
    def clock(self, new_value):
        self.entry_clock.delete(0, tk.END)
        self.entry_clock.insert(0, new_value)

    @property
    def slave_address(self):
        return self.entry_address.get()

    @slave_address.setter
    def slave_address(self, new_value):
        self.entry_address.delete(0, tk.END)
        self.entry_address.insert(0, new_value)

    def open(self):
        ft.open_ftlib()
        if self.i2c_handle is not None:
            raise Exception("Device already opened. Action to open it twice should be disabled.")
            return

        if not ft.find_device_in_paths(FT260_Vid, FT260_Pid):
            self.entry_message.delete(0, tk.END)
            self.entry_message.insert(0, """No FT260 Device found. Was looking USB devices by VID/PID combination and didn't find any. 
            Did you forget to connect FT260 chip to USB?
            Did you install the driver?
            Do you see FT260 in device list?""")
            return

        self.i2c_handle = ft.openFtAsI2c(FT260_Vid, FT260_Pid, int(self.clock))

        if self.i2c_handle is None:
            self.entry_message.delete(0, tk.END)
            self.entry_message.insert(0, "Open I2C error. Was opening FT260 in I2C mode and failed.")
            return

        self.button_open.config(state = "disable")
        self.entry_clock.config(state = "disable")
        self.button_close.config(state="normal")
        self.entry_message.delete(0, tk.END)

    def close(self):
        if self.i2c_handle is not None:
            ft.close_device(self.i2c_handle)
            self.i2c_handle = None
            self.button_open.config(state="normal")
            self.entry_clock.config(state="normal")
            self.button_close.config(state="disable")
        else:
            raise Exception("Device is not opened. Action to close it twice should be disabled.")

    def __del__(self):
        if self.i2c_handle is not None:
            ft.close_device(self.i2c_handle)

    def __init__(self, parent):
        self.parent = parent
        self.i2c_handle = None
        super().__init__(self.parent)
        self.config(pady=5)
        self.grid_columnconfigure(4, weight=1)
        label_clock = tk.Label(self, text="Clock rate [kbps]:")
        label_address = tk.Label(self, text="I2C slave device address [hex]:")
        self.entry_clock = tk.Entry(self, width=6)
        self.entry_address = tk.Entry(self, width=6)
        self.button_open = tk.Button(self, text="Open device", command=self.open)
        self.button_close = tk.Button(self, text="Close device", command=self.close, state = "disabled")
        self.entry_message = tk.Entry(self)

        label_clock.grid(row=0, column=0)
        self.entry_clock.grid(row=0, column=1)
        label_address.grid(row=1, column=0)
        self.entry_address.grid(row=1, column=1)
        self.button_open.grid(row=0, column=2, padx = (3,0))
        self.button_close.grid(row=0, column=3)
        self.entry_message.grid(row=0, column=4, rowspan = 2, sticky = "nsew", padx=3)


class _DeviceScannerFrame(tk.Frame):
    global config

    def scan_button(self):
        self.entry_addresses.delete(0, tk.END)
        for address in range(1, 127):
            (ft_status, data_real_read_len, readData, status) = ft.ftI2cRead(config.i2c_handle,
                                                                             address,
                                                                             FT260_I2C_FLAG.FT260_I2C_START_AND_STOP,
                                                                             1)
            if not (status & FT260_I2C_STATUS_SLAVE_NACK):
                self.entry_addresses.insert(tk.END, hex(address) + " ")

    def __init__(self, parent):
        self.parent = parent
        super().__init__(self.parent)
        self.config(pady=5)
        self.grid_columnconfigure(2, weight=1)

        button_scan = tk.Button(self, text="Scan I2C bus", command=self.scan_button)
        label_scan_result = tk.Label(self, text="Found addresses:")
        self.entry_addresses = tk.Entry(self, width=30)

        button_scan.grid(row=0, column=0)
        label_scan_result.grid(row=0, column=1, padx=(3, 0))
        self.entry_addresses.grid(row=0, column=2, sticky="ew")


class _RegFrame(tk.Frame):
    global config

    def read_button(self):
        packstr = ['>', 'B' if self.register_address_size == 1 else 'H']
        unpackstr = ['>', 'B']
        if self.register_size == 2:
            unpackstr[1] = 'H'
        elif self.register_size == 4:
            unpackstr[1] = 'I'
        # Interpret register address as hexadecimal value
        reg_addr = int(self.register_address, 16)
        # Interpret device address as hexadecimal value
        dev_addr = int(config.slave_address, 16)
        ft.ftI2cWrite(config.i2c_handle,
                      dev_addr,
                      FT260_I2C_FLAG.FT260_I2C_START,
                      struct.pack("".join(packstr), reg_addr))
        # Register address is send. Can now retrieve register data
        (ft_status, data_real_read_len, readData, status) = ft.ftI2cRead(config.i2c_handle,
                                                                 dev_addr,
                                                                 FT260_I2C_FLAG.FT260_I2C_START_AND_STOP,
                                                                 self.register_size)
        if data_real_read_len != len(readData):
            print("Read {} bytes from ft260 lib, but {} bytes are in buffer".format(data_real_read_len, len(readData)))
        elif not ft_status == FT260_STATUS.FT260_OK.value:
            print("Read error : %s\r\n" % ft_status)
        if not len(readData) == 0:
            self.register_value = "%#x" % struct.unpack("".join(unpackstr), readData)

    def write_button(self):
        packstr = ['>', 'B', 'B']
        if self.register_address_size == 2:
            packstr[1] = 'H'
        if self.register_size == 2:
            packstr[2] = 'H'
        elif self.register_size == 4:
            packstr[2] = 'I'
        # Interpret register address as hexadecimal value
        reg_addr = int(self.register_address, 16)
        # Interpret device address as hexadecimal value
        dev_addr = int(config.slave_address, 16)
        # Interpret value to write as hexadecimal value
        reg_value = int(self.register_value, 16)
        ft.ftI2cWrite(config.i2c_handle, dev_addr, FT260_I2C_FLAG.FT260_I2C_START_AND_STOP,
                      struct.pack("".join(packstr), reg_addr, reg_value))

    @property
    def register_address(self):
        return self.entry_address.get()

    @register_address.setter
    def register_address(self, new_value):
        self.entry_address.delete(0, tk.END)
        self.entry_address.insert(0, new_value)

    @property
    def register_value(self):
        return self.entry_value.get()

    @register_value.setter
    def register_value(self, new_value):
        self.entry_value.delete(0, tk.END)
        self.entry_value.insert(0, new_value)

    @property
    def register_address_size(self):
        size = self.combo_reg_bits.get()
        if size == "8 bits":
            return 1
        elif size == "16 bits":
            return 2
        else:
            raise Exception("Unknown option {} in register_address_size combobox.".format(bytes))

    @property
    def register_size(self):
        size = self.combo_value_bits.get()
        if size == "8 bits":
            return 1
        elif size == "16 bits":
            return 2
        elif size == "32 bits":
            return 4
        else:
            raise Exception("Unknown option {} in register_size combobox.".format(bytes))

    def __init__(self, parent):
        self.parent = parent
        super().__init__(self.parent)
        self.config(pady=5)
        label_reg_bits = tk.Label(self, text="Register address size:")
        self.combo_reg_bits = ttk.Combobox(self, values=["8 bits", "16 bits"], width=6)
        self.combo_reg_bits.current(0)
        label_address = tk.Label(self, text="Register address:")
        self.entry_address = tk.Entry(self, width=6)
        label_value_bits = tk.Label(self, text="Register value size:")
        self.combo_value_bits = ttk.Combobox(self, values=["8 bits", "16 bits", "32 bits"], width=6)
        self.combo_value_bits.current(0)
        label_value = tk.Label(self, text="Register value:")
        self.entry_value = tk.Entry(self, width=10)
        button_write = tk.Button(self, text="Write", command=self.write_button)
        button_read = tk.Button(self, text="Read", command=self.read_button)

        label_reg_bits.grid(row=0, column=0, padx=(3, 0))
        self.combo_reg_bits.grid(row=0, column=1)
        label_address.grid(row=0, column=2, padx=(3, 0))
        self.entry_address.grid(row=0, column=3)
        label_value_bits.grid(row=0, column=4, padx=(3, 0))
        self.combo_value_bits.grid(row=0, column=5)
        label_value.grid(row=0, column=6, padx=(3, 0))
        self.entry_value.grid(row=0, column=7)
        button_write.grid(row=0, column=8)
        button_read.grid(row=0, column=9)


class _DataFrame(tk.Frame):
    global config

    @property
    def data_size(self):
        return self.entry_data_size.get()

    @data_size.setter
    def data_size(self, new_value):
        self.entry_data_size.delete(0, tk.END)
        self.entry_data_size.insert(0, new_value)

    @property
    def data(self):
        return self.entry_data.get()

    @data.setter
    def data(self, new_value):
        self.entry_data.delete(0, tk.END)
        self.entry_data.insert(0, new_value)

    @property
    def data_word(self):
        size = self.combo_word_size.get()
        if size == "8 bits":
            return 1
        elif size == "16 bits":
            return 2
        elif size == "32 bits":
            return 4
        else:
            raise Exception("Unknown option {} in data_word combobox.".format(bytes))

    def write_button(self):
        data_to_write = self.data.split(' ')
        words = []
        packstr = '>'
        for hex_word in data_to_write:
            if hex_word != "":
                words.append(int(hex_word, 16))
                packstr += self.word_symbol[self.data_word]

        (ft_status, data_real_read_len, readData, status) = ft.ftI2cWrite(config.i2c_handle,
                                                                  int(config.slave_address, 16),
                                                                  FT260_I2C_FLAG.FT260_I2C_START_AND_STOP,
                                                                  struct.pack("".join(packstr), *words)
                                                                  )
        # Error checking
        if data_real_read_len != len(readData):
            print("Read {} bytes from ft260 lib, but {} bytes are in buffer".format(data_real_read_len,
                                                                                    len(readData)))
        elif not ft_status == FT260_STATUS.FT260_OK.value:
            print("Read error : %s\r\n" % ft_status)

        update_str = ""
        unpackstr = "<" + self.word_symbol[self.data_word] * int(len(readData) / self.data_word)
        for i in struct.unpack(unpackstr, readData):
            update_str = update_str + " " + hex(i)
        self.data = update_str

    def read_button(self):
        (ft_status, data_real_read_len, readData, status) = ft.ftI2cRead(config.i2c_handle,
                                                                 int(config.slave_address, 16),
                                                                 FT260_I2C_FLAG.FT260_I2C_START_AND_STOP,
                                                                 int(self.data_size) * self.data_word)

        # Error checking
        if data_real_read_len != len(readData):
            print("Read {} bytes from ft260 lib, but {} bytes are in buffer".format(data_real_read_len,
                                                                                    len(readData)))
        elif not ft_status == FT260_STATUS.FT260_OK.value:
            print("Read error : %s\r\n" % ft_status)

        unpackstr = "<" + self.word_symbol[self.data_word] * int(len(readData) / self.data_word)
        update_str = ""
        for i in struct.unpack(unpackstr, readData):
            update_str = update_str + hex(i) + " "
        self.data = update_str

    def __init__(self, parent):
        self.parent = parent
        super().__init__(self.parent)
        self.config(pady=5)
        self.grid_columnconfigure(5, weight=1)

        label_data_size = tk.Label(self, text="Data length:")
        self.entry_data_size = tk.Entry(self, width=6)
        label_word_size = tk.Label(self, text="Data word size:")
        self.combo_word_size = ttk.Combobox(self, values=["8 bits", "16 bits", "32 bits"], width=6)
        self.combo_word_size.current(0)
        label_data = tk.Label(self, text="Data [hex]:")
        self.entry_data = tk.Entry(self, width=30)
        button_write = tk.Button(self, text="Write", command=self.write_button)
        button_read = tk.Button(self, text="Read", command=self.read_button)

        label_data_size.grid(row=0, column=0, padx=(3, 0))
        self.entry_data_size.grid(row=0, column=1)
        label_word_size.grid(row=0, column=2, padx=(3, 0))
        self.combo_word_size.grid(row=0, column=3)
        label_data.grid(row=0, column=4, padx=(3, 0))
        self.entry_data.grid(row=0, column=5, sticky="we")
        button_write.grid(row=0, column=6)
        button_read.grid(row=0, column=7)

        self.word_symbol = {1: "B", 2: "H", 4: "I"}


class _CommLog(tk.Frame):
    """
    Communication log for USB-I2C messages
    """

    def __init__(self, parent, q: Queue):
        """
        Constructor
        """
        self.q = q
        self.parent = parent
        super().__init__(self.parent)

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
        self.tree.column('#0', minwidth=40, width=40, stretch=tk.YES)
        self.tree.column('#1', minwidth=130, width=130, stretch=tk.YES)
        self.tree.column('#2', minwidth=70, width=70, stretch=tk.YES)
        self.tree.column('#3', minwidth=70, width=70, stretch=tk.YES)
        self.tree.column('#4', minwidth=130, width=130, stretch=tk.YES)
        self.tree.column('#5', minwidth=90, width=90, stretch=tk.YES)
        self.tree.column('#6', minwidth=50, width=50, stretch=tk.YES)

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
        self.parent.after(100, self.check_messages_and_show)

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
            v = list()
            v.append(time.strftime("%Y-%m-%d %H:%M:%S"))
            v.extend(next_in_queue)
            item = self.tree.insert('', 'end', text=str(self.message_number), values=v)
            self.message_number += 1
        if item is not None:
            self.tree.see(item)


def main():
    global config

    parent = tk.Tk()
    parent.title("FT260 I2C")
    config = _ConfigFrame(parent)
    config.clock = "100"
    config.slave_address = "0x68"
    config.pack(fill="x", expand = True)
    separator = ttk.Separator(parent, orient=tk.HORIZONTAL)
    separator.pack(fill="x")
    scanner = _DeviceScannerFrame(parent)
    scanner.pack(fill="x")
    separator = ttk.Separator(parent, orient=tk.HORIZONTAL)
    separator.pack(fill="x")
    reg = _RegFrame(parent)
    reg.pack(fill="x")
    reg.register_address = "0x00"
    separator = ttk.Separator(parent, orient=tk.HORIZONTAL)
    separator.pack(fill="x")
    data = _DataFrame(parent)
    data.data_size = 1
    data.pack(fill="x")
    q = Queue()
    ft._log_queue = q
    comm_log = _CommLog(parent, q)
    comm_log.pack(fill="both", expand=True)
    comm_log.run()
    parent.mainloop()


if __name__ == "__main__":
    main()
