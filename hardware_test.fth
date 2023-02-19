\ ukmars with Pico hardware test file
\ Use with Zeptoforth https://github.com/tabemann/zeptoforth
\ Tested with zeptoforth-0.54.0.tar.gz

adc import
led import 
pin import 


: double_beep
  high 13 pin!
  200 ms
  low 13 pin!
  200 ms 
  high 13 pin!
  200 ms
  low 13 pin!
;

7 constant LMOTOR_DIR
9 constant LMOTOR_PWM
0 constant LMOTOR_forward

8 constant RMOTOR_DIR
10 constant RMOTOR_PWM
1 constant RMOTOR_forward

\ dir = -1=reverse, 0=off, 1=forward
: rmotor ( dir -- )
  dup 0= IF
    0 RMOTOR_PWM pin!
  THEN
  dup 0> IF
    RMOTOR_forward RMOTOR_DIR pin!
    1 RMOTOR_PWM pin!
  THEN
  0< IF
    1 RMOTOR_forward - RMOTOR_DIR pin!
    1 RMOTOR_PWM pin!
  THEN 
;

: lmotor ( dir -- )
  dup 0= IF
    0 LMOTOR_PWM pin!
  THEN
  dup 0> IF
    LMOTOR_forward LMOTOR_DIR pin!
    1 LMOTOR_PWM pin!
  THEN
  0< IF
    1 LMOTOR_forward - LMOTOR_DIR pin!
    1 LMOTOR_PWM pin!
  THEN
;


\ default all the IO necessary
: io_default
  green toggle-led
  13 output-pin   \ Buzzer/external LED pin
  double_beep

  \ MUX pins
  20 output-pin
  21 output-pin
  22 output-pin

  \ on board sensor LEDs
  6 output-pin
  11 output-pin

  \ motor
  LMOTOR_DIR output-pin
  LMOTOR_PWM output-pin
  RMOTOR_DIR output-pin
  RMOTOR_PWM output-pin
;

: rightLED! ( state -- ) 6 pin! ;

: leftLED! ( state -- ) 11 pin! ;


\ example from Zeptoforth docs
: test_temp ( -- ) 10 0 do temp-adc-chan default-adc adc@ . 1000 ms loop ;

: adc0_read ( -- value ) 0 default-adc adc@ ;
: adc2_read ( -- value ) 2 default-adc adc@ ;

: inrange ( low value high -- flag )
  over ( low value high value )
  >=  ( low value flag{high>=value} )
  swap ( low flag value )
  rot ( fl  ag value low )
  >= and
; 
: >> rshift ;
: << lshift ;

: mux! ( channel -- )
  0 over 7 inrange if
    dup          1 and 20 pin!
    dup 1 >> 1 and 21 pin!
        2 >> 1 and 22 pin!
  else
    ." MUX channel out of range" cr abort
  then
;

\ supports negative channels for MUX channels
: adc_read ( channel -- value )
  dup 0< if
    negate mux! 
    1 ms 
    2 \ the 74HC4051 multiplexer is attached to this Pico ADC channel
  then
  default-adc adc@
;

: adc>mV ( adc_reading -- millivolts )
  3300 4095 */
;

\ these assume 0-1023 range
create adc_thresholds 
660 , 647 , 630 , 614 , 590 , 570 , 545 , 522 , 461 , 429 , 385 , 343 , 271 , 212 , 128 , 44 , 0 ,

: get_ADC_threshold ( i -- value )
  cells adc_thresholds + @
;

\ Q: could be more effcient if we did CELL+ on internal address?
\ A: probably minimal, effectively it would avoid a 4<< and a constant fetch
: intermediate_ADC_threshold ( i -- value )
  dup get_adc_threshold swap 1+ get_adc_threshold + 2/
;

4095 constant MAX_ADC

: function_decode ( switches_adc -- decode )
    \ use code from ukmarsbot project
    1023 MAX_ADC */
    dup 800 > if
        drop 16
    else
        16 0 do
          dup I intermediate_ADC_threshold > if
            drop I unloop exit
          then
        loop
        drop -1 
    then
;

: show_switches ( -- )
  -6 adc_read 
  dup ." Function = " . dup hex . decimal
  function_decode 
  dup
  case
  16 of drop ." Button" endof 
  -1 of drop ." Invalid" endof
  binary . decimal
  endcase
  cr
;

: switches_10s ( -- )
  20 0 do 
    show_switches 500 ms
  loop
;

variable Vsum
variable Vcount
variable ADCmin
variable ADCmax
variable ADClast

: Vaverage ( -- Voltage )
  Vsum @ Vcount @ /
;
: Vmin ( -- mV ) ADCmin @ adc>mV ;
: Vmax ( -- mV ) ADCmax @ adc>mV ;

: .adc_summary ( -- )
  ." Count = " Vcount @ . 
  ." Battery Voltage mV = " Vmin . Vaverage . Vmax .
  ." ADC = " ADCmin @ . ADCmax @ .
  ." ADC hex (min,last,max) = "
  hex ADCmin @ . ADClast @ . ADCmax @ . decimal
  cr
  ." Variation "
  Vmin Vaverage - 100 Vaverage */ . ." % "
  Vmax Vaverage - 100 Vaverage */ . ." % "
;


: adc_stats ( channel -- )
  0 Vsum !
  0 Vcount !
  0 ADCmax !
  65535 ADCmin !

  500 0 do
    1 Vcount +!
    dup adc_read 
    dup ADCmin @ < if
      dup ADCmin !
    then
    dup ADCmax @ > if
      dup ADCmax !
    then
    dup ADClast !
    adc>mV
    dup Vsum +!
    . ." mV "
  loop
  drop
  cr .adc_summary
;

: bat_stats ( -- ) 
  -7 adc_stats
;


io_default

