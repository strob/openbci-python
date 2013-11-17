import numpy as np
from scipy.signal import hamming

def nearestneighbor_filter_bank(fft_freqs, output_freqs):
    # Returns a NxM matrix where N is the number of fft_freqs and M is
    # the number of output_freqs
    filter_bank = np.zeros((fft_freqs.shape[0], output_freqs.shape[0]))

    for output_idx, freq in enumerate(output_freqs):
        # pass through the closest fft frequency
        fft_center_idx = np.argmin(abs(fft_freqs - freq))
        filter_bank[fft_center_idx, output_idx] = 1

    return filter_bank

def triangular_filter_bank(fft_freqs, output_freqs, base_width=12):
    filter_bank = np.zeros((fft_freqs.shape[0], output_freqs.shape[0]))

    for output_idx, output_freq in enumerate(output_freqs):
        # pass through the closest fft frequency
        fft_center_idx = np.argmin(abs(fft_freqs - output_freq))
        fft_start_idx = max(0, fft_center_idx - base_width/2)
        fft_end_idx = min(len(fft_freqs)-1, fft_center_idx + base_width/2)

        # Accumulate distance from desired output frequency
        triangle_vector = []
        for fft_idx in range(fft_start_idx, fft_end_idx):
            triangle_vector.append(abs(fft_freqs[fft_idx] - output_freq))

        # Invert & normalize triangle_vector
        triangle_vector = np.array(triangle_vector)
        triangle_vector = abs(triangle_vector - max(triangle_vector))
        triangle_vector /= sum(triangle_vector)

        filter_bank[fft_start_idx:fft_end_idx, output_idx] = triangle_vector

    return filter_bank
    
def get_spectra(a, hamm, fbank):
    return np.dot(abs(np.fft.fft(a * hamm)), fbank)

class Spectra():
    def __init__(self, out_freqs, fft_len=250, R=250):
        fft_freqs = np.fft.fftfreq(fft_len, 1.0/R)
        self.fbank = triangular_filter_bank(fft_freqs, out_freqs, base_width=8)
        self.hamm = hamming(fft_len, sym=0)

    def compute(self, a):
        return get_spectra(a, self.hamm, self.fbank)

if __name__=='__main__':
    from openbci import OpenBCI

    import sys
    if len(sys.argv) == 2:
        datagen = OpenBCI(sys.argv[1])
    else:
        import random
        def fakedata():
            while True:
                yield [random.random() for _x in range(8)]
        datagen = fakedata()

    out_freqs = np.linspace(2, 30, 15)
    spec = Spectra(out_freqs=out_freqs)

    vbuffer = []
    for idx,val in enumerate(datagen):
        vbuffer.append(val)
        if len(vbuffer) > 250:
            vbuffer.pop(0)
            if idx % 50 == 0:
                varray = np.array(vbuffer)
                for probe in range(varray.shape[1]):
                    res = spec.compute(varray[:,probe])
                    print res
