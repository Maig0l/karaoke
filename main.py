#!/usr/bin/python3
import sys
import librosa

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QSlider, QLabel, QPushButton, QDoubleSpinBox, QFileDialog, QMainWindow, QWidget, \
    QVBoxLayout, QApplication, QSpinBox
from PyQt5.QtMultimedia import QAudio, QMediaPlayer

import utils
from multiplayer import MultiPlayer
from track import Track

tracks = ["streams/bo/off-vocal.flac",
          "streams/bo/vocals.flac"]


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.tracks = []
        self.duration = 0
        self.pos = 0
        self.mediaDurationSecs = 0

        self.setup_ui()
        self.show()

    def setup_ui(self):
        self.setWindowTitle("Player")
        self.resize(350, 0)

        self.centralWid = QWidget(self)
        self.layout = QVBoxLayout(self.centralWid)
        self.setCentralWidget(self.centralWid)

        # Create widgets (Players, Status, Controls)
        self.mplayer = MultiPlayer(self.layout, QMediaPlayer.LowLatency)
        self.sldr_pos = QSlider(Qt.Horizontal)
        self.lbl_time = QLabel()
        self.sldr_vocalVol = QSlider(Qt.Horizontal)
        self.spn_pitch = QSpinBox()
        self.spn_tempo = QDoubleSpinBox()
        self.btn_open = QPushButton("Open files...")
        self.btn_play = QPushButton("Play/Pause")

        self.mplayer.addMedia(tracks)
        for idx, track in enumerate(tracks):
            self.tracks.append(Track(track))
            self.mplayer.setTrackToPlayer(idx, self.tracks[idx].buffer)

        self.sldr_pos.setRange(0, 0)
        self.sldr_vocalVol.setRange(0, 100)
        self.sldr_vocalVol.setValue(100)

        self.spn_pitch.setRange(-12, 12)
        self.spn_pitch.setSingleStep(1)
        self.spn_pitch.setValue(0)

        self.spn_tempo.setRange(0.25, 2)
        self.spn_tempo.setSingleStep(0.05)
        self.spn_tempo.setValue(1)

        self.lbl_time.setText(utils.makeTimeStamp(0, 0))
        self.lbl_time.setAlignment(Qt.AlignRight)

        # Add to layout
        self.layout.addWidget(self.btn_open)
        self.layout.addWidget(self.sldr_pos)
        self.layout.addWidget(self.lbl_time)
        self.layout.addWidget(QLabel("Vocals volume:"))
        self.layout.addWidget(self.sldr_vocalVol)
        self.layout.addWidget(QLabel("Pitch:"))
        self.layout.addWidget(self.spn_pitch)
        self.layout.addWidget(QLabel("Tempo:"))
        self.layout.addWidget(self.spn_tempo)
        self.layout.addWidget(self.btn_play)

        # Connect signals
        self.sldr_pos.sliderReleased.connect(self.seekMedia)
        self.sldr_pos.sliderPressed.connect(self.hook_deactivatePosUpdaters)

        self.mplayer.durationChanged.connect(self.hook_durationChanged)
        self.hook_activatePosUpdaters()

        self.btn_open.clicked.connect(self.prompt_openFiles)
        self.btn_play.clicked.connect(self.hook_btnPlay)

        self.sldr_vocalVol.valueChanged.connect(self.plyrVoc_setVolume)

        self.spn_pitch.valueChanged.connect(self.setPitch)
        self.spn_tempo.valueChanged.connect(self.setTempo)

    def hook_btnPlay(self):
        if self.mplayer.state() == QMediaPlayer.PlayingState:
            self.mplayer.pause()
        else:
            self.mplayer.play()

    def updateLabelPos(self, posMillis):
        posSecs = posMillis // 1000
        self.lbl_time.setText(utils.makeTimeStamp(posSecs, self.mediaDurationSecs))

    def updateSliderPos(self, posMillis):
        self.sldr_pos.setSliderPosition(posMillis)

    def hook_activatePosUpdaters(self):
        self.mplayer.positionChanged.connect(self.updateSliderPos)
        self.mplayer.positionChanged.connect(self.updateLabelPos)

    def hook_deactivatePosUpdaters(self):
        # Hook on sliderPressed
        # Deactivates sync with mplayer position to allow scrolling
        self.mplayer.positionChanged.disconnect(self.updateSliderPos)

    def hook_durationChanged(self, duration):
        self.mediaDurationSecs = duration // 1000
        self.sldr_pos.setRange(0, duration)

    def seekMedia(self):
        value = self.sldr_pos.value()
        self.mplayer.mp_setPosition(value)
        # Re-activates slider sync with media mplayer
        self.hook_activatePosUpdaters()

    def plyrVoc_setVolume(self, vol):
        # Divide vol by 100 to get a value in range 0..1
        # The second player in mplayer must be the vocal track
        logVol = QAudio.convertVolume(vol / 100,
                                      QAudio.LogarithmicVolumeScale,
                                      QAudio.LinearVolumeScale)
        self.mplayer.players[1].setVolume(logVol * 100)

    @utils.timer
    def setTempo(self, spin_value):
        """Hook from spin box for pitch control"""
        resumePos = self.mplayer.position() / self.mplayer.duration()
        prevState = self.mplayer.state()
        self.mplayer.stop()
        for idx, t in enumerate(self.tracks):
            t.setStretch(spin_value)
            self.mplayer.setTrackToPlayer(idx, self.tracks[idx].buffer)
        self.mplayer.mp_setPosition(self.mplayer.duration() * resumePos)
        if prevState == QMediaPlayer.PlayingState:
            self.mplayer.play()

    @utils.timer
    def setPitch(self, spin_value):
        """Hook from spin box for pitch control"""
        resumePos = self.mplayer.position()
        prevState = self.mplayer.state()
        self.mplayer.stop()
        for idx, t in enumerate(self.tracks):
            t.setPitch(spin_value)
            self.mplayer.setTrackToPlayer(idx, self.tracks[idx].buffer)
        self.mplayer.mp_setPosition(resumePos)
        if prevState == QMediaPlayer.PlayingState:
            self.mplayer.play()

    def setPlaybackRate(self, rate):
        resumePos = self.mplayer.position()
        prevState = self.mplayer.state()
        self.mplayer.stop()
        self.mplayer.setPlaybackRate(rate)
        self.mplayer.mp_setPosition(resumePos)
        if prevState == QMediaPlayer.PlayingState:
            self.mplayer.play()

    def prompt_openFiles(self):
        self.mplayer.stop()

        fileBg, loadOk = QFileDialog.getOpenFileName(self, "Pick Instrumental track",
                                                     filter="Audio Files (*.wav *.flac *.mp3 *.opus *.m4a)")
        if not loadOk:
            return False

        fileVoc, loadOk = QFileDialog.getOpenFileName(self, "Pick Vocal track",
                                                      filter="Audio Files (*.wav *.flac *.mp3 *.opus *.m4a)")
        if not loadOk:
            return False

        self.tracks = [Track(path) for path in (fileBg, fileVoc)]
        self.mplayer.addMedia([track.buffer for track in self.tracks])


app = QApplication(sys.argv)
window = MainWindow()
app.exec_()
