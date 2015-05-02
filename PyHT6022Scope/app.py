__author__ = 'Robert Cope'

import matplotlib
matplotlib.use('TkAgg')

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from collections import deque
from scope_proc import ScopeReaderInterface
import time

try:
    import Tkinter as Tk
except ImportError:
    import tkinter as Tk


from PyHT6022.LibUsbScope import Oscilloscope


class ScopeApp(Tk.Tk):
    DATA_BUF_SIZE = 0x10000

    def __init__(self, title='PyHT6022 Scope', *args, **kwargs):
        Tk.Tk.__init__(self, *args, **kwargs)
        self.wm_title(title)

        self.plot_frame = Tk.Frame(master=self)
        self.plot_frame.grid(row=0, column=0, sticky='NSEW')
        self.controls_frame = Tk.Frame(master=self)
        self.controls_frame.grid(row=0, column=1, sticky='NSEW')

        self.plot_figure = Figure(figsize=(8, 6), dpi=100)
        self.plot_axis = self.plot_figure.add_subplot(111)
        self.plot_axis.grid()

        self.plot_canvas = FigureCanvasTkAgg(self.plot_figure, master=self.plot_frame)
        self.plot_canvas.show()
        self.plot_canvas._tkcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)
        self.scope = Oscilloscope()

        Tk.Label(master=self.controls_frame, text='Set Sample Rate', width=30).grid(row=0, column=0)
        self.sample_rate_var = Tk.IntVar(self)
        self.sample_rate_var.set(0x10)
        self.sample_rate_entry_box = Tk.Entry(master=self.controls_frame, textvariable=self.sample_rate_var, width=30)
        self.sample_rate_entry_box.grid(row=1, column=0)

        Tk.Label(master=self.controls_frame, text='Trigger Level', width=30).grid(row=2, column=0)
        self.trigger_level_var = Tk.DoubleVar(self)
        self.trigger_level_var.set(1.0)
        self.trigger_level_entry_box = Tk.Entry(master=self.controls_frame, textvariable=self.trigger_level_var,
                                                width=30)
        self.trigger_level_entry_box.grid(row=3, column=0)

        self.run_button = Tk.Button(master=self.controls_frame, text='Run', width=30,
                                    command=self.start_data_collection)
        self.run_button.grid(row=4, column=0)
        self.stop_button = Tk.Button(master=self.controls_frame, text='Stop', width=30,
                                     command=self.stop_data_collection)
        self.stop_button.grid(row=5, column=0)
        self.shutdown_event = None
        self.animation = None
        self.plot_line = None
        self.plot_updater = None
        self.data_queue = deque(maxlen=10)
        self.scope_reader_interface = None

    def initial_setup(self):
        success = self.scope.setup() and self.scope.open_handle()
        success &= self.scope.flash_firmware()
        return success

    def start_data_collection(self):
        sample_rate = self.sample_rate_var.get()
        self.plot_axis.cla()
        self.plot_axis.grid()
        self.scope.set_sample_rate(sample_rate)
        x_axis, label = self.scope.convert_sampling_rate_to_measurement_times(self.DATA_BUF_SIZE, sample_rate)
        self.plot_axis.set_xlabel(label)
        self.plot_line = plot_line, = self.plot_axis.plot(x_axis, [1.0 for _ in x_axis])
        for label in self.plot_axis.get_xticklabels():
            label.set_rotation(40)
        self.plot_figure.tight_layout()
        self.plot_canvas.show()
        self.scope.set_ch1_voltage_range(0x01)
        self.plot_axis.set_ylim([-5.0, 5.0])
        ch1_adc_threshold = self.scope.voltage_to_adc(self.trigger_level_var.get(), 0x01)
        self.scope_reader_interface = ScopeReaderInterface(ch2_trigger_func=None,
                                                           ch1_threshold=ch1_adc_threshold)
        self.scope.clear_fifo()
        self.scope.close_handle()
        time.sleep(0.1)
        self.shutdown_event, self.data_queue, _ = self.scope_reader_interface.start()
        data_queue = self.data_queue

        def update_plot():
            if data_queue:
                y_data = self.scope.scale_read_data(data_queue.pop(), 0x01)
                x_data = self.scope.convert_sampling_rate_to_measurement_times(len(y_data), self.sample_rate_var.get())[0]
                plot_line.set_data(x_data, y_data)
                self.plot_axis.set_xlim(min(x_data), max(x_data))
                self.plot_canvas.show()
            if self.shutdown_event and not self.shutdown_event.is_set():
                self.after(30, update_plot)
            return plot_line,

        self.after(30, update_plot)
        self.plot_updater = update_plot

    def stop_data_collection(self):
        if self.shutdown_event:
            self.shutdown_event.set()
            self.shutdown_event = None
        if self.scope_reader_interface:
            self.scope_reader_interface.stop(1)
        self.scope.open_handle()