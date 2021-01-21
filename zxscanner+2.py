#
# ZX Raspberry Keyboard Scanner v4.1
# @mrpjevans mrpjevans.com 2017
# MIT License (https://opensource.org/licenses/MIT) see LICENSE
#

import time, sys, wiringpi, uinput, os

#
# MagPi Article Mappings
#

# KEYBOARD-Y (BCOM GPIO pins)
dataLines = [19,26,16,15,18,23,24,25,8,7,1, 12]

# KEYBOARD-X (BCOM GPIO pins)
addressLines = [2,3,4,17,27,22,10,9,11,0,5,6,13]

# The ZX Spectrum Keyboard Matrix (Mapped to modern keyboard )
keys = [
	['1','2','3','4','5','A','A','A','A','A','A'],
	['Q','W','E','R','T','A','A','A','A','A','A'],
	['A','S','D','F','G','A','A','A','A','A','A'],
	['0','9','8','7','6','A','A','A','A','A','A'],
	['P','O','I','U','Y','A','A','A','A','A','A'],
	['LEFTSHIFT','Z','X','C','V','A','A','A','A','A','A'],
	['ENTER','L','K','J','H','A','A','A','A','A','A'],
	['SPACE','LEFTCTRL','M','N','B','A','A','A','A','A','A'],
        ['A','A','A','A','A','A','A','A','A','A','A'],
        ['A','A','A','A','A','A','A','A','A','A','A'],
        ['A','A','A','A','A','A','A','A','A','A','LEFT'],
        ['A','A','A','A','A','RIGHT','UP','A','A','A','DOWN'],
        ['A','A','A','A','A','A','A','A','A','A','A']
]

# Function key mode
funcKeys = [
	['F1','F2','F3','F4','LEFT','A','A','A','A','A','A'],
	['Q','W','E','R','T','A','A','A','A','A','A'],
	['A','S','D','F','G','A','A','A','A','A','A'],
	['ESC','9','RIGHT','UP','DOWN','A','A','A','A','A','A'],
	['P','O','I','U','Y','A','A','A','A','A','A'],
	['LEFTSHIFT','Z','X','C','V','A','A','A','A','A','A'],
	['ENTER','L','K','J','H','A','A','A','A','A','A'],
	['SPACE','LEFTCTRL','M','N','B','A','A','A','A','A','A'],
        ['A','A','A','A','A','A','A','A','A','A','A'],
        ['A','A','A','A','A','A','A','A','A','A','A'],
        ['A','A','A','A','A','A','A','A','A','A','A'],
        ['A','A','A','A','A','A','A','A','A','A','A'],
        ['A','A','A','A','A','A','A','A','A','A','A']
]

# Track keypresses so we can support multiple keys
keyTrack = [
	[False, False, False, False, False, False, False, False, False, False, False],
	[False, False, False, False, False, False, False, False, False, False, False],
	[False, False, False, False, False, False, False, False, False, False, False],
	[False, False, False, False, False, False, False, False, False, False, False],
	[False, False, False, False, False, False, False, False, False, False, False],
	[False, False, False, False, False, False, False, False, False, False, False],
	[False, False, False, False, False, False, False, False, False, False, False],
	[False, False, False, False, False, False, False, False, False, False, False],
	[False, False, False, False, False, False, False, False, False, False, False],
	[False, False, False, False, False, False, False, False, False, False, False],
	[False, False, False, False, False, False, False, False, False, False, False],
	[False, False, False, False, False, False, False, False, False, False, False],
	[False, False, False, False, False, False, False, False, False, False, False]
]

# Keyboard mode and reset button
buttonPressed = -1
buttonGPIO = 12
buttonTime = 0
ledGPIO = 21

# 0 = Spectrum, 1 = Function Keys
keyboardMode = 0

# Local path
myDir = os.path.dirname(os.path.realpath(__file__));

