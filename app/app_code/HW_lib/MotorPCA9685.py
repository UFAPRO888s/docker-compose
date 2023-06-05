import time
# Servo with PCA9685 implementation

# Configure min and max servo pulse lengths
motor_min = 0 # Min pulse length out of 4096 / 150/112
motor_max = 4096 # Max pulse length out of 4096 / 600/492

def map(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min + 1) / (in_max - in_min + 1) + out_min

class MotorPCA9685(object):
    def __init__(self, pca9685, channel0,channel1,dir=1):
        self.pca9685 = pca9685
        self.channel0 = channel0
        self.channel1 = channel1
        self.dir = 1.0 if dir == 1 else -1.0
        self.set_pwm_freq(50)
        self.disable()

    def set_pwm_freq(self, freq=50):
        self.pca9685.set_pwm_freq(freq)
        # time.sleep(0.005)

    def set_percent(self, p):
        p=p*self.dir
        if p < 0:
            self.set_pulse(self.channel0,map(-p, 0, 100, motor_min, motor_max))
            self.set_pulse(self.channel1,0 )
        else:
            self.set_pulse(self.channel1,map(p, 0, 100,motor_min,motor_max))
            self.set_pulse(self.channel0,0 )


    def set_pulse(self,channel, pulse):
        if pulse >= motor_min and pulse <= motor_max:
            self.pca9685.set_pwm(channel, 0,int(pulse))
            # time.sleep(0.005)

    def disable(self):
        self.pca9685.set_pwm(self.channel0, 0, 0)
        self.pca9685.set_pwm(self.channel1, 0, 0)
        # time.sleep(0.005)
