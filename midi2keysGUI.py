import sys
import pretty_midi
import pyperclip as pc
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QTextEdit, QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QIcon

def read_midi_file(file_path):
    return pretty_midi.PrettyMIDI(file_path)

def get_note_and_timing(instrument, key_mapping):
    notes = []
    timings = []
    current_group = []
    prev_time = -1

    for note in instrument.notes:
        note_name = pretty_midi.note_number_to_name(note.pitch)
        note_time = note.start
        keyboard_key = key_mapping.get(note_name, '')

        if keyboard_key:
            if note_time == prev_time:
                current_group.append(keyboard_key)
            else:
                if current_group:
                    notes.append(current_group)
                current_group = [keyboard_key]
                timings.append(note_time)
            
            prev_time = note_time

    if current_group:
        notes.append(current_group)
        
    return notes, timings

def generate_output_string(notes, timings):
    output = []
    for note_group in notes:
        if len(note_group) > 1:
            output.append(f"[{''.join(note_group)}]")
        else:
            output.append(note_group[0])

    return ''.join(output)

class Worker(QThread):
    finished = pyqtSignal(str)

    def __init__(self, file_path, key_mapping):
        super(Worker, self).__init__()
        self.file_path = file_path
        self.key_mapping = key_mapping

    def run(self):
        try:
            midi_data = read_midi_file(self.file_path)
        except Exception as e:
            self.finished.emit(f"Error reading MIDI file: {e}")
            return

        if midi_data.instruments:
            notes, timings = get_note_and_timing(midi_data.instruments[0], self.key_mapping)
            result = generate_output_string(notes, timings)
            self.finished.emit(result)
        else:
            self.finished.emit("No instruments found in the MIDI file.")

class MidiApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.result_edit = QTextEdit()
        layout.addWidget(self.result_edit)

        self.open_button = QPushButton('Open MIDI File')
        self.open_button.clicked.connect(self.open_midi_file)
        layout.addWidget(self.open_button)

        self.copy_button = QPushButton('Copy to Clipboard')
        self.copy_button.clicked.connect(self.copy_to_clipboard)
        layout.addWidget(self.copy_button)

        self.setLayout(layout)
        self.setWindowTitle('MIDI to Keys')
        self.setWindowIcon(QIcon('iconsMIDI\\piano.ico'))
        self.show()

    def open_midi_file(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Open MIDI File", "", "MIDI Files (*.mid);;All Files (*)", options=options)
        if file_path:
            self.worker = Worker(file_path, key_mapping)
            self.worker.finished.connect(self.update_text_area)
            self.worker.start()

    def update_text_area(self, result):
        self.result_edit.setText(result)

    def copy_to_clipboard(self):
        pc.copy(self.result_edit.toPlainText())
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("Keys copied to the clipboard!")
        msg.setWindowTitle("Clipboard Copy")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

key_mapping = {
    'C3': '1', 'C#3': '!', 'D3': '2', 'D#3': '@', 'E3': '3', 'F3': '4', 'F#3': '$', 'G3': '5', 'G#3': '%', 'A3': '6', 'A#3': '^', 'B3': '7',
    'C4': '8', 'C#4': '*', 'D4': '9', 'D#4': '(', 'E4': '0', 'F4': 'q', 'F#4': 'Q', 'G4': 'w', 'G#4': 'W', 'A4': 'e', 'A#4': 'E', 'B4': 'r',
    'C5': 't', 'C#5': 'T', 'D5': 'y', 'D#5': 'Y', 'E5': 'u', 'F5': 'i', 'F#5': 'I', 'G5': 'o', 'G#5': 'O', 'A5': 'p', 'A#5': 'P', 'B5': 'a',
    'C6': 's', 'C#6': 'S', 'D6': 'd', 'D#6': 'D', 'E6': 'f', 'F6': 'g', 'F#6': 'G', 'G6': 'h', 'G#6': 'H', 'A6': 'j', 'A#6': 'J', 'B6': 'k',
    'C7': 'l', 'C#7': 'L', 'D7': 'z', 'D#7': 'Z', 'E7': 'x', 'F7': 'c', 'F#7': 'C', 'G7': 'v', 'G#7': 'V', 'A7': 'b', 'A#7': 'B', 'B7': 'n',
    'C8': 'm'
}

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(r'iconsMIDI\piano.ico'))
    ex = MidiApp()
    sys.exit(app.exec_())