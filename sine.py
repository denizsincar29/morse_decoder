# a threaded sine wave player. Accepts booleans to it's queue to start and stop the sine wave. Uses sounddevice to play the sine wave.

import numpy as np
import sounddevice as sd

# returns a frame of a sine wave by index, or x position. e.g. x is an integer index of a frame, so x/sr is the time in seconds
def sine_wave_frame(x, freq, sr, volume):
    return (volume*np.sin(2*np.pi*freq*x/sr)).astype(np.float32)
class SineWavePlayer():
    def __init__(self):
        self.stream=sd.OutputStream(channels=1, callback=self.sd_callback, dtype=np.float32)
        self.freq=440*2**(10/12)
        self.sr=44100
        self.volume=0.5
        # write frame by frame, so we need to keep track of the phase
        self.sine_phase=0
        self.running=False
        self.stream.start()

    def sd_callback(self, outdata, frames, time, status):
        if self.running:
            for i in range(frames):
                outdata[i]=sine_wave_frame(self.sine_phase, self.freq, self.sr, self.volume)
                self.sine_phase+=1
        else:
            outdata[:]=0

    def play(self):
        self.running=True

    def stop(self):
        self.running=False

    def close(self):
        self.stream.stop()
        self.stream.close()

    def __del__(self):  # automatically close the stream when the object is deleted
        self.close()

if __name__=="__main__":
    from time import sleep
    player=SineWavePlayer()
    for i in range (5):
        player.play()
        sleep(1)
        player.stop()
        sleep(1)
