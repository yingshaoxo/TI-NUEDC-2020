"""
We handle ad1292 here
"""


from struct import pack, unpack
from time import sleep
from machine import SPI, Pin


CONFIG_SPI_MASTER_DUMMY = 0xFF

# Register Read Commands
RREG = 0x20  # Read n nnnn registers starting at address r rrrr
# first byte 001r rrrr (2xh)(2) - second byte 000n nnnn(2)
WREG = 0x40  # Write n nnnn registers starting at address r rrrr
# first byte 010r rrrr (2xh)(2) - second byte 000n nnnn(2)

START = 0x08  # Start/restart (synchronize) conversions
STOP = 0x0A  # Stop conversion
RDATAC = 0x10  # Enable Read Data Continuous mode.

# This mode is the default mode at power-up.
SDATAC = 0x11  # Stop Read Data Continuously mode
RDATA = 0x12  # Read data by command; supports multiple read back.

# Pin declartion the other you need are controlled by the SPI library
ADS1292_DRDY_PIN = Pin(6)
ADS1292_CS_PIN = Pin(7)
ADS1292_START_PIN = Pin(5)
ADS1292_PWDN_PIN = Pin(4)

# register address
ADS1292_REG_ID = 0x00
ADS1292_REG_CONFIG1 = 0x01
ADS1292_REG_CONFIG2 = 0x02
ADS1292_REG_LOFF = 0x03
ADS1292_REG_CH1SET = 0x04
ADS1292_REG_CH2SET = 0x05
ADS1292_REG_RLDSENS = 0x06
ADS1292_REG_LOFFSENS = 0x07
ADS1292_REG_LOFFSTAT = 0x08
ADS1292_REG_RESP1 = 0x09
ADS1292_REG_RESP2 = 0x0A


class MyADS1292():
    def __init__(self):
        self.spi = SPI(id=2, baudrate=1000000, polarity=0, phase=1)

        self.reset()
        sleep(0.1)

        self.disable_start()
        self.enable_start()

        self.hard_stop()
        self.start_data_conv_command()
        self.soft_stop()
        sleep(0.05)
        self.stop_read_data_continuous()
        sleep(0.3)

        self.reg_write(ADS1292_REG_CONFIG1, 0x00)
        sleep(0.01)
        self.reg_write(ADS1292_REG_CONFIG2, 0b10100000)
        sleep(0.01)
        self.reg_write(ADS1292_REG_LOFF, 0b00010000)
        sleep(0.01)
        self.reg_write(ADS1292_REG_CH1SET, 0b01000000)
        sleep(0.01)
        self.reg_write(ADS1292_REG_CH2SET, 0b01100000)
        sleep(0.01)
        self.reg_write(ADS1292_REG_RLDSENS, 0b00101100)
        sleep(0.01)
        self.reg_write(ADS1292_REG_LOFFSENS, 0x00)
        sleep(0.01)
        self.reg_write(ADS1292_REG_RESP1, 0b11110010)
        sleep(0.01)
        self.reg_write(ADS1292_REG_RESP2, 0b00000011)
        sleep(0.01)
        self.start_read_data_continuous()
        sleep(0.01)
        self.enable_start()

    def read_data(self):
        ADS1292_CS_PIN.off()
        bytes_return = self.spi.read(CONFIG_SPI_MASTER_DUMMY, 10)
        ADS1292_CS_PIN.on()
        return bytes_return

    def reset(self):
        ADS1292_PWDN_PIN.on()
        sleep(0.1)
        ADS1292_PWDN_PIN.off()
        sleep(0.1)
        ADS1292_PWDN_PIN.on()

    def disable_start(self):
        ADS1292_START_PIN.off()
        sleep(0.02)

    def enable_start(self):
        ADS1292_START_PIN.on()
        sleep(0.02)

    def hard_stop(self):
        ADS1292_START_PIN.off()
        sleep(0.1)

    def soft_stop(self):
        self.spi_command_data(STOP)

    def start_data_conv_command(self):
        self.spi_command_data(START)

    def spi_write(self, data):
        if isinstance(data, bytes):
            self.spi.write(bytearray(data))
        else:
            self.spi.write(bytearray([data]))

    def spi_command_data(self, data_in):
        ADS1292_CS_PIN.off()
        sleep(0.002)
        ADS1292_CS_PIN.on()
        sleep(0.002)
        ADS1292_CS_PIN.off()
        sleep(0.002)
        self.spi_write(data_in)
        sleep(0.002)
        ADS1292_CS_PIN.on()

    def start_read_data_continuous(self):
        self.spi_command_data(RDATAC)

    def stop_read_data_continuous(self):
        self.spi_command_data(SDATAC)

    def reg_write(self, read_write_address, DATA):
        if read_write_address == 1:
            DATA = DATA & 0x87
        elif read_write_address == 2:
            DATA = DATA & 0xFB
            DATA |= 0x80
        elif read_write_address == 3:
            DATA = DATA & 0xFD
            DATA |= 0x10
        elif read_write_address == 7:
            DATA = DATA & 0x3F
        elif read_write_address == 8:
            DATA = DATA & 0x5F
        elif read_write_address == 9:
            DATA |= 0x02
        elif read_write_address == 10:
            DATA = DATA & 0x87
            DATA |= 0x01
        elif read_write_address == 11:
            DATA = DATA & 0x0F

        dataToSend = read_write_address | WREG
        ADS1292_CS_PIN.off()
        sleep(0.002)
        ADS1292_CS_PIN.on()
        sleep(0.002)
        ADS1292_CS_PIN.off()
        sleep(0.002)
        self.spi_write(dataToSend)
        self.spi_write(0x00)
        self.spi_write(DATA)

        sleep(0.002)
        ADS1292_CS_PIN.on()


def main():
    print("Welcome to RT-Thread MicroPython!")


if __name__ == '__main__':
    main()
