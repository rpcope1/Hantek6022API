__author__ = 'Robert Cope'

from PyHT6022.LibUsbScope import Oscilloscope
import multiprocessing
import os
import select
import threading
import time
from collections import deque


os_write = os.write
os_read = os.read
os_close = os.close


def data_collection_proc_target(trigger_ch1_pipe, trigger_ch2_pipe, shutdown_event, data_points=0x2000,
                                max_transfers_queued=5, poll_interval=0.1):
    scope = Oscilloscope()
    scope.setup()
    scope.open_handle()

    def punt_to_pipe(ch1_data, ch2_data):
        os_write(trigger_ch1_pipe, ch1_data)
        # os_write(trigger_ch2_pipe, ch2_data)
    callback_shutdown_event = scope.read_async(punt_to_pipe, data_points,
                                               outstanding_bulk_transfers=max_transfers_queued,
                                               raw=True)
    while not shutdown_event.is_set():
        time.sleep(poll_interval)
    callback_shutdown_event.set()
    scope.close_handle()
    os_close(trigger_ch1_pipe)
    os_close(trigger_ch2_pipe)


def data_trigger_rising_edge_proc_target(ch1_reader_in_pipe, ch2_reader_in_pipe, ch1_trigger_out_pipe,
                                         ch2_trigger_out_pipe, shutdown_event, raw_threshold=180,
                                         points_save=500, trigger_ch=1, data_points=0x2000):
    assert trigger_ch in [1, 2]
    trigger_ch -= 1

    last_data_ch1 = bytearray("\x00")
    last_data_len = 1
    # last_data_ch2 = ""

    trigger_next_iter = False
    last_trigger_loc = 0
    shutdown_event_is_set = shutdown_event.is_set

    while not shutdown_event_is_set():
        channel_data = bytearray(os_read(ch1_reader_in_pipe, data_points)), ""
        # , os_read(ch2_reader_in_pipe, data_points)
        ch1_data, ch2_data = channel_data
        data_len = len(ch1_data)

        if trigger_next_iter:
            os_write(ch1_trigger_out_pipe,
                     (last_data_ch1 + ch1_data)[last_trigger_loc-points_save:last_trigger_loc+points_save])
            trigger_next_iter = False
        init = True
        trigger_loc = None

        for i in xrange(data_len):
            if init and ch1_data[i] < raw_threshold:
                init = False
            if not init and ch1_data[i] > raw_threshold:
                trigger_loc = i
                break
        if trigger_loc is not None:
            if trigger_loc + points_save > data_len:
                trigger_next_iter = True
                last_trigger_loc = trigger_loc
            else:
                start = trigger_loc - points_save
                end = trigger_loc + points_save
                os_write(ch1_trigger_out_pipe, (last_data_ch1 + ch1_data)[last_data_len+start:last_data_len+end])
                # os_write(ch2_trigger_out_pipe, (last_data_ch2 + ch2_data)[start:end])

        last_data_ch1 = ch1_data
        last_data_len = data_len
        # last_data_ch2 = ch2_data

    os_close(ch1_reader_in_pipe)
    os_close(ch1_trigger_out_pipe)
    os_close(ch2_reader_in_pipe)
    os_close(ch2_trigger_out_pipe)


class ScopeReaderInterface(object):
    POINTS_SAVE = 2000

    def __init__(self, reader_proc_func=data_collection_proc_target,
                 trigger_func=data_trigger_rising_edge_proc_target,
                 data_points=8192, trigger_threshold=180, trigger_channel=1, points_save=POINTS_SAVE):

        self.reader_proc_func = reader_proc_func
        self.trigger_proc_func = trigger_func

        self.reader_ch1_data_pipe_out, self.reader_data_ch1_pipe_in = os.pipe()
        self.trigger_pipe_ch1_out, self.trigger_pipe_ch1_in = os.pipe()
        
        self.reader_ch2_data_pipe_out, self.reader_data_ch2_pipe_in = os.pipe()
        self.trigger_pipe_ch2_out, self.trigger_pipe_ch2_in = os.pipe()
        
        self.ch1_trigger_queue = deque(maxlen=10)
        self.ch2_trigger_queue = deque(maxlen=10)
        
        self.shutdown_event = multiprocessing.Event()

        self.data_points = data_points
        self.trigger_threshold = trigger_threshold
        self.trigger_channel = trigger_channel
        self.points_save = points_save
        
        self._reader_proc = None
        self._trigger_proc = None
        self._trigger_recv_thread = None

    @staticmethod
    def build_trigger_poll_thread_func(ch1_input_pipe, ch2_input_pipe, ch1_queue, ch2_queue, shutdown_event,
                                       poll_interval=0.1, recv_points=POINTS_SAVE*2):
        def trigger_poll_func():
            ch1_queue_append = ch1_queue.append
            # ch2_queue_append = ch2_queue.append
            fd_select = select.select
            read_fd_list = [ch1_input_pipe]
            empty_list = []

            def poll_read_fd(fd_list, timeout=None):
                read_obj = fd_select(fd_list, empty_list, empty_list, timeout)[0]
                return bool(read_obj)

            while not shutdown_event.is_set():
                ch1_data = bytearray("")
                if poll_read_fd(read_fd_list, poll_interval):
                    while len(ch1_data) < recv_points:
                        ch1_data += os_read(ch1_input_pipe, recv_points)
                    # ch2_data = os_read(ch2_input_pipe, recv_points)
                    ch1_queue_append(ch1_data)
                    # ch2_queue_append(ch2_data)
            ch1_input_pipe.close()
            ch2_input_pipe.close()
        return trigger_poll_func
    
    def start(self):
        trigger_recv_target = self.build_trigger_poll_thread_func(self.trigger_pipe_ch1_out, self.trigger_pipe_ch1_out,
                                                                  self.ch1_trigger_queue, self.ch2_trigger_queue,
                                                                  self.shutdown_event, self.points_save*2)
        self._trigger_recv_thread = threading.Thread(target=trigger_recv_target)
        self._trigger_recv_thread.daemon = True
        self._trigger_recv_thread.start()
        self._trigger_proc = multiprocessing.Process(target=self.trigger_proc_func,
                                                     args=(self.reader_ch1_data_pipe_out, self.reader_ch2_data_pipe_out,
                                                           self.trigger_pipe_ch1_in, self.trigger_pipe_ch2_in,
                                                           self.shutdown_event, self.trigger_threshold,
                                                           self.points_save, self.trigger_channel,
                                                           self.data_points))
        self._trigger_proc.start()

        self._reader_proc = multiprocessing.Process(target=self.reader_proc_func, args=(self.reader_data_ch1_pipe_in,
                                                                                        self.reader_data_ch1_pipe_in,
                                                                                        self.shutdown_event,
                                                                                        self.data_points))
        self._reader_proc.start()
        return self.shutdown_event, self.ch1_trigger_queue, self.ch2_trigger_queue

    def stop(self, timeout=5):
        self.shutdown_event.set()
        if self._reader_proc:
            self._reader_proc.join(timeout)
        if self._reader_proc.is_alive():
            self._reader_proc.terminate()
        if self._trigger_proc:
            self._trigger_proc.join(timeout)
        if self._trigger_proc and self._trigger_proc.is_alive():
            self._trigger_proc.terminate()