from multiplexer import multiplex
import smbus
import numpy as np
import time
import Adafruit_BBIO.GPIO as GPIO


# Turn on devices (load switches and EPS output channels need to be turned on.
# EPS Channel 4: Multiplexer > output 4 1 0
# EPS Channel 5: IO Expander > output 5 1 0
# EPS Channel 6: CAN Tranceiver > output 6 1 0
# Load Switch U4: Magnetorquer Driver > GPIO2_24
# Load Switch U5: Stepper Motor Driver > GPIO2_22 AND also turn on GPIO1_29 to wake stepper motor
# Disable reset for Multiplexer > GPIO2_25 and IO Expander > GPIO2_23 

#Magnetorquer Load Switch
GPIO.setup("GPIO2_24", GPIO.OUT)
GPIO.output("GPIO2_24", GPIO.HIGH)
GPIO.cleanup()

#IO Expander Reset
GPIO.setup("GPIO2_23", GPIO.OUT)
GPIO.output("GPIO2_23", GPIO.HIGH)
GPIO.cleanup()

#Stepper Motor Load Switch
GPIO.setup("GPIO2_22", GPIO.OUT)
GPIO.output("GPIO2_22", GPIO.HIGH)
GPIO.cleanup()

#Stepper Motor Sleep (Wake)
GPIO.setup("GPIO1_29", GPIO.OUT)
GPIO.output("GPIO1_29", GPIO.HIGH)
GPIO.cleanup()

#Multiplexer Reset
GPIO.setup("GPIO2_25", GPIO.OUT)
GPIO.output("GPIO2_25", GPIO.HIGH)
GPIO.cleanup()

def solar_panel_I2C(multiplexer,mult_register, action, channel):
  bus.write_byte_data(multiplexer,mult_register, action)
  time.sleep(1)
  try:
    data = bus.read_i2c_block_data(0x4a, 0x00, 2)
    temp_I2C(data);
  except:
    try:
      data = bus.read_i2c_block_data(0x4c, 0x00, 2)
      temp_I2C(data);
   except:
      try:
        data = bus.read_i2c_block_data(0x4e, 0x00, 2)
        temp_I2C(data);
      except:
        try:
          data = bus.read_i2c_block_data(0x48, 0x00, 2)
          temp_I2C(data);
        except:
        # Output error to screen
          print("Temperature Sensor not connected on channel "+str(channel))

def temp_I2C(data):  
    # Convert the data to 12-bits
    temp = (data[0] * 256 + (data[1] & 0xF0)) / 16
    if temp > 2047 :
      temp -= 4096
    cTemp = temp * 0.0625
    fTemp = cTemp * 1.8 + 32

    # Output data to screen
    print("Temperature in Celsius on channel "+str(channel)+" is : %.2f C" %cTemp)
    print("Temperature in Fahrenheit on channel "+str(channel)+" is : %.2f F" %fTemp)
def magnetorquer_I2C(multiplexer,mult_register, action, channel,read_address):
  bus.write_byte_data(multiplexer,mult_register, action)
  time.sleep(1)
  try:
    bus.write_byte_data(read_address,0x01,0x00)
    bus.write_byte_data(read_address,0x00,0x00)
    read_data = bus.read_byte_data(read_address,0x00)
    print("Magnetorquer Driver connected on channel "+str(channel)+". Control Reg: ",read_data)
  except:
  # Output error to screen
    print("Magnetorquer Driver not connected on channel "+str(channel))

def stepper_I2C():
  try:
    read_data = bus.read_byte_data(0x60,0x00)
    print("Stepper Driver connected on address 0x60")
  except:
    # Output error to screen
    print("Stepper Driver  not connected on address 0x60. Check if H2.18 is low instead of high.")


# On the I2C Expander, we need to enable channel 0 for us to see solar panel temperature sensor and magnetometer
# We first define the bus is 1, the address of the I2C expander (0x70), and we write to register 4 to enable channels
bus = smbus.SMBus(1)
multiplexer = 0x70
mult_register = 0x04
channel = 0
while channel < 7:
  if (channel==0):
     action = 0x01
     solar_panel_I2C(multiplexer,mult_register, action, channel)
     time.sleep(1)
  elif (channel==1):
     action = 0x02
     solar_panel_I2C(multiplexer,mult_register, action, channel)
     time.sleep(1)
  elif (channel==2):
     action = 0x04
     solar_panel_I2C(multiplexer,mult_register, action, channel)
     time.sleep(1)
  elif (channel==3):
     action = 0x08
     solar_panel_I2C(multiplexer,mult_register, action, channel)
     time.sleep(1)
  elif (channel==4):
     action = 0x10
     read_address=0x61
     magnetorquer_I2C(multiplexer,mult_register, action, channel,read_address)
     time.sleep(1)
  elif (channel==5):
     action = 0x20
     read_address=0x63
     magnetorquer_I2C(multiplexer,mult_register, action, channel,read_address)
     time.sleep(1)
  elif (channel==6):
     action = 0x40
     read_address=0x64
     magnetorquer_I2C(multiplexer,mult_register, action, channel,read_address)
     time.sleep(1)
  channel = channel + 1

try:
    hex_data = bus.read_byte_data(0x20, 0x00)
    print('IO Expander connected on address 0x20.')
    IN0 = bus.read_byte_data(0x20, 0x00)
    IN1 = bus.read_byte_data(0x20, 0x01)
    OUT0 = bus.read_byte_data(0x20, 0x02)
    OUT1 = bus.read_byte_data(0x20, 0x03)
    print(IN0,IN1,OUT0,OUT1)

except Exception:
    print('ERROR: Cannot read data from IO Expander')

    
stepper_I2C()
