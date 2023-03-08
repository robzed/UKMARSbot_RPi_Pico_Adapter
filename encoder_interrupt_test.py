from machine import Pin

ENCODER_LEFT_CLK = Pin(2, Pin.IN)		# output of XOR gate - no pull up required
ENCODER_RIGHT_CLK = Pin(3, Pin.IN)
ENCODER_LEFT_B = Pin(4, Pin.IN)		# the magnetic encoders have built in pull ups
ENCODER_RIGHT_B = Pin(5, Pin.IN)
        

# read and print the pin value
print(ENCODER_LEFT_CLK.value())
print(ENCODER_RIGHT_CLK.value())


# configure irq callback
ENCODER_LEFT_CLK.irq(lambda p:print(p, p.value()))
ENCODER_RIGHT_CLK.irq(lambda p:print(p, p.value()))
