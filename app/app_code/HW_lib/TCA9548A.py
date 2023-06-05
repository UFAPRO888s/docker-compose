# import time
current_lane=None
class TCA9548A(object):
    I2C_ch=[0b00000001<<i for i in range(0,8)]
    def __init__(self, bus, channel, address=0x70,):
        self.i2c_address = address
        self.i2c_bus = bus
        self.channel = channel
        print(self.setup())
    def setup(self,):
        try:
            self.lane_check()
            return 1, "Success"
        except Exception as msg:
            return 0, "Fail: {}".format(msg)
    def lane_check(self):
        global current_lane
        if current_lane != self.channel:
            # print("changing channel")
            self.i2c_bus.write_byte(self.i2c_address, self.I2C_ch[self.channel])
            current_lane = self.channel
        else:
            # print("recall channel")
            pass
        
    def write_byte_data(self, address,data,length):
        self.lane_check()
        # time.sleep(0.01)
        self.i2c_bus.write_byte_data(address,data,length)

    def read_byte_data(self, address1,address2):
        self.lane_check()
        # time.sleep(0.01)
        return self.i2c_bus.read_byte_data(address1,address2)
    
    def write_byte(self, address,data):
        self.lane_check()
        # time.sleep(0.01)
        self.i2c_bus.write_byte(address,data)

    def read_byte(self, address):
        self.lane_check()
        # time.sleep(0.01)
        return self.i2c_bus.read_byte(address)
    
    def write_i2c_block_data(self, address1,address2,data):
        self.lane_check()
        # time.sleep(0.01)
        self.i2c_bus.write_i2c_block_data(address1,address2,data)

    def read_i2c_block_data(self, address1,address2,length):
        self.lane_check()
        # time.sleep(0.01)
        return self.i2c_bus.read_i2c_block_data(address1,address2,length)
    
    def i2c_rdwr(self,write, read):
        self.lane_check()
        # time.sleep(0.01)
        self.i2c_bus.i2c_rdwr(write, read)
        
    def i2c_rdwr(self,msg):
        self.lane_check()
        # time.sleep(0.01)
        self.i2c_bus.i2c_rdwr(msg)

    def read(self):
        # time.sleep(0.01)
        return self.i2c_bus.read_byte(self.i2c_address)