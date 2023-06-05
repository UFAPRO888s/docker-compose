import logging
import time
import math

class MPU6050(object):
	# Default address:
	MPU6050_ADDRESS=0x68
	#some MPU6050 Registers and their Address
	PWR_MGMT_1=0x6B
	SMPLRT_DIV=0x19
	CONFIG=0x1A
	GYRO_CONFIG=0x1B
	INT_ENABLE=0x38
	ACCEL_XOUT_H=0x3B
	ACCEL_YOUT_H=0x3D
	ACCEL_ZOUT_H=0x3F
	GYRO_XOUT_H=0x43
	GYRO_YOUT_H=0x45
	GYRO_ZOUT_H=0x47
	def __init__(self, i2cBus, address=MPU6050_ADDRESS):
		self.i2cBus = i2cBus
		self.address = address
		self.begin()
	def begin(self):
		"""Initialize device"""
		#write to sample rate register
		self.i2cBus.write_byte_data(self.address, self.SMPLRT_DIV, 7)
		#Write to power management register
		self.i2cBus.write_byte_data(self.address, self.PWR_MGMT_1, 1)
		#Write to Configuration register
		self.i2cBus.write_byte_data(self.address, self.CONFIG, 0)
		#Write to Gyro configuration register
		self.i2cBus.write_byte_data(self.address, self.GYRO_CONFIG, 24)
		#Write to interrupt enable register
		self.i2cBus.write_byte_data(self.address, self.INT_ENABLE, 1)
		time.sleep(0.005)
	def read_raw_data(self,addr):
	#Accelero and Gyro value are 16-bit
		high = self.i2cBus.read_byte_data(self.address, addr)
		low = self.i2cBus.read_byte_data(self.address, addr+1)
		#concatenate higher and lower value
		value = ((high << 8) | low)
		#to get signed value from mpu6050
		if(value > 32768):
			value = value - 65536
		return value
	def get_accelerometer(self):
		acc_x = self.read_raw_data(self.ACCEL_XOUT_H)
		acc_y = self.read_raw_data(self.ACCEL_YOUT_H)
		acc_z = self.read_raw_data(self.ACCEL_ZOUT_H)
		Ax = acc_x/16384.0
		Ay = acc_y/16384.0
		Az = acc_z/16384.0
		return (Ax,Ay,Az)
	def get_gyroscope(self):
		gyro_x = self.read_raw_data(self.GYRO_XOUT_H)
		gyro_y = self.read_raw_data(self.GYRO_YOUT_H)
		gyro_z = self.read_raw_data(self.GYRO_ZOUT_H)
		Gx = gyro_x/131.0
		Gy = gyro_y/131.0
		Gz = gyro_z/131.0
		return (Gx,Gy,Gz)
	def set_address(self, address):
		"""Sets device address."""
		self.address = address
	def set_i2c_bus(self, i2cBus):
		"""Sets I2C Bus."""
		self.i2cBus = i2cBus
	def __enter__(self):
		return self