# Well this is annoying
device = uinput.Device([
        uinput.KEY_A, uinput.KEY_B, uinput.KEY_C, uinput.KEY_D, uinput.KEY_E, uinput.KEY_F, uinput.KEY_G, uinput.KEY_H,
        uinput.KEY_I, uinput.KEY_J, uinput.KEY_K, uinput.KEY_L, uinput.KEY_M, uinput.KEY_N, uinput.KEY_O, uinput.KEY_P,
        uinput.KEY_Q, uinput.KEY_R, uinput.KEY_S, uinput.KEY_T, uinput.KEY_U, uinput.KEY_V, uinput.KEY_W, uinput.KEY_X,
        uinput.KEY_Y, uinput.KEY_Z, uinput.KEY_0, uinput.KEY_1, uinput.KEY_2, uinput.KEY_3, uinput.KEY_4, uinput.KEY_5,
        uinput.KEY_6, uinput.KEY_7, uinput.KEY_8, uinput.KEY_9,
        uinput.KEY_LEFTSHIFT, uinput.KEY_ENTER, uinput.KEY_SPACE, uinput.KEY_LEFTCTRL,
        uinput.KEY_F1, uinput.KEY_F2, uinput.KEY_F3, uinput.KEY_F4, uinput.KEY_F5,
        uinput.KEY_F6, uinput.KEY_F7, uinput.KEY_F8, uinput.KEY_F9, uinput.KEY_F10,
        uinput.KEY_UP, uinput.KEY_DOWN, uinput.KEY_LEFT, uinput.KEY_RIGHT,
        uinput.KEY_ESC
        ])

# Setup GPIO
wiringpi.wiringPiSetupGpio()

# Set all address lines high
for addressLine in addressLines:
	wiringpi.pinMode(addressLine, 1)
	wiringpi.digitalWrite(addressLine, 1)

# Set all data lines for input
for dataLine in dataLines:
	wiringpi.pullUpDnControl(dataLine, 2)

wiringpi.pinMode(ledGPIO, 1)
wiringpi.digitalWrite(ledGPIO, 0)

# Setup Button
wiringpi.pullUpDnControl(buttonGPIO, 2)

# Announce
print("Running")

try:

	# Loop forever
	while True:
		
		# Button check
		if(wiringpi.digitalRead(buttonGPIO) == False):

			# Record time the button was pressed
			if(buttonPressed == -1):
				buttonPressed = int(time.time())
				print('Button pressed')

		elif(buttonPressed != -1):

			# Button released - but how long was it pressed for?
			buttonTime = int(time.time()) - buttonPressed

			# If over 3 secs, switch keyboard mode
			if(buttonTime < 3):

				# Switch modes
				if(keyboardMode == 0):
					print("Switching to Function Keys")
					keyboardMode = 1;
                                        wiringpi.digitalWrite(ledGPIO, 1)
				else:
					print("Switching to Spectrum Keys")
					keyboardMode = 0;
                                        wiringpi.digitalWrite(ledGPIO, 0)

			else:

				print('Killing FUSE')
				os.system('sudo killall fuse')

			# Reset
			buttonPressed = -1
			
		# Individually set each address line low
		for addressLine in range(13):
			
			# Set low
			wiringpi.digitalWrite(addressLines[addressLine], 0)
			
			# Scan data lines
			for dataLine in range(11):

				# Get state and details for this button
				isFree = wiringpi.digitalRead(dataLines[dataLine])
				if(keyboardMode == 0):
					keyPressed = keys[addressLine][dataLine]
				else:
					keyPressed = funcKeys[addressLine][dataLine]
				keyCode = getattr(uinput, 'KEY_' + keyPressed)

				# If pressed for the first time
				if(isFree == False and keyTrack[addressLine][dataLine] == False):

					# Press the key and make a note
					#print('Pressing ' + keyPressed)
					device.emit(keyCode, 1)
					keyTrack[addressLine][dataLine] = True

				# If not pressed now but was pressed on last check
				elif(isFree == True and keyTrack[addressLine][dataLine] == True):
					
					# Release the key and make a note
					#print('Releasing ' + keyPressed)
					device.emit(keyCode, 0)
					keyTrack[addressLine][dataLine] = False

			# Set high
			wiringpi.digitalWrite(addressLines[addressLine], 1)

			# Have a quick snooze (suggested by Keef)
			time.sleep(.01)
		

except KeyboardInterrupt:
	sys.exit(0)
