# Using the Cytron Maker Nano RP2040 with the UKMARSBot
Written up by Rob Probin, August 2023, based on original notes by David Hannaford.

[Maker Nano RP2040](images/Maker_Nano_RP2040.jpg)


## Introduction

The Cytron Maker Nano RP2040 is a cheap alternative to the Arduino Nano, with 
the much more powerful RP2040 microcontroller - the same micro used on the Raspberry Pi Pico. 

This can run:
 - in the Arduino environment, 
 - in standard C/C++ with the Pico SDK,
 - in Micropython,
 - in CircuitPython,
 - in Forth, with Zeptoforth and meCrisp Forth.

However this unit only has 4 ADC inputs, which is a limitation, since the UKMARSBot
as designed uses more than this - details below.

Although the Maker Nano RP2040 supplies 5v, we will run the UKMARSbot logic 
exclusively at 3v because the I/O of the RP2040 is exclusively 3.3v. So we 
take care to disconnect the 5v power before use so that the RP2040 is not 
damaged.


## Modification Steps

### Stage 1: XOR and Battery Voltage

Summary:
 1. Replacing the 74LS86 to a 74HC86 Exclusive-OR gate - so that the XOR gate runs at 3v logic.
    If you already build the UKMARSbot with a 74HC86 then you are done!
    If you haven't built it - you can use the 74HC86 at 5v and 3.3v - so you can use it with the original
    Arduino Nano if you choose not to use the Maker Nano RP2040.

 2. Changing the battery measurement potential divider - so avoid putting more than 3v on the I/O pin.
    Also see section below about ADC limitations before you decide which option to take.

These are described in more detail pictures in this link:

    http://zedcode.blogspot.com/2022/12/converting-ukmarsbot-to-raspberry-pi.html

There are three alternatives for battery voltage.

#### Battery Measurement Alternative 1:

Change the upper resistor of the potential divider (R7 - normally 10K) with a 22K.

#### Battery Measurement Alternative 2:

David has an alternative method which is to remove or leave out the R7 10Kohm 
resistor. This will stop the battery voltage/2 being fed to GP15 which could be above the 3.3v input pin voltage.

[Remove R7](images/Remove_R7.jpg)

#### Battery Measurement Alternative 3:

Peter suggesting soldering an additional resistor - see references below for technical details.


### Stage 2: Remove 5v

The 5v pin is fed into the UKMARSBot from the Arduino Nano fourth pin. You have two options here.

  1. Remove the pin from the Maker Nano RP2040 module itself.

  2. Remove the that specific pin socket from the UKMARSBot. 

(I've detailed removing the regulator from the Maker Nano RP2040, since 
there isn't a schematic supplied by Cytron so we can't be sure of the change).

Whatever you do it is *critical* that 5v is not fed into the underlying 
circuitry - since we will short the UKMARSBot PCB 5v pin to 3v in order to 
power the robot logic from 3v!!

If you are building the UKMARSBot from scratch, then the easiest method is to 
put an 11 pin socket and 3 pin socket instead of the normal 15 pin socket with
a gap between them, 

If you have already made the UKMARSBot then you can carefully snip that socket 
pin out with some side cutters.

[Remove 5v Pin](images/Remove_5v_Pin.jpg)


### Stage 3: Power the logic and sensors with 3.3v

To feed the 3.3v output from the Maker Nano RP2040 to the UKMARSbot power 
line - previously the 5v line. This means that, excluding the battery voltage, 
the rest of the board will run at 3.3v. This protects the RP2040 from having
more than 3.3v on the GPIO.

To do this, you need to short the 3.3v and 5v nets together. An easy way to 
do this is on the end of the pin header of the sensor connector, as shown 
in this image:

[Connect 3.3v to 5v line](images/Connect_3.3v.jpg)


### Stage 4: Plug in the Arduino Nano RP2040

Finally you can plug the Cytron Maker Nano RP2040 into the UKMARSBot 
socket where the Arduino Nano normally goes!

Make sure the device goes the right way around!

[Plug in Maker Nano RP2040](images/Plugged_in_Maker_Nano_RP2040.jpg)


