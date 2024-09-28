# Flashlight MIDI Instrument

A script that finds the brightest pixel on the webcam's input, then generates a corresponding MIDI note to be sent to a DAW to make sound.
This project was done for the McGill MAT minor course "Fundamentals of New Media".

Below are selected parts from the report submitted with the project.

## Introduction
Theremins work by measuring the capacitance between two antennas and a musician’s hands. The distance between an antenna and a hand determines the pitch or loudness (depending on which antenna/hand) of the generated sound. Recreating a simple one would make for an interesting but time-consuming and potentially expensive project, requiring sensors and other hardware I do not have.

Instead, a MIDI controller was programmed in Python using my laptop’s webcam and a flashlight as input. The location of the light on the image frame determines the pitch and loudness by mapping the light’s x and y coordinates to note-number and volume respectively. A MIDI message is thereby generated and sent to a synthesizer in a digital audio workstation through a virtual MIDI port. If the light is off, a threshold brightness is not met and no note-on MIDI message is generated.

## Methodology
Prior to running the program, create a virtual port (with loopMIDI) and open an instrument (I used the 3x Osc plugin with the default setting, which is three sine waves each an octave apart) to be controlled in FL Studio.

### Overview of the program:
1. Get the current frame.
2. Apply a Gaussian blur to the image to smooth out unintended bright pixels.
3. Convert the image to black and white.
4. Find the brightest pixel’s magnitude (0-255) and coordinates (640x480 resolution).
5. Map the x-coordinate to note-number (in range 60-84) and y-coordinate to channel
volume.
6. Send a note-off message for the previous note if the flashlight is turned off (maximum
brightness is below a threshold) or moved left or right.
7. Send a note-on message if the flashlight is on (maximum brightness is above a threshold)
and the note has changed. Then, keep track of the new note (for steps 6 and 7).
8. Repeat all steps until the user quits.

## Things to Note About the Project
● There are 24 possible note number mappings, each a semitone apart, ranging from 60
(middle C) to 83.

● There are 27 (128) possible channel volume mappings

● The instrument is monophonic.

● It is also possible to restrict the note mappings to a certain scale (like a harmonica). This
would make it easier to play some melodies but also restrict the possible melodies.

● The frame is displayed to help the musician keep the flashlight within the frame.

## Discussion
### Improvements Made
There were two major changes made throughout the development of this program. 
The first was the addition of the Gaussian blur, which was added to fix a problem caused by unpredictable bright reflections in the frame. 
The second was mapping the y-coordinate to channel volume instead of note velocity.

If a reflection and the flashlight both have at least one pixel with the maximum value (255), then the program might choose the location of the reflection instead of the flashlight when generating the note-on message. 
This bug caused unintended notes to be played. The fix was to apply a Gaussian blur to the image, which is the convolution of a Gaussian function applied to the image. 
Put simply, a pixel’s updated (post-blur) pixel brightness is based on the average brightness of the pixels around it, which results in a blurring effect. The flashlight is a relatively large bright circle on the screen, so pixels in the center of it retain their brightness after the blur. 
A reflection is a relatively small blemish on the screen, so its pixels decrease in brightness after the blur due to nearby pixels being darker. After this correction, the brightest pixel is much more likely to correspond to the flashlight’s location, as intended.

Originally, the program generated a note-on message about every 0.1s (that is, the time the program takes to execute the loop plus an intentional wait-time of 0.1s). This limited the possible melodies by forcing each note to be the same duration. 
Even if the flashlight was held in the same location for a moment, the corresponding note would be repeated every 0.1s. So, the program was changed to only generate a note-on message if there was a new note played. Consequently, the only way to play the same note in a row is to turn off and on the flashlight, which must take up 2 loops (one to turn off the note and one to turn it back on) or about 0.2s. 
With this feature, if a note was held, moving the flashlight up and down would not change the velocity until a new note was triggered. For a piano or guitar this is realistic, but for a synth generating 3 sine waves (the instrument of choice) this is a setback. 
With this in mind, the code was changed to map the y-coordinate to channel volume (via a control change message) and have every note be played with maximum velocity.

### Instrument Limitations
● The instrument requires a dim room to function. If there are any lights in the background or if the room is bright enough, unintended pixels can be mistakenly chosen as the brightest (e.g., the classroom light’s reflection on the whiteboard when the lights were on during my presentation)

● The flashlight takes up more than one pixel. Consequently, the choice of the brightest pixel is ambiguous (i.e., anywhere within the area taken up by the light might be chosen).

  ○ This issue was masked by having wider subdivisions of the frame, sacrificing a wider range of notes.
 
  ○ When the flashlight is pointed directly at the camera, the area taken up by the flashlight is large and so one of a few possible notes are chosen. This can be avoided by pointing the flashlight at an angle, not directly at the camera.

● As a consequence of mapping the horizontal position of the light to note number, the possible notes are restricted to the notes of a piano. That is, all adjacent notes are a semitone apart, so vibrato/bending is not possible.

  ○ Implementing vibrato might involve first mapping to a note as before, then mapping to a pitch bend. The frame would still be divided into 24 semitones, but each semitone would be subdivided into 27 (or less) values of pitch bend.

● Recording MIDI input in FL Studio with the loopMIDI virtual port malfunctions. This is a glitch that I can’t figure out how to fix. So, the instrument must be used live.

● When intending to play two non-adjacent notes back to back, it is very difficult to avoid playing notes in between them. The solutions are either to move the flashlight fast enough for the notes in between to not be registered, or to turn off the flashlight, move it to the desired location, then turn it back on.

In addition to these limitations, there are also some inefficiencies in the code:
- The message rate is about 10 per second to allow FL Studio to keep up with the speed of
MIDI messages (some messages are missed when the rate is faster)
- The openCV minMaxLoc returns the minimum and maximum pixel’s location and value.
The minimum location and value are unused.

## Sources accessed
1. https://pypi.org/project/opencv-python/
2. https://docs.opencv.org/3.4/d6/d00/tutorial_py_root.html
3. https://pypi.org/project/rtmidi-python/
4. https://www.midi.org/specifications-old/item/table-1-summary-of-midi-message
5. https://www.w3.org/Talks/2012/0125-HTML-Tehran/Gaussian.xhtml#:~:text=The%20Ga
ussian%20blur%20is%20a,each%20pixel%20in%20the%20image.
6. https://ioflood.com/blog/python-wait/#:~:text=To%20pause%20or%20delay%20executio
n,a%20specified%20number%20of%20seconds.
