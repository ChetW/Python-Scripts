# earlier version of code used IO expander for waking stepper motor, but that is now controlled by pin P8_26 directly from BBB
# import the smbus, adafruit, and time library if not already installed
#!/usr/bin/env python3
import Adafruit_BBIO.GPIO as GPIO
import smbus
import time
from progress.bar import ShadyBar


class StepperBar(ShadyBar):
        message="Deploying"
        


def enable():
        # P8_27 on BBB must be set to high to send power to stepper motor
        # P8_26 on BBB must be set to high to wake stepper motor
        GPIO.setup("P8_27", GPIO.OUT)
        GPIO.output("P8_27", GPIO.HIGH)
        time.sleep(1)
        GPIO.setup("P8_26", GPIO.OUT)
        GPIO.output("P8_26", GPIO.HIGH)
        GPIO.cleanup()

def disable():
        # P8_26 on BBB must be set to low to sleep stepper motor
        # P8_27 on BBB must be set to low to cut power to stepper motor
        GPIO.setup("P8_26", GPIO.OUT)
        GPIO.output("P8_26", GPIO.LOW)
        time.sleep(1)
        GPIO.setup("P8_27", GPIO.OUT)
        GPIO.output("P8_27", GPIO.LOW)
        GPIO.cleanup()

#stepper motor driver
ADD_SM = 0x60
                                                # register                      address def bits        bit fields
SLAVE_ADDR = 0x00               # slave address                 0x00    1100000         RSVD/ADDR/ADDR/ADDR/ADDR/ADDR/ADDR/ADDR
IC1_CON = 0x01                  # IC1 control                   0x01    0000000         TRQ/IN4/IN3/IN2/IN1/I2CBC/MODE/MODE
IC2_CON = 0x02                  # IC2 control                   0x02    0000000         CLRFLT/DISFLT/RSVD/DECAY/OCPR/OLDOD/OLDFD/OLDBO
SLR_STATUS1 = 0x03              # slew rate and fault1  0x03    0000000         RSVD/SLR/RSVD/nFAULT/OCP/OLD/TSDF/UVLOF
STATUS2 = 0x04                  # fault2                                0x04    0000000         OLD4/OLD3/OLD2/OLD1/OCP4/OCP3/OCP2/OCP1



def stepper_driver_execute(final_position,brake):
        BUS = 1
        bus = smbus.SMBus(BUS)
        seq_counter=0
        current_position=0
        fault=0
        faults=0
        enable()
        steps = int(abs(final_position-current_position)/0.00625)
        bar = StepperBar(max=steps)
        while current_position<final_position and fault==0:
                
                seq_counter=0
                step_skip=0
                if brake==0:
                    step1 = 0x44 
                    step2 = 0x4C 
                    step3 = 0x0C 
                    step4 = 0x2C 
                    step5 = 0x24 
                    step6 = 0x34 
                    step7 = 0x14 
                    step8 = 0x54 
                else:
                    step1 = 0x54 
                    step2 = 0x14 
                    step3 = 0x34 
                    step4 = 0x24 
                    step5 = 0x2C 
                    step6 = 0x0C 
                    step7 = 0x4C 
                    step8 = 0x44 
                # control register values to IC1
                steps = [step1,step2,step3,step4,step5,step6,step7,step8]
                #print(steps)
                while seq_counter<8 and step_skip<5 and fault==0:
                #step_skip is currently ignored in this loop
                        bus.write_byte_data(ADD_SM,IC2_CON,0x08)
                        time.sleep(0.005)
                        print("Command to IC1:",steps[seq_counter])
                        bus.write_byte_data(ADD_SM,IC1_CON,steps[seq_counter])
                        time.sleep(0.005)
                        SLAVE_ADDR_R = bus.read_byte_data(ADD_SM, SLAVE_ADDR)
                        time.sleep(0.005)
                        IC1_CON_R = bus.read_byte_data(ADD_SM, IC1_CON)
                        time.sleep(0.005)
                        IC2_CON_R = bus.read_byte_data(ADD_SM, IC2_CON)
                        time.sleep(0.005)
                        SLR_STATUS1_R = bus.read_byte_data(ADD_SM, SLR_STATUS1)
                        time.sleep(0.005)
                        STATUS2_R = bus.read_byte_data(ADD_SM, STATUS2)
                        time.sleep(0.005)
                        print("I2C Registers:",SLAVE_ADDR_R,IC1_CON_R,IC2_CON_R,SLR_STATUS1_R,STATUS2_R)
                        #if IC1_CON_R==steps[seq_counter]:
                        seq_counter=seq_counter+1
                        #else:
                        #        step_skip=step_skip+1
                        if SLR_STATUS1_R or STATUS2_R != 0x00:
                                faults+=1
                                fault=1
                                print('Fault detected in stepper motor driver!')
                                break

                        current_position=current_position+0.00625
                if current_position>=final_position:
                        print('Final position reached successfully!')
                else:
                        print("Distance in mm: ",current_position)
                        bar.next()
                if step_skip==5:
                        print('I2C register is not writing to IC1 correctly.')
                        break
        disable() #send command to disable stepper motor
        bar.finish()
        return final_position, faults

def main():
        brake=int(input("Type 0 CW, type 1 CCW"))
        #brake=0
        final_position=90
        print("Stepper motor will push the payload ",final_position," mm.")
        #stepper_driver_decision=input("Type Y and enter to continue")
        stepper_driver_decision="Y"
        if 'y' in stepper_driver_decision.lower():
                stepper_driver_execute(final_position,brake)

if __name__ == "__main__":
        main()