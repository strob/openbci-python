import serial
import struct
import time

class OpenBCI():
    BYTE_START = 0xA0
    BYTE_END = 0xC0
    NCHANNELS = 8
    DELAY = 5                   # seconds

    ACTIVATE = "qwertyui"
    DEACTIVATE = "12345678"

    def __init__(self, port="/dev/ttyACM0"):
        self.port = serial.Serial(
            port=port,
            baudrate=115200)

        # Stop anything that's currently happening
        self._send_cmd("s")

        time.sleep(self.DELAY)

        for i in range(8):
            if i < self.NCHANNELS:
                self._send_cmd(self.ACTIVATE[i])
            else:
                self._send_cmd(self.DEACTIVATE[i])

        # Start reading in binary
        self._send_cmd("b")

    def _send_cmd(self, cmd):
        self.port.write("%s\n" %(cmd))

    def _read_byte(self):
        return struct.unpack("B", self.port.read(1))[0]

    def _unpack_value(self, value):
        # Little-endian integer
        return struct.unpack("<i", value)[0] / float(2**23)

    def __iter__(self):
        return self

    def next(self):
        # Returns channel measurement as a list of 24bit integers

        while True:
            if self._read_byte() == self.BYTE_START:
                break

        nframes = self._read_byte()
        if nframes != (self.NCHANNELS+1) * 4:
            print "Malformed frame (%d frames): ignoring" % (nframes)
            return self.next()

        # Discard the so-called `sample_index'
        self.port.read(4)

        channels = []
        for _i in range(self.NCHANNELS):
            channels.append(self._unpack_value(self.port.read(4)))

        # Find the end
        if self._read_byte() == self.BYTE_END:
            return channels
        else:
            print "Frame broken at end: ignoring"
            return self.next()

if __name__=='__main__':
    import sys

    USAGE = "python openbci.py /dev/OPENBCI_PORT"

    if len(sys.argv) != 2:
        print USAGE
        sys.exit(1)

    for val in OpenBCI(port=sys.argv[1]):
        print val
