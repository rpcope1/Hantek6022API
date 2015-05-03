__author__ = 'Robert Cope'

from PyHT6022.LibUsbScope import Oscilloscope
import multiprocessing
import threading
import time
from collections import deque


def data_collection_proc_target(trigger_pipe, shutdown_event, data_points=0x2000,
                                max_transfers_queued=5, poll_interval=0.1):
    scope = Oscilloscope()
    scope.setup()
    scope.open_handle()

    send_to_trigger = trigger_pipe.send

    def punt_to_pipe(ch1_data, ch2_data):
        send_to_trigger((ch1_data, ch2_data))
    callback_shutdown_event = scope.read_async(punt_to_pipe, data_points,
                                               outstanding_bulk_transfers=max_transfers_queued)
    while not shutdown_event.is_set():
        time.sleep(poll_interval)

    callback_shutdown_event.set()
    scope.close_handle()
    trigger_pipe.close()


def data_trigger_rising_edge_proc_target(reader_in_pipe, trigger_out_pipe, shutdown_event, raw_threshold=180,
                                         points_save=500, trigger_ch=1):
    assert trigger_ch in [1, 2]
    trigger_ch -= 1

    last_data_ch1 = []
    last_data_len = 0
    last_data_ch2 = []

    trigger_next_iter = False
    last_trigger_loc = 0
    recv_from_pipe = reader_in_pipe.recv
    send_to_pipe = trigger_out_pipe.send

    while not shutdown_event.is_set():
        ch1_data, ch2_data = channel_data = [list(data) for data in recv_from_pipe()]
        data_len = len(ch1_data)

        if trigger_next_iter:
            send_to_pipe(((last_data_ch1 + ch1_data)[last_trigger_loc-points_save:last_trigger_loc+points_save],
                          (last_data_ch2 + ch2_data)[last_trigger_loc-points_save:last_trigger_loc+points_save]))
            trigger_next_iter = False
        init = True
        trigger_loc = None

        for i, point in enumerate(channel_data[trigger_ch]):
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
                mid = trigger_loc + last_data_len
                start = (mid - points_save)
                end = (mid + points_save)
                send_to_pipe(((last_data_ch1 + ch1_data)[start:end], (last_data_ch2 + ch2_data)[start:end]))

        last_data_ch1 = ch1_data
        last_data_len = data_len
        last_data_ch2 = ch2_data

    reader_in_pipe.close()
    trigger_out_pipe.close()


class ScopeReaderInterface(object):
    def __init__(self, reader_proc_func=data_collection_proc_target,
                 trigger_func=data_trigger_rising_edge_proc_target,
                 data_points=8192, trigger_threshold=180, trigger_channel=1, points_save=2000):

        self.reader_proc_func = reader_proc_func
        self.trigger_proc_func = trigger_func

        self.reader_data_pipe_out, self.reader_data_pipe_in = multiprocessing.Pipe(duplex=False)
        self.trigger_pipe_out, self.trigger_pipe_in = multiprocessing.Pipe(duplex=False)
        self.ch1_trigger_queue = deque(maxlen=10)
        self.ch2_trigger_queue = deque(maxlen=10)
        
        self.shutdown_event = multiprocessing.Event()

        self.data_points = data_points
        self.ch1_threshold = trigger_threshold
        self.ch2_threshold = trigger_channel
        self.points_save = points_save
        
        self._reader_proc = None
        self._trigger_proc = None
        self._trigger_recv_thread = None

    @staticmethod
    def build_trigger_poll_thread_func(input_pipe, ch1_queue, ch2_queue, shutdown_event, poll_interval=0.1):
        def trigger_poll_func():
            ch1_queue_append = ch1_queue.append
            ch2_queue_append = ch2_queue.append
            input_pipe_recv = input_pipe.recv
            while not shutdown_event.is_set():
                if input_pipe.poll(poll_interval):
                    ch1_data, ch2_data = input_pipe_recv()
                    ch1_queue_append(ch1_data)
                    ch2_queue_append(ch2_queue)
            input_pipe.close()
        return trigger_poll_func
    
    def start(self):
        trigger_recv_target = self.build_trigger_poll_thread_func(self.trigger_pipe_out, self.ch1_trigger_queue,
                                                                  self.ch2_trigger_queue, self.shutdown_event)
        self._trigger_recv_thread = threading.Thread(target=trigger_recv_target)
        self._trigger_recv_thread.daemon = True
        self._trigger_recv_thread.start()
        self._trigger_proc = multiprocessing.Process(target=self.trigger_proc_func,
                                                     args=(self.reader_data_pipe_out,
                                                           self.trigger_pipe_in,
                                                           self.shutdown_event,
                                                           self.ch1_threshold,
                                                           self.points_save))
        self._trigger_proc.start()

        self._reader_proc = multiprocessing.Process(target=self.reader_proc_func, args=(self.reader_data_pipe_in,
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