import socket
import struct

from PyQt5.QtCore import QObject

import settings

# class TcpServer(QObject):
#     dataReadyToPlot = pyqtSignal()

#     def receive(self):
#         print("Receiving")
#         self.dataReadyToPlot.emit()


class TcpServer(QObject):
    def __init__(self) -> None:
        super(QObject, self).__init__()
        self.buffer_len = 13  # number of elements in received TCP buffer
        self.buffer_size = (
            self.buffer_len * 8
        )  # number of bytes in received TCP buffer. 8 because storing doubles.

        # Initialise shared memory for buffer
        self.V1_buffer = []
        self.V2_buffer = []
        self.V3_buffer = []
        self.I1_buffer = []
        self.I2_buffer = []
        self.I3_buffer = []

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
                        1.1,
                        1.1,
                        1.1,
                        1.1,
                        1.1,
                        1.1,
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

                    # Add received data to appropriate buffers
                    # t_buffer.append(data[0])
                    self.V1_buffer.append(data[1])
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
