__author__ = 'Robert Cope'

from PyHT6022.LibUsbScope import Oscilloscope
import multiprocessing
import threading
import time
from collections import deque


def data_collection_proc_target(ch1_pipe, ch2_pipe, shutdown_event, data_points=0x2000,
                                max_transfers_queued=5, poll_interval=0.1):
    scope = Oscilloscope()
    scope.setup()
    scope.open_handle()

    if ch1_pipe and ch2_pipe:
        ch1_pipe_send = ch1_pipe.send
        ch2_pipe_send = ch1_pipe.send

        def punt_to_pipe(ch1_data, ch2_data):
            ch1_pipe_send(ch1_data)
            ch2_pipe_send(ch2_data)
    elif ch1_pipe:
        ch1_pipe_send = ch1_pipe.send

        def punt_to_pipe(ch1_data, _):
            ch1_pipe_send(ch1_data)
    else:
        ch2_pipe_send = ch1_pipe.send

        def punt_to_pipe(_, ch2_data):
            ch2_pipe_send(ch2_data)

    callback_shutdown_event = scope.read_async(punt_to_pipe, data_points,
                                               outstanding_bulk_transfers=max_transfers_queued)
    while not shutdown_event.is_set():
        time.sleep(poll_interval)
    scope.close_handle()
    callback_shutdown_event.set()
    if ch1_pipe:
        ch1_pipe.close()
    if ch2_pipe:
        ch2_pipe.close()


def data_trigger_rising_edge_proc_target(channel_in_pipe, trigger_out_pipe, shutdown_event, raw_threshold=180,
                                         points_save=500):
    last_data = []
    last_len = 0
    trigger_next_iter = False
    last_trigger_loc = 0
    recv_from_pipe = channel_in_pipe.recv
    send_to_pipe = trigger_out_pipe.send
    while not shutdown_event.is_set():
        data = list(recv_from_pipe())
        data_len = len(data)
        if trigger_next_iter:
            send_to_pipe((last_data + data)[last_trigger_loc-points_save:last_trigger_loc+points_save])
            trigger_next_iter = False
        init = True
        trigger_loc = None
        for i, point in enumerate(data):
            if init and point < raw_threshold:
                init = False
            if not init and point > raw_threshold:
                trigger_loc = i
                break
        if trigger_loc is not None:
            if trigger_loc + points_save > data_len:
                trigger_next_iter = True
                last_trigger_loc = trigger_loc
            else:
                mid = trigger_loc + last_len
                start = (mid - points_save)
                end = (mid + points_save)
                send_to_pipe((last_data + data)[start:end])
        last_data = data
        last_len = data_len

    channel_in_pipe.close()
    trigger_out_pipe.close()


