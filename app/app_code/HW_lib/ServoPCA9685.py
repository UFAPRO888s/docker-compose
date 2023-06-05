# import time
import numpy as np
# Servo with PCA9685 implementation

# Configure min and max servo pulse lengths


def map(x, in_min, in_max, out_min, out_max):
    # return (x - in_min) * (out_max - out_min + 1) / (in_max - in_min + 1) + out_min
    return float(np.interp(x,[in_min, in_max],[out_min, out_max]))

class ServoPCA9685(object):
    min = 130 # Min pulse length out of 4096 / 150/112
    max = 510 # Max pulse length out of 4096 / 600/492
    def __init__(self, pca9685, channel):
        self.pca9685 = pca9685
        self.channel = channel
        self.set_pwm_freq(50)
        self.set_pulse(300)

    def set_pwm_freq(self, freq=50):
        self.pca9685.set_pwm_freq(freq)
        # time.sleep(0.005)

    def set_deg(self, q):
        self.set_pulse(int(map(q, 0, 180, self.min, self.max)))
        
    def set_rad(self, q):
        self.set_pulse(int(map(q, 0, np.pi, self.min, self.max)))
    
    def set_percent(self, q):
        self.set_pulse(int(map(q, -1.0, 1.0, self.min, self.max)))

    def set_pulse(self, pulse):
        if pulse >= self.min and pulse <= self.max:
            self.pca9685.set_pwm(self.channel, 0, pulse)
            # time.sleep(0.005)

    def disable(self):
        self.pca9685.set_pwm(self.channel, 0, 0)
        # time.sleep(0.005)
