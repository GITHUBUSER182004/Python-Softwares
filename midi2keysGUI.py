import sys
import pretty_midi
import pyautogui
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel, QSlider
from collections import defaultdict

pyautogui.FAILSAFE = False

class MyApp(QWidget):

    def __init__(self):
        super().__init__()

        self.initUI()
        self.timer = QTimer()
        self.timer.timeout.connect(self.play_notes)
        self.speed_multiplier = 1.0
        self.current_event_index = 0
        self.note_events = []
        self.isPlaying = False
        self.original_interval = 0
        self.note_to_key = {
            'C3': '1', 'C#3': '!', 'D3': '2', 'D#3': '@', 'E3': '3', 'F3': '4', 'F#3': '$', 'G3': '5', 'G#3': '%', 'A3': '6', 'A#3': '^', 'B3': '7',
            'C4': '8', 'C#4': '*', 'D4': '9', 'D#4': '(', 'E4': '0', 'F4': 'q', 'F#4': 'Q', 'G4': 'w', 'G#4': 'W', 'A4': 'e', 'A#4': 'E', 'B4': 'r',
            'C5': 't', 'C#5': 'T', 'D5': 'y', 'D#5': 'Y', 'E5': 'u', 'F5': 'i', 'F#5': 'I', 'G5': 'o', 'G#5': 'O', 'A5': 'p', 'A#5': 'P', 'B5': 'a',
            'C6': 's', 'C#6': 'S', 'D6': 'd', 'D#6': 'D', 'E6': 'f', 'F6': 'g', 'F#6': 'G', 'G6': 'h', 'G#6': 'H', 'A6': 'j', 'A#6': 'J', 'B6': 'k',
            'C7': 'l', 'C#7': 'L', 'D7': 'z', 'D#7': 'Z', 'E7': 'x', 'F7': 'c', 'F#7': 'C', 'G7': 'v', 'G#7': 'V', 'A7': 'b', 'A#7': 'B', 'B7': 'n',
            'C8': 'm'
        }

    def initUI(self):
        vbox = QVBoxLayout()

        self.loadButton = QPushButton('Load MIDI', self)
        self.loadButton.setStyleSheet("QPushButton { background-color: #2ecc71; font: bold 16px; padding: 5px; }")
        self.loadButton.clicked.connect(self.read_midi)
        vbox.addWidget(self.loadButton)

        self.label = QLabel('No MIDI loaded', self)
        self.label.setStyleSheet("QLabel { font: bold 14px; }")
        vbox.addWidget(self.label)

        self.simulationButton = QPushButton('Start Simulation', self)
        self.simulationButton.setStyleSheet("QPushButton { background-color: #3498db; font: bold 16px; padding: 5px; }")
        self.simulationButton.clicked.connect(self.toggle_simulation)
        vbox.addWidget(self.simulationButton)

        vbox.addWidget(QLabel("Playback Speed:"))

        self.speedSlider = QSlider(Qt.Orientation.Horizontal, self)
        self.speedSlider.setStyleSheet("QSlider { background: #ecf0f1; } QSlider::groove:horizontal { background: #bdc3c7; } QSlider::handle:horizontal { background: #e74c3c; width: 20px; }")
        self.speedSlider.setRange(50, 200)  # 50% to 200% speed
        self.speedSlider.setValue(100)
        self.speedSlider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.speedSlider.setTickInterval(10)
        self.speedSlider.valueChanged.connect(self.update_speed)
        vbox.addWidget(self.speedSlider)
        
        self.speedLabel = QLabel("100%", self)
        self.speedLabel.setStyleSheet("QLabel { font: bold 14px; }")
        vbox.addWidget(self.speedLabel)

        self.setLayout(vbox)
        self.setWindowTitle('MIDI to Keyboard')
        self.setStyleSheet("QWidget { background-color: #ecf0f1; }")
        self.show()

    def update_speed(self, value):
        self.speed_multiplier = value / 100.0
        self.speedLabel.setText(f"{value}%")
        
        if self.timer.isActive():
            elapsed_time = self.original_interval - self.timer.remainingTime()
            adjusted_elapsed_time = elapsed_time / self.speed_multiplier
            remaining_time = self.original_interval - adjusted_elapsed_time
            remaining_time = max(remaining_time, 0)
            self.timer.setInterval(int(remaining_time))

    def read_midi(self):
        self.midi_path, _ = QFileDialog.getOpenFileName(self, "Load MIDI file", "", "MIDI Files (*.mid *.midi);;All Files (*)")
        if self.midi_path:
            self.label.setText(f'Loaded {self.midi_path}')
            midi_data = pretty_midi.PrettyMIDI(self.midi_path)
            self.parse_midi(midi_data)
            self.current_event_index = 0

    def parse_midi(self, midi_data):
        timed_events = defaultdict(list)
        
        for instrument in midi_data.instruments:
            for note in instrument.notes:
                timed_events[note.start].append(note)
                
        sorted_times = sorted(timed_events.keys())
        
        self.note_events = []
        for t in sorted_times:
            self.note_events.append(('chord', timed_events[t]))

        self.current_event_index = 0

    def toggle_simulation(self):
        if not self.isPlaying:
            self.simulationButton.setText('Stop Simulation')
            self.timer.start(5000)
            self.isPlaying = True
        else:
            self.simulationButton.setText('Start Simulation')
            self.timer.stop()
            self.isPlaying = False

    def play_notes(self):
        if self.current_event_index < len(self.note_events):
            event_type, event_data = self.note_events[self.current_event_index]
            if event_type == 'chord':
                chord_keys = [self.note_to_key.get(pretty_midi.note_number_to_name(note.pitch), '') for note in event_data]
                chord_keys = [key for key in chord_keys if key]
                if chord_keys:
                    pyautogui.hotkey(*chord_keys)
            self.current_event_index += 1
            if self.current_event_index < len(self.note_events):
                next_event_time = self.note_events[self.current_event_index][1][0].start
                self.original_interval = int((next_event_time - event_data[0].start) * 1000)
                self.timer.setInterval(int(self.original_interval / self.speed_multiplier))
            else:
                self.timer.stop()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec())