### Stage 5 [OPTIONAL] - Sensor resistors

You might want to consider replacing the sensor board LED series drive 
resistors with lower value as they will be driven from 3.3v instead of 5v.

However for line following they will probably run OK with the lower 
voltage, and it might work as well for wall following. I suggest testing
before making any changes. It seems to work ok with default values.

The ADC input on the Cytron board is higher resolution than on
the original Arduino Nano so this helps to compensate.


## ADC Inputs

The standard Arduino Nano has 8 ADC (Analogue-to-digital) inputs.
The Maker Nano RP2040 only has 4 ADC inputs connected to the same place as A0 to A3 on the Nano. The equivalent ports to A4 to A7 go into digital-only inputs.

|Input| 1/2 Size Line Follower  | 3 Sensor Wall Follower | 4 Sensor Wall Follower |Maker Nano RP2040|
|-----|-------------------------|------------------------|------------------------|-----------------|
|  A0 | Radius Mark Sensor      | Left Wall Sensor       | Wall Sensor            |Analog & Digital |
|  A1 | Line Left Side Sensor   | Front Wall Sensor      | Wall Sensor            |Analog & Digital |
|  A2 | Line Right Side Sensor  | Right Wall Sensor      | Wall Sensor            |Analog & Digital |
|  A3 | Start/Finish Mark Sensor| (not used)             | Wall Sensor            |Analog & Digital |
|  A4 | (not used)              | (not used)             | (not used)             |Digital only     |
|  A5 | (not used)              | (not used)             | (not used)             |Digital only     |
|  A6 | Function Sw. / Button   | Function / Button      | Function Sw. / Button  |Digital only     |
|  A7 | Battery Voltage sense   | Battery Voltage sense  | Battery Voltage sense  |Digital only     |


### Function Sw. / Button Workarounds

It's not documented here, but you can probably modify the circuit to just have the 
button trigger the digital input connected to A6, and ignore (or remove) the function 
DIP switch. Specific circuit modifications welcome - email me, and I will update this
instruction page.

### Battery Voltage Sense Work Arounds

The more serious problem for the budding roboticist is the voltage sense - since 
this allows you to compensate for variation in the battery voltage, and also signal 
when the battery is too low to continue. 

Here are some ideas:
   - Fitting a seperate ADC chip (potentially using A4 and A5 to read this).

   - Forgo voltage compensation, and make sure you always use fresh 
     batteries - course this is problematic since you will like get different 
     results during testing - but this is the easiest option. 

   - For battery-too-low only sensing you could add a comparator to 
     compare the voltage against a known low voltage to stop the mouse and feed 
     that into A7.

   - If you are using a 3 input wall sensor, cross couple the battery sense
     to the unused A3 input (make sure you set the A7 pin to input if you 
     do not disconnect it).

   - If you are using the 1/2 size line follower board, forgo the radius mark sensor
     and use that input for the battery voltage sensor. You'd need to find the
     turn radii in software and keep some sort of map in order to do a faster run
     by memory. You'll probably need encoder odometry to make this work.


## Software Notes

The GPIO (general purpose input-output) pins are assigned differently. You 
will need to remap any inputs and outputs, or specialise peripherals in 
software in order for the software to work.


## References

These are based on the notes by David Hannaford, watch the start of the video here:
 - https://www.youtube.com/watch?v=oCECuOwtVjM

Peter Harrison discusion 3.3v running https://youtu.be/_E6mRQq4exo?t=1071

https://ukmars.org/2021/02/a-raspberry-pi-pico-based-ukmarsbot/

https://ukmars.org/2020/12/alternative-processors-for-ukmarsbot/

Some Zeptoforth reference code for the Maker Nano RP2040 is located here: 
https://github.com/robzed/Maker_Nano_RP2040_Forth_Demo
This is not Robot code!

For Micropython, David Hannaford is working on some code - but there is 
some simple non-robot example code here: 
https://github.com/robzed/UKMARSbot_RPi_Pico_Adapter

David Hannafords UKMARS page is here https://www.davidhannaford.com/ukmars/


