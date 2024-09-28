import cv2 as cv
import rtmidi_python as rt
import time

cap = cv.VideoCapture(0)  # Access the webcam
midi_out = rt.MidiOut(b'out')  # Create MIDI output stream
midi_out.open_port(1) # Access virtual MIDI port (must be turned on with loopMIDI)
prevnote = 0;  

while True:
    
    # STEP 1: FIND THE LIGHT
    
    ret, frame = cap.read()  # Read a frame from the webcam
    if not ret: # Error reading frame
        break
    
    # Smooth out image, in case there's randomly bright pixels (i.e., reflections)
    blurred = cv.GaussianBlur(frame, (65, 65), 0) 
    
    gray_frame = cv.cvtColor(blurred, cv.COLOR_BGR2GRAY)
    
    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(gray_frame)

    # Return the coordinates of the brightest region and the maximum brightness value
    brightest_x, brightest_y = max_loc
    
    # Display the frame (display is not mirrored, which can be confusing at first)
    cv.imshow('Webcam', blurred)


    # STEP 2: GENERATE AND SEND MIDI MESSAGE

    # Map brightest_x to pitch and brightest_y to loudness
    loudness = (int) (127-(brightest_y / 480 * 127))
    note = (int) ((127-(brightest_x / 640 * 127))/6 + 60) # Ranges from 60 to 83 inclusive (2 octaves)

    # FL Studio (and my laptop) can only handle MIDI messages at some rate.
    # Waiting 0.1s slows this rate down to about 10 messages per second.
    time.sleep(0.1)
    
    if (max_val > 220): # If light is on, set volume
        midi_out.send_message([0xB0,1,loudness]) # Control change - channel volume
        
    if ((prevnote != note or max_val <= 220) and prevnote != 0): # If new note played or light is off, turn off previous note
        midi_out.send_message([0x80, prevnote, 0]) # Note off
        prevnote = 0    
    if (max_val > 220 and prevnote != note): # If light is on and new note played, turn on new note
        midi_out.send_message([0x90, note, 127]) # Note on (vel is max, loudness is already set)
        prevnote = note
    
    if cv.waitKey(1) & 0xFF == ord('q'): # q key quits the program
         break

# Clean up
cap.release() # Close webcam
cv.destroyAllWindows() # Close webcam's display window
del midi_out # Close MIDI output
