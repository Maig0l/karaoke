"""MultiPlayer is a class that implements two QMediaPlayers and syncs their states to be simultaneous.

TODO:
X Verify it plays multiple streams
X Verify interface compatibility
- THEN try to implement buffers
"""
import sys
import time
from typing import List

from PyQt5.QtCore import QObject, QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtWidgets import QApplication


class MultiPlayer(QMediaPlayer):
    def __init__(self, parent: QObject = None, flags: QMediaPlayer.Flags = QMediaPlayer.Flags(), nPlayers: int = 2):
        # Multiplayer is one of the players itself
        super().__init__(parent, flags)
        self.nPlayers = nPlayers

        # Create media players
        self.players = [self]
        for n in range(nPlayers - 1):
            self.players.append(QMediaPlayer())

        # Sync signals
        # Position change should be handled by a method, as position constantly changes throughout playback
        self.stateChanged.connect(self.hook_stateChanged)
        for p in self.players[1:]:
            self.mutedChanged.connect(p.setMuted)
            self.playbackRateChanged.connect(p.setPlaybackRate)

    def hook_stateChanged(self, state):
        print(f"Master state changed: {state}")
        for p in self.players[1:]:
            if state == QMediaPlayer.PlayingState:
                p.play()
            elif state == QMediaPlayer.PausedState:
                p.pause()

    # FIXME
    def addMedia(self, *args: str):
        """Currently only allows opening from files (with file: prefix)"""
        assert 0 < len(args) <= self.nPlayers
        for p, track in zip(self.players, args):
            p.setMedia(QMediaContent(QUrl(track)))

    def addMedia(self, streams: List[str]):
        for p, s in zip(self.players, streams):
            p.setMedia(QMediaContent(QUrl(s)))

    def setMediaToPlayer(self, index: int, media: str):
        self.players[index].setMedia(QMediaContent(QUrl(media)))

    # TODO: See if I can use setPosition method name instead of using prefix
    def mp_setPosition(self, position: int) -> None:
        for p in self.players:
            p.setPosition(position)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mp = MultiPlayer()
    app.exec_()
