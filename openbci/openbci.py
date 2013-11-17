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

    def _unpack_int32_value(self, value):
        # Little-endian integer
        return struct.unpack("<i", value)[0]

    def get_microvolts(self, int_value):
        """Here's the unpacking of the scale factor...

        * Internally, the digitizer in the ADS1299 chip spans zero to
          4.5 volts...that's the "4.5f".  Before the digitizer it (in
          my code) * configured for gain of 24x...that's the "24.0f".
          The ADS1299 takes * that span of (4.5V / 24) and breaks it
          into 2^24 values...that's the * "pow(2,24)".

          Those three values together would result in "volts per
          count".  Since I find microvolts more convenient than
          volts...

        * The "1000000.f" makes the result be microvolts instead of
          volts

          So, at this point you'd think that you'd be done.  But, I
          actually tested the OpenBCI board to make sure the
          conversion factor was correct.  I injected a variety of
          known signals at a range of amplitudes.  The reported
          amplitude was always off by a factor of two.  So, that final
          "2.0f" is the an addition to make the reported values line
          up with the known-true injected values.

          That's how you get: 
            (4.5f / 24.0 / pow(2,24)) * 1000000.f * 2.0f;

          -- e-mail from Chip
        """
        return 1e6 * (4.5/24) * float(int_value) / 2**23

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
            channels.append(self.get_microvolts(
                self._unpack_int32_value(
                    self.port.read(4))))

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
