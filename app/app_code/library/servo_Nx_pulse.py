
import time
import smbus
import PCA9685
import ServoPCA9685
import MotorPCA9685
i2cBus = smbus.SMBus(0)
pca9685 = PCA9685.PCA9685(i2cBus)
servo00 = ServoPCA9685.ServoPCA9685 (pca9685, PCA9685.CHANNEL00)
servo01 = ServoPCA9685.ServoPCA9685 (pca9685, PCA9685.CHANNEL01)
# servo02 = ServoPCA9685.ServoPCA9685 (pca9685, PCA9685.CHANNEL02)
# servo03 = ServoPCA9685.ServoPCA9685 (pca9685, PCA9685.CHANNEL03)
motor01 = MotorPCA9685.MotorPCA9685 (pca9685, PCA9685.CHANNEL12,PCA9685.CHANNEL13)
motor02 = MotorPCA9685.MotorPCA9685 (pca9685, PCA9685.CHANNEL14,PCA9685.CHANNEL15)

# 130 -> 510 
for pulse in  range (ServoPCA9685.servo_min, ServoPCA9685.servo_max + 1 ):
    servo00.set_pulse(pulse)
    servo01.set_pulse(pulse)
    time.sleep(0.01)

# 510 -> 130
for pulse in reversed(range(ServoPCA9685.servo_min, ServoPCA9685.servo_max + 1)):
    servo00.set_pulse(pulse)
    servo01.set_pulse(pulse)
    time.sleep(0.01)
servo00.disable()
servo01.disable()

# -100 -> 100 
for pwm in  range (-100, 100 ):
    motor01.set_percent(pwm)
    motor02.set_percent(pwm)
    time.sleep(0.1)

# 100 -> -100 
for pwm in  reversed(range (-100, 100 )):
    motor01.set_percent(pwm)
    motor02.set_percent(pwm)
    time.sleep(0.1)


motor01.disable()
motor02.disable()
