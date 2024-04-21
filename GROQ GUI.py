import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QTextEdit, QPushButton, QMessageBox
from PyQt5 import QtGui
from PyQt5.QtGui import QIcon
from groq import Groq
import os
import html

class MyApp(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, 1000, 700)
        self.setWindowTitle("GROQ GUI")
        self.setWindowIcon(QIcon('groq.ico'))

        layout = QVBoxLayout()

        self.input_text = QLineEdit()
        self.input_text.returnPressed.connect(self.onSubmit)
        layout.addWidget(self.input_text)

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        layout.addWidget(self.output_text)

        submit_button = QPushButton('Submit')
        submit_button.clicked.connect(self.onSubmit)
        layout.addWidget(submit_button)

        clear_button = QPushButton('Clear')
        clear_button.clicked.connect(self.clearOutput)
        layout.addWidget(clear_button)

        self.setLayout(layout)

        self.show_popup()

    def onSubmit(self):
        input_text = self.input_text.text()
        self.input_text.clear()  # Clear the input field
        self.output_text.clear()
        self.process_input(input_text)

    def process_input(self, input_text):
        if os.path.exists('key.txt') == True:
            key = open('key.txt', 'r')
            api_key_text = key.read()

            client = Groq(
                api_key = api_key_text
            )

            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": input_text,
                    }
                ],
                model="llama3-70b-8192",
            )
            
            output_text = chat_completion.choices[0].message.content
            formatted_text = self.format_text(output_text)
            self.output_text.setHtml(formatted_text)

    def format_text(self, text):
        # Escape HTML code
        text = html.escape(text)

        # Format **bold** text
        while "**" in text:
            start = text.find("**")
            end = text.find("**", start + 2)
            bold_text = text[start + 2:end]
            text = text.replace("**" + bold_text + "**", "<b>" + bold_text + "</b>", 1)

        # Format ````code block```` text
        text = text.replace("```", "<code><pre style='background-color: #f0f0f0; padding: 5px;'>")
        text = text.replace("```", "</pre></code>")

        # Add HTML and body tags
        text = "<html><head><style>code { background-color: #f0f0f0; padding: 5px; }</style></head><body>" + text + "</body></html>"

        return text

    def clearOutput(self):
        self.output_text.clear()

    def show_popup(self):
        if os.path.exists('key.txt') == True:
            if not os.path.exists('api_key_valid.txt'):
                key = open('key.txt', 'r')
                api_key_text = key.read()

                client = Groq(
                    api_key = api_key_text
                )

                try:
                    chat_completion = client.chat.completions.create(
                        messages=[
                            {
                                "role": "user",
                                "content": "Hello",
                            }
                        ],
                        model="llama3-70b-8192",
                    )
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Information)
                    msg.setText("Groq API key valid!")
                    msg.setWindowTitle("Info")
                    msg.setStandardButtons(QMessageBox.Ok)
                    msg.setDefaultButton(QMessageBox.Ok)
                    msg.exec_()
                    with open('api_key_valid.txt', 'w') as f:
                        f.write('True')
                except:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Critical)
                    msg.setText("Invalid Groq API key!")
                    msg.setWindowTitle("Error")
                    msg.setStandardButtons(QMessageBox.Ok)
                    msg.setDefaultButton(QMessageBox.Ok)
                    msg.exec_()
            else:
                if not os.path.exists('key.txt'):
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Critical)
                    msg.setText("You need a Groq API key in order to use this application! Put it in a new .txt file with a name 'key', and save in the same directory as the application.")
                    msg.setWindowTitle("Error")
                    msg.setStandardButtons(QMessageBox.Ok)
                    msg.setDefaultButton(QMessageBox.Ok)
                    msg.exec_()
                    exit()
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("You need a Groq API key in order to use this application! Put it in a new .txt file with a name 'key', and save in the same directory as the application.")
            msg.setWindowTitle("Error")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setDefaultButton(QMessageBox.Ok)
            msg.exec_()
            exit()

if __name__ == '__main__':
    font = QtGui.QFont()
    font.setFamily("Arial")  # Set the font family
    font.setPointSize(14)  # Set the font size
    app = QApplication(sys.argv)
    app.setFont(font)
    ex = MyApp()
    ex.show()
    sys.exit(app.exec_())