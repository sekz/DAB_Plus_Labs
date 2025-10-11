from rtlsdr import RtlSdr

# เชื่อมต่อ RTL-SDR
sdr = RtlSdr()
sdr.sample_rate = 2.4e6    
sdr.center_freq = 186360000      
sdr.gain = 'auto'

test_samples = sdr.read_samples(1024)
print(test_samples)

sdr.close()