class ScopeReaderInterface(object):
    def __init__(self, reader_proc_func=data_collection_proc_target,
                 ch1_trigger_func=data_trigger_rising_edge_proc_target,
                 ch2_trigger_func=data_trigger_rising_edge_proc_target,
                 data_points=0x2000, ch1_threshold=180, ch2_threshold=180, points_save=500):
        assert ch1_trigger_func or ch2_trigger_func
        self.reader_proc_func = reader_proc_func
        self.ch1_trigger_func = ch1_trigger_func
        self.ch2_trigger_func = ch2_trigger_func

        if ch1_trigger_func:
            self.reader_ch1_pipe_out, self.reader_ch1_pipe_in = multiprocessing.Pipe(duplex=False)
            self.ch1_trigger_pipe_out, self.ch1_trigger_pipe_in = multiprocessing.Pipe(duplex=False)
            self.ch1_trigger_queue = deque(maxlen=10)
        else:
            self.reader_ch1_pipe_out = self.reader_ch1_pipe_in = None
            self.ch1_trigger_pipe_out = self.ch1_trigger_pipe_in = None
            self.ch1_trigger_queue = None
        
        if ch2_trigger_func:
            self.reader_ch2_pipe_out, self.reader_ch2_pipe_in = multiprocessing.Pipe(duplex=False)
            self.ch2_trigger_pipe_out, self.ch2_trigger_pipe_in = multiprocessing.Pipe(duplex=False)
            self.ch2_trigger_queue = deque(maxlen=10)
        else:
            self.reader_ch2_pipe_out = self.reader_ch2_pipe_in = None
            self.ch2_trigger_pipe_out = self.ch2_trigger_pipe_in = None
            self.ch2_trigger_queue = None
        
        self.shutdown_event = multiprocessing.Event()

        self.data_points = data_points
        self.ch1_threshold = ch1_threshold
        self.ch2_threshold = ch2_threshold
        self.points_save = points_save
        
        self._reader_proc = None
        self._ch1_trigger_proc = None
        self._ch2_trigger_proc = None        
        self._ch1_trigger_recv_thread = None
        self._ch2_trigger_recv_thread = None

    @staticmethod
    def build_trigger_poll_thread_func(input_pipe, queue, shutdown_event, poll_interval=0.1):
        def trigger_poll_func():
            while not shutdown_event.is_set():
                if input_pipe.poll(poll_interval):
                    queue.append(input_pipe.recv())
            input_pipe.close()
        return trigger_poll_func
    
    def start(self):
        if self.ch1_trigger_func:
            ch1_recv_target = self.build_trigger_poll_thread_func(self.ch1_trigger_pipe_out, self.ch1_trigger_queue,
                                                                  self.shutdown_event)
            self._ch1_trigger_recv_thread = threading.Thread(target=ch1_recv_target)
            self._ch1_trigger_recv_thread.daemon = True
            self._ch1_trigger_recv_thread.start()
            self._ch1_trigger_proc = multiprocessing.Process(target=self.ch1_trigger_func, 
                                                             args=(self.reader_ch1_pipe_out,
                                                                   self.ch1_trigger_pipe_in,
                                                                   self.shutdown_event,
                                                                   self.ch1_threshold,
                                                                   self.points_save))
            self._ch1_trigger_proc.start()
        if self.ch2_trigger_func:
            ch2_recv_target = self.build_trigger_poll_thread_func(self.ch2_trigger_pipe_out, self.ch2_trigger_queue,
                                                                  self.shutdown_event)
            self._ch2_trigger_recv_thread = threading.Thread(target=ch2_recv_target)
            self._ch2_trigger_recv_thread.daemon = True
            self._ch2_trigger_recv_thread.start()
            self._ch2_trigger_proc = multiprocessing.Process(target=self.ch2_trigger_func, 
                                                             args=(self.reader_ch2_pipe_out,
                                                                   self.ch2_trigger_pipe_in,
                                                                   self.shutdown_event,
                                                                   self.ch2_threshold,
                                                                   self.points_save))
            self._ch2_trigger_proc.start()
        self._reader_proc = multiprocessing.Process(target=self.reader_proc_func, args=(self.reader_ch1_pipe_in,
                                                                                        self.reader_ch2_pipe_in,
                                                                                        self.shutdown_event,
                                                                                        self.data_points))
        self._reader_proc.start()
        return self.shutdown_event, self.ch1_trigger_queue, self.ch2_trigger_queue

    def stop(self, timeout=5):
        self.shutdown_event.set()
        self._reader_proc.join(timeout)
        if self._reader_proc.is_alive():
            self._reader_proc.terminate()
        if self._ch1_trigger_proc:
            self._ch1_trigger_proc.join(timeout)
        if self._ch1_trigger_proc and self._ch1_trigger_proc.is_alive():
            self._ch1_trigger_proc.terminate()
        if self._ch2_trigger_proc:
            self._ch2_trigger_proc.join(timeout)
        if self._ch2_trigger_proc and self._ch2_trigger_proc.is_alive():
            self._ch2_trigger_proc.terminate()

if __name__ == "__main__":
    sample_rate_index = 0x1E
    voltage_range = 0x01

    scope = Oscilloscope()
    scope.setup()
    scope.open_handle()
    scope.flash_firmware()
    time.sleep(1)
    scope.set_num_channels(1)
    scope.set_sample_rate(sample_rate_index)
    scope.set_ch1_voltage_range(voltage_range)
    scope.clear_fifo()
    scope.close_handle()
    time.sleep(1)
    reader_interface = ScopeReaderInterface(ch2_trigger_func=None, points_save=5, ch1_threshold=145)
    try:
        shutdown, ch1_queue, ch2_queue = reader_interface.start()
        for i in xrange(20):
            print i
            if ch1_queue:
                print ch1_queue.pop()
            else:
                print "Queue empty!"
            time.sleep(1)
        shutdown.set()
        print "Intitiating shutdown sequence."
        reader_interface.stop()
    except KeyboardInterrupt:
        print "Intitiating shutdown sequence."
        reader_interface.stop()
        raise