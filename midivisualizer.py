import sys
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QFileDialog, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor, QFont, QIcon
from mido import MidiFile
from threading import Thread
import mido

# List available output ports
print(mido.get_output_names())

class PianoKeyboard(QWidget):
    def __init__(self):
        super().__init__()
        self.keys = []
        self.sustain_pedal = False

    def paintEvent(self, event):
        painter = QPainter(self)
        for key in self.keys:
            if key['pressed'] or (key['sustained'] and self.sustain_pedal):
                painter.setBrush(QColor(255, 0, 0))
            else:
                painter.setBrush(QColor(255, 255, 255) if key['white'] else QColor(0, 0, 0))
            painter.drawRect(*key['rect'])

        # Draw note labels below the piano keys
        painter.setPen(QColor(255, 255, 255))  # Set text color to white
        font = painter.font()
        font.setPointSize(8)
        painter.setFont(font)
        for key in self.keys:
            label_rect = (key['rect'][0], key['rect'][3], key['rect'][2], 15)
            painter.drawText(*label_rect, Qt.AlignmentFlag.AlignCenter, key['label'])

    def press_key(self, note):
        self.keys[note]['pressed'] = True
        self.update()

    def release_key(self, note):
        self.keys[note]['pressed'] = False
        if not self.sustain_pedal:
            self.update()

    def sustain_on(self):
        self.sustain_pedal = True
        self.update()

    def sustain_off(self):
        self.sustain_pedal = False
        self.update()

    def reset_keys(self):
        for key in self.keys:
            key['pressed'] = False
        self.update()

class MidiPlayer(QWidget):
    def __init__(self):
        super().__init__()
        self.midi_file = None
        self.output = mido.open_output('Microsoft GS Wavetable Synth 0')
        self.playing = False
        self.init_ui()

    def init_ui(self):
        self.piano = PianoKeyboard()
        self.load_button = QPushButton('Load MIDI File', self)
        self.load_button.clicked.connect(self.load_midi)
        self.play_button = QPushButton('Play', self)
        self.play_button.clicked.connect(self.play_midi)
        self.stop_button = QPushButton('Stop', self)
        self.stop_button.clicked.connect(self.stop_midi)

        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.piano)
        self.vbox.addWidget(self.load_button)
        self.vbox.addWidget(self.play_button)
        self.vbox.addWidget(self.stop_button)
        self.setLayout(self.vbox)

        key_width = 10
        key_height = 100

        for i in range(128):
            white = (i % 12) not in [1, 4, 6, 9, 11]
            x = i * key_width
            note_label = str(i % 12)  # Use the note number as the label
            self.piano.keys.append({'rect': (x, 0, key_width, key_height), 'white': white, 'pressed': False, 'sustained': False, 'label': note_label})

        total_piano_width = key_width * 128
        self.setFixedSize(total_piano_width, key_height + 150)
        self.setWindowTitle("Piano Visualizer")

        app_icon = QIcon(r"iconsMIDI\piano.ico")  # Replace with the path to your icon image
        self.setWindowIcon(app_icon)  # Set the window icon

    def load_midi(self):
        self.stop_midi()
        file_name, _ = QFileDialog.getOpenFileName(self, "Load MIDI File", "", "MIDI Files (*.mid)")
        if file_name:
            self.midi_file = MidiFile(file_name)

    def play_midi(self):
        if self.midi_file:
            self.playing = True
            self.thread = Thread(target=self.play_midi_thread)
            self.thread.start()

    def play_midi_thread(self):
        for msg in self.midi_file.play():
            if not self.playing:
                break
            if msg.type == 'note_on':
                if msg.velocity > 0:
                    self.piano.press_key(msg.note)
                else:
                    self.piano.release_key(msg.note)
            elif msg.type == 'note_off':
                self.piano.release_key(msg.note)
            elif msg.type == 'control_change' and msg.control == 64:
                if msg.value >= 64:
                    self.piano.sustain_on()
                else:
                    self.piano.sustain_off()
            self.output.send(msg)

    def stop_midi(self):
        self.playing = False
        self.piano.reset_keys()
        self.piano.sustain_off()

        self.output.reset()
        self.output.close()
        self.output = mido.open_output('Microsoft GS Wavetable Synth 0')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = MidiPlayer()
    player.show()
    sys.exit(app.exec())
