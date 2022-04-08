"""Tcp server implementation for General Power Theory GUI.

The server is responsible for acquiring data that is plotted.

To-do:
    * Check how quickly the client sends data and then profile how quickly the
        current server can run the whole while loop and then reconcile those times.
        However, it's nothing to be too worried about because the server actually
        sends data first so if the client is using a block recv, the times will
        synchronise automatically (unless if using threads in the client).
"""
# Standard library imports
import socket
import struct

# Third-party library imports
from PyQt5.QtCore import QMutex, QObject
import pyqtgraph as pg

# Local application imports
import settings

class TcpServer(QObject):
    """Tcp server implementation.
    
    The server is responsible for acquiring and managing data that is
    then plotted.
    """
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
        self.bufferLen = 13  # number of elements in received TCP buffer
        self.bufferSize = (
            self.bufferLen * 8
        )  # number of bytes in received TCP buffer. 8 because storing doubles.

        # ------------
        # QMutex setup
        # ------------
        self.mutex = QMutex()

        # ---------------
        # Initialisations
        # ---------------
        self.debugBuffer = [] # buffer for use in debugging
        self.v1Buffer = []
        self.v2Buffer = []
        self.v3Buffer = []
        self.i1Buffer = []
        self.i2Buffer = []
        self.i3Buffer = []

        self.v1TriggerValue = 0
        self.v2TriggerValue = 0
        self.v3TriggerValue = 0
        self.i1TriggerValue = 0
        self.i2TriggerValue = 0
        self.i3TriggerValue = 0

        self.v1UpperLimit = 0
        self.v1LowerLimit = 0
        self.v2UpperLimit = 0
        self.v2LowerLimit = 0
        self.v3UpperLimit = 0
        self.v3LowerLimit = 0
        self.i1UpperLimit = 0
        self.i1LowerLimit = 0
        self.i2UpperLimit = 0
        self.i2LowerLimit = 0
        self.i3UpperLimit = 0
        self.i3LowerLimit = 0

        self.f0_V1 = 0
        self.f0_V2 = 0
        self.f0_V3 = 0
        self.f0_I1 = 0
        self.f0_I2 = 0
        self.f0_I3 = 0

        self.inputGroup1DoubleSpinBox_1 = inputGroup1DoubleSpinBox_1
        self.inputGroup1DoubleSpinBox_2 = inputGroup1DoubleSpinBox_2
        self.inputGroup1DoubleSpinBox_3 = inputGroup1DoubleSpinBox_3
        self.inputGroup2DoubleSpinBox_1 = inputGroup2DoubleSpinBox_1
        self.inputGroup2DoubleSpinBox_2 = inputGroup2DoubleSpinBox_2
        self.inputGroup2DoubleSpinBox_3 = inputGroup2DoubleSpinBox_3

    def runServer(self):
        """Listen for connections to a socket and if a client connects,
        start receving data and writing it to buffers.
        """
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
                    doubleList = [
                        self.inputGroup1DoubleSpinBox_1.value(),
                        self.inputGroup1DoubleSpinBox_2.value(),
                        self.inputGroup1DoubleSpinBox_3.value(),
                        self.inputGroup2DoubleSpinBox_1.value(),
                        self.inputGroup2DoubleSpinBox_2.value(),
                        self.inputGroup2DoubleSpinBox_3.value()
                    ]
                    dataToSend = struct.pack("6d", *doubleList)
                    conn.sendall(dataToSend)

                    # ------------
                    # Data receive
                    # ------------
                    sizeToRead = self.bufferSize
                    data = b""

                    # Keep receiving until the expected buffer size has been read
                    while sizeToRead > 0:
                        data = data + conn.recv(sizeToRead)
                        sizeToRead -= len(data)

                    data = struct.unpack((str(self.bufferLen) + "d"), data)

                    v1Value = data[1]
                    v2Value = data[2]
                    v3Value = data[3]
                    i1Value = data[4]
                    i2Value = data[5]
                    i3Value = data[6]
        
                    # Add received data to appropriate buffers
                    self.debugBuffer.append(data[0])
                    self.v1Buffer.append(v1Value)
                    self.v2Buffer.append(v2Value)
                    self.v3Buffer.append(v3Value)
                    self.i1Buffer.append(i1Value)
                    self.i2Buffer.append(i2Value)
                    self.i3Buffer.append(i3Value)

                    self.f0_V1 = data[7]
                    self.f0_V2 = data[8]
                    self.f0_V3 = data[9]
                    self.f0_I1 = data[10]
                    self.f0_I2 = data[11]
                    self.f0_I3 = data[12]

                    # Reset plot limits. Must be done before triggering
                    if len(self.v1Buffer) >= settings.nSamplesInView:
                        self.mutex.lock()
                        v1BufferLen = len(self.v1Buffer)
                        self.v1UpperLimit = v1BufferLen
                        self.v1LowerLimit = v1BufferLen - settings.nSamplesInView
  
                        v2BufferLen = len(self.v2Buffer)
                        self.v2UpperLimit = v2BufferLen
                        self.v2LowerLimit = v2BufferLen - settings.nSamplesInView

                        v3BufferLen = len(self.v3Buffer)
                        self.v3UpperLimit = v3BufferLen
                        self.v3LowerLimit = v3BufferLen - settings.nSamplesInView

                        i1BufferLen = len(self.i1Buffer)
                        self.i1UpperLimit = i1BufferLen
                        self.i1LowerLimit = i1BufferLen - settings.nSamplesInView

                        i2BufferLen = len(self.i2Buffer)
                        self.i2UpperLimit = i2BufferLen
                        self.i2LowerLimit = i2BufferLen - settings.nSamplesInView

                        i3BufferLen = len(self.i3Buffer)
                        self.i3UpperLimit = i3BufferLen
                        self.i3LowerLimit = i3BufferLen - settings.nSamplesInView
                        self.mutex.unlock()

                    # Run trigger function
                    self.trigger(v1Value, v2Value, v3Value, i1Value, i2Value, i3Value)

                    if len(self.v1Buffer) > settings.maxBufferLength:
                        self.clearBuffers()

    def trigger(self, v1Value, v2Value, v3Value, i1Value, i2Value, i3Value):
        """Determine the range of indexes to be plotted for each buffer
        such that the moving signal can, somewhat, appear in the same
        place. This is based on the triggering function of oscilloscopes.

        This method is synchronized with the plotting using a mutex lock to
        avoid plotting while the indexes are being modified.

        Warning:
            If data is not repeating, do not run trigger function as it will
            not work.
        """
        self.mutex.lock()
        # Check trigger value
        if v1Value > self.v1TriggerValue:
            self.v1UpperLimit = len(self.v1Buffer)
            self.v1LowerLimit = self.v1UpperLimit - settings.nSamplesInView
            if self.v1LowerLimit < 0:
                self.v1LowerLimit = 0

        if v2Value > self.v2TriggerValue:
            self.v2UpperLimit = len(self.v2Buffer)
            self.v2LowerLimit = self.v2UpperLimit - settings.nSamplesInView
            if self.v2LowerLimit < 0:
                self.v2LowerLimit = 0

        if v3Value > self.v3TriggerValue:
            self.v3UpperLimit = len(self.v3Buffer)
            self.v3LowerLimit = self.v3UpperLimit - settings.nSamplesInView
            if self.v3LowerLimit < 0:
                self.v3LowerLimit = 0

        if i1Value > self.i1TriggerValue:
            self.i1UpperLimit = len(self.i1Buffer)
            self.i1LowerLimit = self.i1UpperLimit - settings.nSamplesInView
            if self.i1LowerLimit < 0:
                self.i1LowerLimit = 0

        if i2Value > self.i2TriggerValue:
            self.i2UpperLimit = len(self.i2Buffer)
            self.i2LowerLimit = self.i2UpperLimit - settings.nSamplesInView
            if self.i2LowerLimit < 0:
                self.i2LowerLimit = 0

        if i3Value > self.i3TriggerValue:
            self.i3UpperLimit = len(self.i3Buffer)
            self.i3LowerLimit = self.i3UpperLimit - settings.nSamplesInView
            if self.i3LowerLimit < 0:
                self.i3LowerLimit = 0        

        self.mutex.unlock()
    
    def clearBuffers(self):
        """If buffers get too large, clear them an only leave the data
        to be plotted in the current frame.
        
        This method is synchronized with the plotting using a mutex lock to
        avoid plotting while the buffers are being modified.
        """
        self.mutex.lock()

        del self.v1Buffer[:self.v1LowerLimit]
        self.v1LowerLimit = 0
        self.v1UpperLimit = len(self.v1Buffer)

        del self.v2Buffer[:self.v2LowerLimit]
        self.v2LowerLimit = 0
        self.v2UpperLimit = len(self.v2Buffer)

        del self.v3Buffer[:self.v3LowerLimit]
        self.v3LowerLimit = 0
        self.v3UpperLimit = len(self.v3Buffer)

        del self.i1Buffer[:self.i1LowerLimit]
        self.i1LowerLimit = 0
        self.i1UpperLimit = len(self.i1Buffer)

        del self.i2Buffer[:self.i2LowerLimit]
        self.i2LowerLimit = 0
        self.i2UpperLimit = len(self.i2Buffer)

        del self.i3Buffer[:self.i3LowerLimit]
        self.i3LowerLimit = 0
        self.i3UpperLimit = len(self.i3Buffer)

        self.mutex.unlock()





