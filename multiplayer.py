"""MultiPlayer is a class that implements two QMediaPlayers and syncs their states to be simultaneous.

TODO:
X Verify it plays multiple streams
- Verify interface compaitbility
- THEN try to implement buffers
"""
import sys
import time

from PyQt5.QtCore import QObject, QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtWidgets import QApplication


class MultiPlayer(QMediaPlayer):
    def __init__(self, parent: QObject = None, flags: QMediaPlayer.Flags = None, nPlayers: int = 2):
        # I think it's not necessary, unless Multiplayer acts as the first player(?
        #super().__init__(parent, flags)
        self.nPlayers = nPlayers

        # Create media players
        self.players = []
        for n in range(nPlayers):
            self.players.append(QMediaPlayer())
        self.master: QMediaPlayer = self.players[0]

        # Sync signals
        # Position change should be handled by a method, as position constantly changes throughout playback
        # State change signal doesn't appear to work, so play() and stop() methods set media to play
        #  on all players individually.
        for p in self.players[1:]:
            self.master.mutedChanged.connect(p.setMuted)
            self.master.playbackRateChanged.connect(p.setPlaybackRate)

    def hook_stateChanged(self, state):
        print(f"Master state changed: {state}")
        for p in self.players[1:]:
            if state == 1:
                p.play()
            else:
                p.pause()

    def addMedia(self, *args):
        """Currently only allows opening from files (with file: prefix)"""
        assert 0 < len(args) <= self.nPlayers
        for p, track in zip(self.players, args):
            p.setMedia(QMediaContent(QUrl(track)))

    def setMediaToPlayer(self, index: int, media: str):
        self.players[index].setMedia(QMediaContent(QUrl(media)))

    def play(self):
        for p in self.players:
            p.play()

    def stop(self):
        for p in self.players:
            p.stop()

    def setPosition(self, position: int) -> None:
        for p in self.players:
            p.setPosition(position)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mp = MultiPlayer()
    mp.addMedia("file:/home/miguel/dox/projects/python/karaoke/streams/bo/off-vocal.flac",
                "file:/home/miguel/dox/projects/python/karaoke/streams/bo/vocals.flac")
    mp.play()
    app.exec_()
