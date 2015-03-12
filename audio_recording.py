# Imports
from array import array
from struct import pack
from sys import byteorder
import copy
import pyaudio
import wave
import time


class Main():
  def __init__(self):
    self.THRESHOLD = 500  # normalization threshhold
    self.CHUNK_SIZE = 1024
    self.FORMAT = pyaudio.paInt16
    self.FRAME_MAX_VALUE = 2 ** 15 - 1
    self.NORMALIZE_MINUS_ONE_dB = 10 ** (-1.0 / 20)
    self.RATE = 44100
    self.CHANNELS = 1
    self.TRIM_APPEND = self.RATE / 4

    self.record_to_file("recording.wav")

  # Normalizes audio volume
  def normalize(self, data_all):
    # MAXIMUM = 16384
    normalize_factor = (float(self.NORMALIZE_MINUS_ONE_dB * self.FRAME_MAX_VALUE)
                        / max(abs(i) for i in data_all))

    r = array('h')
    for i in data_all:
      r.append(int(i * normalize_factor))
    return r

  # Used to trim the audio before normalizing it
  def trim(self, data_all):
    _from = 0
    _to = len(data_all) - 1
    for i, b in enumerate(data_all):
      if abs(b) > self.THRESHOLD:
        _from = max(0, i - self.TRIM_APPEND)
        break

    for i, b in enumerate(reversed(data_all)):
      if abs(b) > self.THRESHOLD:
        _to = min(len(data_all) - 1, len(data_all) - 1 - i + self.TRIM_APPEND)
        break

    return copy.deepcopy(data_all[_from:(_to + 1)])

  def record(self):
    p = pyaudio.PyAudio()
    stream = p.open(format=self.FORMAT, channels=self.CHANNELS, rate=self.RATE, input=True, output=True, frames_per_buffer=self.CHUNK_SIZE)
    data_all = array('h')
    starttime = time.time()
    while True:
      data_chunk = array('h', stream.read(self.CHUNK_SIZE))
      if byteorder == 'big':
        data_chunk.byteswap()
      data_all.extend(data_chunk)
      if time.time() > starttime+5:
        break


    sample_width = p.get_sample_size(self.FORMAT)
    stream.stop_stream()
    stream.close()
    p.terminate()

    # Uncomment these lines to trim/normalize recording
    #data_all = self.trim(data_all)  # we trim before normalize as threshhold applies to un-normalized wave (as well as is_silent() function)
    #data_all = self.normalize(data_all)
    return sample_width, data_all

  # Uses the Record method to write a recording to a file
  def record_to_file(self, path):
    sample_width, data = self.record()
    data = pack('<' + ('h' * len(data)), *data)

    wave_file = wave.open(path, 'wb')
    wave_file.setnchannels(self.CHANNELS)
    wave_file.setsampwidth(sample_width)
    wave_file.setframerate(self.RATE)
    wave_file.writeframes(data)
    wave_file.close()

if __name__ == "__main__":
  Main()
