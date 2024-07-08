#!/usr/bin/env python3
import mido
import pyvisa
#import os, time
"""
issues:
switching wave form, voltage, or output, will make the relays click. 
setting the frequency to 0 will make the Function generator beep.
Its a setting, but my cpu battery is dead, and I dont know how to configure that
via pyvisa or USBTMC
 This isn't automatic midi initalization, I dumped the list, and pasted in the 
 right midi_port after running once. tried to use the aseqdump listed midi port,
 but mido doesnt like it. 
 
 Other todo:
 Figure out how to do user defined wave forms, and figure something out for attack, decay.
 
 Oh, and you can hit multiple keys, but the first relase is going to set the output to effectively 0
"""


# Initialize the VISA resource manager
rm = pyvisa.ResourceManager()
instruments = rm.list_resources()
if instruments:
    func_gen_resource = instruments[0]  # Get the first instrument
    print(f"Connected instrument: {func_gen_resource}")
else:
    print("No instruments found")
    exit(1)

# Open a connection to the function generator
func_gen = rm.open_resource(func_gen_resource)

amp = 10.0
# Set up the function generator
func_gen.write('*RST')  # Reset the function generator to default settings
func_gen.write('FUNC SQU')  # Set waveform: options: SIN, RAMP, SQU,PUL, SAW ( SAW sets to SIN ) 
func_gen.write(f"VOLT {amp}")
func_gen.write('OUTP:LOAD INF')  # Set output load to infinite
func_gen.write('OUTP ON')  

# Function to convert MIDI note number to frequency
def midi_to_frequency(note):
    # A4 (MIDI note 69) is 440 Hz
    return 440.0 * 2**((note - 69) / 12.0)

# List available MIDI input ports
print("Available MIDI input ports:")
for port in mido.get_input_names():
    print(port)

# Open the specified MIDI input port
midi_port = 'Launchkey MK3 61:Launchkey MK3 61 LKMK3 MIDI In 20:0'  # Replace with the actual port name
midi_in = mido.open_input(midi_port)
print("Listening for MIDI input...")
# setting frq to 0 makes a beep, but 0.0001 is fine regardless of waveform
func_gen.write(f'FREQ {0.0001}') 

try:
    for msg in midi_in:
        if msg.type == 'note_on' and msg.velocity > 0:
            note = msg.note
            frequency = midi_to_frequency(note)
            print(f"Note: {note}, Frequency: {frequency:.2f} Hz")
            func_gen.write(f'FREQ {frequency:.2f}')
        
        elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
            print(f"Note off: {msg.note}")
            func_gen.write(f'FREQ {0.0001}') 

except KeyboardInterrupt:
	# ctrl+c
    print("Exiting...")

finally:
    # Close the MIDI input and function generator connection
    midi_in.close()
    func_gen.write('OUTP OFF')
    func_gen.write('SYSTEM:LOCAL') # Return to manual control
    func_gen.close()
