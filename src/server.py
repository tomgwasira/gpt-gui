"""
To-do:
    * Check how quickly the client sends data and then profile how quickly the
        current server can run the whole while loop and then reconcile those times.
        However, it's nothing to be too worried about because the server actually
        sends data first so if the client is using a block recv, the times will
        synchronise automatically (unless if using threads in the client).
"""

import socket
import struct
import pyqtgraph as pg

from PyQt5.QtCore import QMutex, QObject

import settings

# class TcpServer(QObject):
#     dataReadyToPlot = pyqtSignal()

#     def receive(self):
#         print("Receiving")
#         self.dataReadyToPlot.emit()


class TcpServer(QObject):
    def __init__(
                    self,
                    inputGroup1DoubleSpinBox_1,
                    inputGroup1DoubleSpinBox_2,
                    inputGroup1DoubleSpinBox_3,
                    inputGroup2DoubleSpinBox_1,
                    inputGroup2DoubleSpinBox_2,
                    inputGroup2DoubleSpinBox_3
                ) -> None:
        super(QObject, self).__init__()
        self.buffer_len = 13  # number of elements in received TCP buffer
        self.buffer_size = (
            self.buffer_len * 8
        )  # number of bytes in received TCP buffer. 8 because storing doubles.

        # ------------
        # QMutex setup
        # ------------
        self.mutex = QMutex()

        # Initialise shared memory for buffer
        self.V1_buffer = []
        self.V2_buffer = []
        self.V3_buffer = []
        self.I1_buffer = []
        self.I2_buffer = []
        self.I3_buffer = []

        self.n_samples_in_view = 100

        self.V1_trigger_value = 0
        self.V2_trigger_value = 0
        self.V3_trigger_value = 0
        self.I1_trigger_value = 0
        self.I2_trigger_value = 0
        self.I3_trigger_value = 0

        self.V1_upper_limit = 0
        self.V1_lower_limit = 0
        self.V2_upper_limit = 0
        self.V2_lower_limit = 0
        self.V3_upper_limit = 0
        self.V3_lower_limit = 0
        self.I1_upper_limit = 0
        self.I1_lower_limit = 0
        self.I2_upper_limit = 0
        self.I2_lower_limit = 0
        self.I3_upper_limit = 0
        self.I3_lower_limit = 0

        self.inputGroup1DoubleSpinBox_1 = inputGroup1DoubleSpinBox_1
        self.inputGroup1DoubleSpinBox_2 = inputGroup1DoubleSpinBox_2
        self.inputGroup1DoubleSpinBox_3 = inputGroup1DoubleSpinBox_3
        self.inputGroup2DoubleSpinBox_1 = inputGroup2DoubleSpinBox_1
        self.inputGroup2DoubleSpinBox_2 = inputGroup2DoubleSpinBox_2
        self.inputGroup2DoubleSpinBox_3 = inputGroup2DoubleSpinBox_3

    def run_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((settings.HOST, settings.PORT))
            s.listen()
            conn, addr = s.accept()
            with conn:
                print(f"Connected by {addr}")
                while True:
                    # -----------
                    # Inputs send
                    # -----------
                    # Always send first before recv incase some data to be received depends on sent data.
                    # Additionally, Simulink block written for this program calls a blocking recv, so it
                    # will block if recv is called with no data sent.
                    double_list = [
                        self.inputGroup1DoubleSpinBox_1.value(),
                        self.inputGroup1DoubleSpinBox_2.value(),
                        self.inputGroup1DoubleSpinBox_3.value(),
                        self.inputGroup2DoubleSpinBox_1.value(),
                        self.inputGroup2DoubleSpinBox_2.value(),
                        self.inputGroup2DoubleSpinBox_3.value()
                    ]
                    data_to_send = struct.pack("6d", *double_list)
                    conn.sendall(data_to_send)

                    # ------------
                    # Data receive
                    # ------------
                    size_to_read = self.buffer_size
                    data = b""

                    # Keep receiving until the expected buffer size has been read
                    while size_to_read > 0:
                        data = data + conn.recv(size_to_read)
                        size_to_read -= len(data)

                    data = struct.unpack((str(self.buffer_len) + "d"), data)

                    V1_value = data[1]
                    V2_value = data[2]
                    V3_value = data[3]
                    I1_value = data[4]
                    I2_value = data[5]
                    I3_value = data[6]
        
                    # Add received data to appropriate buffers
                    # TODO: Deal with t_buffer inputs
                    self.V1_buffer.append(V1_value)
                    self.V2_buffer.append(data[2])
                    self.V3_buffer.append(data[3])
                    self.I1_buffer.append(data[4])
                    self.I2_buffer.append(data[5])
                    self.I3_buffer.append(data[6])

                    self.f0_V1 = data[7]
                    self.f0_V2 = data[8]
                    self.f0_V3 = data[9]
                    self.f0_I1 = data[10]
                    self.f0_I2 = data[11]
                    self.f0_I3 = data[12]

                    self.trigger(V1_value, V2_value, V3_value, I1_value, I2_value, I3_value)

                    if len(self.V1_buffer) > settings.maxBufferLength:
                        self.clearBuffers()

    def trigger(self, V1_value, V2_value, V3_value, I1_value, I2_value, I3_value):
        # Lock to avoid plotting while indexes are being modified
        self.mutex.lock()
        # Check trigger value
        if V1_value > self.V1_trigger_value:
            self.V1_upper_limit = len(self.V1_buffer)
            self.V1_lower_limit = self.V1_upper_limit - self.n_samples_in_view
            if self.V1_lower_limit < 0:
                self.V1_lower_limit = 0

        if V2_value > self.V2_trigger_value:
            self.V2_upper_limit = len(self.V2_buffer)
            self.V2_lower_limit = self.V2_upper_limit - self.n_samples_in_view
            if self.V2_lower_limit < 0:
                self.V2_lower_limit = 0

        if V3_value > self.V3_trigger_value:
            self.V3_upper_limit = len(self.V3_buffer)
            self.V3_lower_limit = self.V3_upper_limit - self.n_samples_in_view
            if self.V3_lower_limit < 0:
                self.V3_lower_limit = 0

        if I1_value > self.I1_trigger_value:
            self.I1_upper_limit = len(self.I1_buffer)
            self.I1_lower_limit = self.I1_upper_limit - self.n_samples_in_view
            if self.I1_lower_limit < 0:
                self.I1_lower_limit = 0

        if I2_value > self.I2_trigger_value:
            self.I2_upper_limit = len(self.I2_buffer)
            self.I2_lower_limit = self.I2_upper_limit - self.n_samples_in_view
            if self.I2_lower_limit < 0:
                self.I2_lower_limit = 0

        if I3_value > self.I3_trigger_value:
            self.I3_upper_limit = len(self.I3_buffer)
            self.I3_lower_limit = self.I3_upper_limit - self.n_samples_in_view
            if self.I3_lower_limit < 0:
                self.I3_lower_limit = 0        

        self.mutex.unlock()
    
    def clearBuffers(self):
        self.mutex.lock()

        del self.V1_buffer[:self.V1_lower_limit]
        self.V1_lower_limit = 0
        self.V1_upper_limit = len(self.V1_buffer)

        del self.V2_buffer[:self.V2_lower_limit]
        self.V2_lower_limit = 0
        self.V2_upper_limit = len(self.V2_buffer)

        del self.V3_buffer[:self.V3_lower_limit]
        self.V3_lower_limit = 0
        self.V3_upper_limit = len(self.V3_buffer)

        del self.I1_buffer[:self.I1_lower_limit]
        self.I1_lower_limit = 0
        self.I1_upper_limit = len(self.I1_buffer)

        del self.I2_buffer[:self.I2_lower_limit]
        self.I2_lower_limit = 0
        self.I2_upper_limit = len(self.I2_buffer)

        del self.I3_buffer[:self.I3_lower_limit]
        self.I3_lower_limit = 0
        self.I3_upper_limit = len(self.I3_buffer)

        self.mutex.unlock()





