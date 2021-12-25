## A QSlider, showing song position, and moving controls
## And a QLabel showing timeElapsed/timeTotal

import sys

from PyQt5.QtWidgets import QSlider, QLabel, QPushButton, QDoubleSpinBox, QFileDialog

import utils
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtMultimedia import QAudio, QMediaPlayer, QMediaContent

streams = ["file:/home/miguel/dox/projects/python/karaoke/streams/bo/off-vocal.flac",
           "file:/home/miguel/dox/projects/python/karaoke/streams/bo/vocals.flac"]


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.duration = 0
        self.pos = 0
        self.mediaDurationSecs = 0

        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Player")
        self.resize(350, 0)

        self.centralWid = QtWidgets.QWidget(self)
        self.layout = QtWidgets.QVBoxLayout(self.centralWid)
        self.setCentralWidget(self.centralWid)

        # Create widgets (Players, Status, Controls)
        # TODO: Make a "Meta-Player" Class that unifies both players
        self.plyr_bg = QMediaPlayer(self.layout, QMediaPlayer.LowLatency)
        self.plyr_voc = QMediaPlayer(self.layout, QMediaPlayer.LowLatency)
        self.sldr_pos = QSlider(Qt.Horizontal)
        self.lbl_time = QLabel()
        self.sldr_vocalVol = QSlider(Qt.Horizontal)
        self.spn_speed = QDoubleSpinBox()
        self.btn_open = QPushButton("Open files...")
        self.btn_play = QPushButton("Play/Pause")

        self.sldr_pos.setRange(0, 0)
        self.sldr_vocalVol.setRange(0, 100)
        self.sldr_vocalVol.setValue(100)

        self.lbl_time.setText(utils.makeTimeStamp(0, 0))
        self.lbl_time.setAlignment(Qt.AlignRight)

        self.spn_speed.setRange(0.25, 2)
        self.spn_speed.setSingleStep(0.05)
        self.spn_speed.setValue(1)

        for p, stream in zip((self.plyr_bg, self.plyr_voc), streams):
            p.setMedia(QMediaContent(QUrl(stream)))

        # Sync players
        self.plyr_bg.stateChanged.connect(self.plyrVoc_syncState)
        self.plyr_bg.positionChanged.connect(self.plyr_voc.setPosition)
        self.plyr_bg.playbackRateChanged.connect(self.plyr_voc.setPlaybackRate)

        # Add to layout
        self.layout.addWidget(self.btn_open)
        self.layout.addWidget(self.sldr_pos)
        self.layout.addWidget(self.lbl_time)
        self.layout.addWidget(self.sldr_vocalVol)
        self.layout.addWidget(self.spn_speed)
        self.layout.addWidget(self.btn_play)

        # Connect actions
        self.sldr_pos.sliderReleased.connect(self.seekMedia)
        self.sldr_pos.sliderPressed.connect(self.hook_deactivatePosUpdaters)

        self.plyr_bg.durationChanged.connect(self.hook_durationChanged)
        self.hook_activatePosUpdaters()

        self.btn_open.clicked.connect(self.prompt_openFiles)
        self.btn_play.clicked.connect(self.play_snd)

        self.sldr_vocalVol.valueChanged.connect(self.plyrVoc_setVolume)

        self.spn_speed.valueChanged.connect(self.setPlaybackRate)

    def play_snd(self):
        if self.plyr_bg.state() == QMediaPlayer.PlayingState:
            self.plyr_bg.pause()
        else:
            self.plyr_bg.play()

    def updateLabelPos(self, posMillis):
        posSecs = posMillis // 1000
        self.lbl_time.setText(utils.makeTimeStamp(posSecs, self.mediaDurationSecs))

    def updateSliderPos(self, posMillis):
        self.sldr_pos.setSliderPosition(posMillis)

    def hook_activatePosUpdaters(self):
        self.plyr_bg.positionChanged.connect(self.updateSliderPos)
        self.plyr_bg.positionChanged.connect(self.updateLabelPos)

    def hook_deactivatePosUpdaters(self):
        # Hook on sliderPressed
        # Deactivates sync with plyr_bg position to allow scrolling
        self.plyr_bg.positionChanged.disconnect(self.updateSliderPos)

    def hook_durationChanged(self, duration):
        self.mediaDurationSecs = duration // 1000
        self.sldr_pos.setRange(0, duration)

    def seekMedia(self):
        value = self.sldr_pos.value()
        self.plyr_bg.setPosition(value)
        # Re-activates slider sync with media plyr_bg
        self.hook_activatePosUpdaters()

    def plyrVoc_syncState(self, state):
        if state == 1:
            self.plyr_voc.play()
        else:
            self.plyr_voc.pause()

    def plyrVoc_setVolume(self, vol):
        # Divide vol by 100 to get a value in range 0..1
        logVol = QAudio.convertVolume(vol/100,
                                      QAudio.LogarithmicVolumeScale,
                                      QAudio.LinearVolumeScale)
        self.plyr_voc.setVolume(logVol*100)
        print(self.plyr_voc.volume())

    def setPlaybackRate(self, rate):
        resumePos = self.plyr_bg.position()
        self.plyr_bg.stop()
        self.plyr_bg.setPlaybackRate(rate)
        self.plyr_bg.setPosition(resumePos)
        self.plyr_bg.play()

    def prompt_openFiles(self):
        self.plyr_bg.stop()

        fileBg = QFileDialog.getOpenFileName(self, "Pick Instrumental track",
                                             filter="Audio Files (*.wav *.flac *.mp3 *.opus *.m4a)")
        if not fileBg[0]:
            return False

        fileVoc = QFileDialog.getOpenFileName(self, "Pick Vocal track",
                                              filter="Audio Files (*.wav *.flac *.mp3 *.opus *.m4a)")
        if not fileVoc[0]:
            return False

        print(fileBg, fileVoc)
        for p, track in zip((self.plyr_bg, self.plyr_voc), (fileBg, fileVoc)):
            p.setMedia(QMediaContent(QUrl(f"file:{track[0]}")))


app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()
