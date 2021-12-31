import io
import pathlib
from functools import lru_cache
from utils import timer

import soundfile
import pyrubberband as pyrb
from PyQt5.QtCore import QBuffer, QIODevice
from typing import Optional, Union
from numpy import ndarray


class Track:
    def __init__(self, path: str):
        self.path = pathlib.Path(path)
        self.fullpath = self.path.absolute()
        self.data, self.rate = soundfile.read(path)
        # Apply all effects into a copy of data (what is done here),
        # or calculate deltas of effect amount before processing
        self.dataProcessed = self.data
        self.buffer = QBuffer()
        self.updateBuffer()

        self.amnt_pitchShift = 0
        self.amnt_stretch = 0
        self.effectsCache = {}
        #self.pitch_shift = lru_cache(pyrb.pitch_shift)

    def updateBuffer(self, data: Optional[ndarray] = None):
        if data is None:
            data = self.data

        # TODO: Could use a BytesIO interface from QT?
        waveBuf = io.BytesIO()
        soundfile.write(waveBuf, data, self.rate, format='WAV')

        self.buffer.close()
        self.buffer.setData(waveBuf.getvalue())
        self.buffer.open(QIODevice.ReadOnly)
        self.buffer.seek(0)

    def setStretch(self, amount: float):
        # TODO: Send QT signal: progress
        targetKey = self.getEffectKey(ps=amount)
        if targetKey in self.effectsCache:
            self.dataProcessed = self.effectsCache[targetKey]
        else:
            self.dataProcessed = pyrb.time_stretch(self.data, self.rate, amount)
        self.updateBuffer(self.dataProcessed)

        self.amnt_pitchShift = amount
        self.storeInCache(self.dataProcessed)

    def setPitch(self, amount: int):
        # TODO: Send QT signal: progress
        targetKey = self.getEffectKey(ps=amount)
        if targetKey in self.effectsCache:
            self.dataProcessed = self.effectsCache[targetKey]
        else:
            self.dataProcessed = pyrb.pitch_shift(self.data, self.rate, amount)
        self.updateBuffer(self.dataProcessed)

        self.amnt_pitchShift = amount
        self.storeInCache(self.dataProcessed)

    def setTimestretch(self, *args):
        raise NotImplemented

    def storeInCache(self, data):
        self.effectsCache[self.getEffectKey()] = data

    def getEffectKey(self, ps: Optional[int] = None, ts: Optional[int] = None):
        if ps is None:
            ps = self.amnt_pitchShift
        if ts is None:
            ts = self.amnt_stretch
        return f"{ps:02}_{ts:02}"


if __name__ == '__main__':
    t = Track("./streams/bo/vocals.flac")
    print(t.path)
    print(t.fullpath)
    t.setPitch(-2)
