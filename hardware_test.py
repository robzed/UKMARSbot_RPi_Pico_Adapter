from machine import Pin, ADC, PWM
from time import sleep, sleep_ms, sleep_us

#import micropython
#micropython.alloc_emergency_exception_buf(100)

class MotorEncoders:
    def __init__(self):
        self.ENCODER_LEFT_CLK = Pin(2, Pin.IN)		# output of XOR gate - no pull up required
        self.ENCODER_RIGHT_CLK = Pin(3, Pin.IN)
        self.ENCODER_LEFT_B = Pin(4, Pin.IN)		# the magnetic encoders have built in pull ups
        self.ENCODER_RIGHT_B = Pin(5, Pin.IN)
        self.left_oldA = 0
        self.left_oldB = 0
        self.right_oldA = 0
        self.right_oldB = 0
        # encoder polarity is either 1 or -1 and is used to account for reversal of the encoder phases
        self.ENCODER_LEFT_POLARITY = -1
        self.ENCODER_RIGHT_POLARITY = 1
        
        self.m_left_counter = 0
        self.m_right_counter = 0
    
    def enable_interrupts(self):
        self.ENCODER_LEFT_CLK.irq(trigger=machine.Pin.IRQ_FALLING | machine.Pin.IRQ_RISING, handler=self.left_input_change)
        self.ENCODER_RIGHT_CLK.irq(trigger=machine.Pin.IRQ_FALLING | machine.Pin.IRQ_RISING, handler=self.right_input_change)
        
    def left_input_change(self):
        newB = self.ENCODER_LEFT_B.value()
        newA = self.ENCODER_LEFT_CLK.value() ^ newB
        delta = self.ENCODER_LEFT_POLARITY * ((left_oldA ^ newB) - (newA ^ left_oldB))
        self.m_left_counter += delta
        left_oldA = newA
        left_oldB = newB

    def right_input_change(self):
        newB = self.ENCODER_RIGHT_B.value()
        newA = self.ENCODER_RIGHT_CLK.value() ^ newB
        delta = self.ENCODER_RIGHT_POLARITY * ((right_oldA ^ newB) - (newA ^ right_oldB))
        self.m_right_counter += delta
        right_oldA = newA
        right_oldB = newB
        
    def poll_print(self, duration_in_ms):
        # hacky test for inputs changing state
        oldLB = None
        oldLC = None
        oldRB = None
        oldRC = None
        print("LB LC RB RC")
        for _ in range(duration_in_ms//10):
            LB = self.ENCODER_LEFT_B.value()
            LC = self.ENCODER_LEFT_CLK.value()
            RB = self.ENCODER_RIGHT_B.value()
            RC = self.ENCODER_RIGHT_CLK.value()
            if LB != oldLB or LC != oldLC or RB != oldRB or RC != oldRC:
                print(LB, LC, RB, RC)
                oldLB = LB
                oldLC = LC
                oldRB = RB
                oldRC = RC
            sleep_ms(10)
            
    def printf(self):
        print(self.m_right_counter, self.m_left_counter)

class D13LED_or_Buzzer:
    def __init__(self):
        self.p13 = Pin(13, Pin.OUT)    # create output pin on GPIO
        self.p13.off()
    def on(self):
        self.p13.on()
    def off(self):
        self.p13.off()
    def toggle(self):
        self.p13.toggle()
    def setval(self, value):
        self.p13.value(value)             # set pin to on/high

class sensorLEDs:
    def __init__(self):
        self.p6 = Pin(6, Pin.OUT)    # create output pin on GPIO
        self.p6.off()
        self.p11 = Pin(11, Pin.OUT)    # create output pin on GPIO
        self.p11.off()
    def right(self, value):
        self.p6.value(value)
    def left(self, value):
        self.p11.value(value)
    def toggle(self):
        self.p6.toggle()
        self.p11.toggle()
        

class MUX:
    def __init__(self):
        self.s0 = Pin(20, Pin.OUT)
        self.s1 = Pin(21, Pin.OUT)
        self.s2 = Pin(22, Pin.OUT)

    def channel(self, value):
        if value >= 0 and value <= 7:
            self.s0.value(1 & value)
            self.s1.value(1 & (value>>1))
            self.s2.value(1 & (value>>2))

class basic_ADC_Read:
    def __init__(self, adc_channel):
        self.adc = ADC(adc_channel)
        
    def read(self):
        return self.adc.read_u16()
    
    def block_read(self, _):
        return self.adc.read_u16()
        
class Muxed_ADC_Read:
    def __init__(self):
        self.mux = MUX()
        self.adc = ADC(Pin(28))

    def read(self):
        # whatever channel was selected last timeb
        return self.adc.read_u16()
    
    def block_read(self, channel):
        self.mux.channel(channel)
        sleep_ms(1)
        return self.adc.read_u16()

class GenericMotor:
    def __init__(self, dir_pin, pwm_pin):
        self._dir_pin = dir_pin
        self._pwm_pin = pwm_pin
        
        self.dir = Pin(dir_pin, Pin.OUT)
        self.pwm = Pin(pwm_pin, Pin.OUT)
        self.direction_reg = 1
        self.PWM_mode = False
        self.stop()

    def set_PWM_mode(self):
        pass
        #pwm0 = PWM(Pin(0))      # create PWM object from a pin
        #pwm0.freq()             # get current frequency
        #pwm0.freq(1000)         # set frequency
        #pwm0.duty_u16()         # get current duty cycle, range 0-65535
        #pwm0.duty_u16(200)      # set duty cycle, range 0-65535
        #pwm0.deinit()           # turn off PWM on the pin
    
    def set_reverse(self):
        self.direction_reg = 0
        
    def full_forward(self):
        self.dir.value(self.direction_reg)
        self.pwm.value(1)
        
    def full_reverse(self):
        self.dir.value(1-self.direction_reg)
        self.pwm.value(1)

    def stop(self):
        self.pwm.value(0)
        
        
class LeftMotor(GenericMotor):
    def __init__(self):
        lmotorDIR     = 7  # Left motor dirn input
        lmotorPWM     = 9  # Left motor PWM pin
        super(LeftMotor, self).__init__(lmotorDIR, lmotorPWM)
        self.set_reverse()

class RightMotor(GenericMotor):
    def __init__(self):
        rmotorDIR     = 8  # Right motor dirn input
        rmotorPWM     = 10 # Right motor PWM pin
        super(RightMotor, self).__init__(rmotorDIR, rmotorPWM)


# these assume 0-1023 range
adc_thesholds = [ 660, 647, 630, 614, 590, 570, 545, 522, 461, 429, 385, 343, 271, 212, 128, 44, 0 ]

def function_decode(switches_adc):
    # use code from ukmarsbot project
    switches_adc = (switches_adc * 1023) // 65535
    if switches_adc > 800:
        return 16
    else:
        for i in range(16):
          if switches_adc > ((adc_thesholds[i] + adc_thesholds[i + 1]) / 2):
            return i
        return -1

def do_menu():
    print()
    print("1 = Indicator test")
    print("2 = ADC test")
    print("3 = Motor Left Full Forward 1 second")
    print("4 = Motor Left Full Reverse 1 second")
    print("5 = Motor Right Full Forward 1 second")
    print("6 = Motor Right Full Reverse 1 second")
    print("7 = Slow MUX cycle")
    print("8 = Button Watch")
    print("9 = Motor cycling")
    print("rmf rmr lmf rmr = right/left motor forward/reverse")
    print("enc = encoder test")
    print("stop = stop motor")
    print("bat = battery variation test")
    print("adc0 = variation test on ADC0")
    print("adc = read 4 on board ADCs")
    print("Q = Quit")
    print()
    return input("Select ")


def double_beep(d13):
    d13.on()
    sleep(0.2)
    d13.off()
    sleep(0.2)
    d13.on()
    sleep(0.2)
    d13.off()


#
# global variables for hardware - so they can be accessed from REPL interpreter\
#
d13 = D13LED_or_Buzzer()

indicators = sensorLEDs()
adc = Muxed_ADC_Read()
adc0 = basic_ADC_Read(0)
adc1 = basic_ADC_Read(1)
#adc2 = basic_ADC_Read(2)
adc3 = basic_ADC_Read(3)
lmotor = LeftMotor()
rmotor = RightMotor()
encoders = MotorEncoders()


def main():
    double_beep(d13)

    while True:
        option = do_menu().strip().lower()
        if option == "1":
            for _ in range(10):
                # double flash right, single flash left
                indicators.right(1)
                indicators.left(0)
                sleep(0.2)
                indicators.right(0)
                sleep(0.2)
                indicators.right(1)
                sleep(0.2)
        
                indicators.left(1)
                indicators.right(0)
                sleep(0.25)
        elif option == "2":
            for _ in range(60):
                #for i in range(8):
                #    print(i, analogue.block_read(i))
                adc7 = adc.block_read(7)
                voltage = adc7 / 65535 * 3.3
                print("Battery ADC =", adc7, ", ADC voltage =", voltage, "volts, Battery voltage (after diode)", (voltage / 10) * 32, "volts")
                function_adc = adc.block_read(6)
                print("function =", function_adc)
                print(adc.block_read(0), adc.block_read(1), adc.block_read(2), adc.block_read(3), adc.block_read(4), adc.block_read(5))
                sleep(0.5)
        elif option == "3" or option == "lmf":
            lmotor.full_forward()
            if option == "3":
                sleep(1)
                lmotor.stop()
        elif option == "4" or option == "lmr":
            lmotor.full_reverse()
            if option == "4":
                sleep(1)
                lmotor.stop()
        elif option == "5" or option == "rmf":
            rmotor.full_forward()
            if option == "5":
                sleep(1)
                rmotor.stop()
        elif option == "6" or option == "rmr":
            rmotor.full_reverse()
            if option == "6":
                sleep(1)
                rmotor.stop()
        elif option == '7':
            indicators.left(0)
            indicators.right(0)
            for _ in range(30):
                for i in range(8):
                    indicators.toggle()
                    adc_reading = adc.block_read(i)
                    print("ADC", i, "=", adc_reading)
                    sleep(2)

        elif option == '8':
            last = None
            for _ in range(600):
                function_adc = adc.block_read(6)
                actual = function_decode(function_adc)
                if actual == 16:
                    output = "Button"
                elif actual == -1:
                    output = "Invalid"
                else:
                    output = '{0:04b}'.format(actual)
                if last != output:
                    print("function =", function_adc, '{0:04x}'.format(function_adc), (function_adc * 1023) // 65535, actual, output)
                    last = output
                sleep(0.1)
        
        elif option == '9':
            for _ in range(30):
                lmotor.full_forward()
                sleep(1)
                lmotor.stop()
                lmotor.full_reverse()
                sleep(1)
                lmotor.stop()
                rmotor.full_forward()
                sleep(1)
                rmotor.stop()
                rmotor.full_reverse()
                sleep(1)
                rmotor.stop()
        
        elif option == 'stop':
            lmotor.stop()
            rmotor.stop()
            
        elif option == 'enc':
            print("Left Forward")
            lmotor.full_forward()
            encoders.poll_print(200)
            lmotor.stop()
            sleep(0.5)

            print("Left Reverse")
            lmotor.full_reverse()
            encoders.poll_print(200)
            lmotor.stop()
            sleep(0.5)
            
            print("Right Forward")
            rmotor.full_forward()
            encoders.poll_print(200)
            rmotor.stop()
            sleep(0.5)
            
            print("Right Reverse")
            rmotor.full_reverse()
            encoders.poll_print(200)
            rmotor.stop()
        
        
        elif option == 'bat' or option == 'adc0' or option == 'adc1' or option == 'adc2' or option == 'adc3':
            Vmax = -1
            Vmin = 100
            ADCmax = 0
            ADCmin = 0
            count = 0
            Vsum = 0
            if option == 'bat':
                this_adc = adc
            elif option == 'adc0':
                this_adc = adc0
            elif option == 'adc1':
                this_adc = adc1
            elif option == 'adc2':
                this_adc = adc2
            else:
                this_adc = adc3
            print("Bat test running...")
            for i in range(500):
                adc7 = this_adc.block_read(7)
                voltage = adc7 / 65535 * 3.3
                voltage = (voltage / 10) * 32
                Vsum += voltage
                count += 1
                if voltage > Vmax:
                    Vmax = voltage
                    ADCmax = adc7
                if voltage < Vmin:
                    Vmin = voltage
                    ADCmin = adc7
                print(adc7, end=',')
            Vaverage = Vsum / count
            print()
            print("Count =", count, "  Battery Voltage =", Vmin, Vaverage, Vmax, "  ADC =", ADCmin, ADCmax, "ADC hex (min,last,max) {:04x} {:04x} {:04x}".format(ADCmin, adc7, ADCmax))
            print("Variation", 100*(Vmin-Vaverage)/Vaverage, "%  ", 100*(Vmax-Vaverage)/Vaverage, "%")

        elif option == 'adc':
            print(adc0.read())
            print(adc1.read())
            print(adc.read())
            print(adc3.read())
        
        elif option == 'adc0mon' or option == 'adc1mon':
            time_to_wait_per_reading_seconds = 0.2
            time_to_monitor_seconds = 30
            if option == 'adc0mon':
                myadc = adc0
            else:
                myadc = adc1
            for _ in range(time_to_monitor_seconds/time_to_wait_per_reading_seconds):
                print(myadc.read()*3.3/65535, end='v ')
                sleep(time_to_wait_per_reading_seconds)
            print()
        
        elif option == 'adc0pat' or option == 'adc1pat':
            time_to_wait_per_reading_seconds = 0.2
            time_to_monitor_seconds = 30
            if option == 'adc0pat':
                myadc = adc0
            else:
                myadc = adc1
            for _ in range(time_to_monitor_seconds/time_to_wait_per_reading_seconds):
                value = myadc.read()
                print('{:04x} {:012b}'.format(value, value//16))	# bottom 4 bit meaningless duplication of top 4 bits
                sleep(time_to_wait_per_reading_seconds)
            print()
            
        elif option == 'q':
            break
        
        else:
            print("Unknown")
 
        d13.on()
        sleep(0.1)
        d13.off()
    
main()



