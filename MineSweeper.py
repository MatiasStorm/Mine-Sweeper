import sys
from PyQt5.QtWidgets import QApplication, QLabel, QPushButton, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QDialog
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTime, QTimer, QObject, Qt, QSize
import random
from Settings import *
import numpy as np


class Field(QPushButton):
    def __init__(self, row, col, parent=None):
        super(Field, self).__init__(parent)
        self.row = row
        self.col = col
        self.isMine = False
        self.mine_count = 0
        self.flag = False

    def get_isMine(self):
        return self.isMine

    def set_isMine(self, bool):
        self.isMine = bool

    def get_mine_count(self):
        return self.mine_count

    def set_mine_count(self, i):
        self.mine_count = i

    def get_row(self):
        return self.row

    def get_col(self):
        return self.col

    def get_flag(self):
        return self.flag

    def set_flag(self, bool):
        self.flag = bool

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.timerRunning = False
        self.load_images()
        

        self.setWindowTitle("Mine Sweeper")
        self.setWindowIcon(self.mine_icon)
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.masterLayout = QVBoxLayout(self.centralWidget)

        # Top fields/widgets:
        topLayout = QHBoxLayout()
        topLayout.setSpacing(100)

        #Time label:
        self.time_label = QLabel("0.0 Secounds")
        self.time_label.setStyleSheet("font: bold 18px")
        self.time = QTime(0, 0, 0)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)

        #Start field and flag label
        self.start_button = QPushButton()
        self.start_button.setFixedSize(45,45)
        self.start_button.setStyleSheet("QPushfield {background-color: white}")
        self.start_button.setIcon(self.happy_smiley_icon)
        self.start_button.setIconSize(QSize(45,45))
        self.start_button.clicked.connect(self.new_game)
        self.total_mines = BOMBS
        self.total_flags = 0
        self.flag_label = QLabel()
        self.flag_label.setStyleSheet("font: bold 18px")

        topLayout.addWidget(self.time_label)
        topLayout.addWidget(self.start_button)
        topLayout.addWidget(self.flag_label)
        
        self.masterLayout.addLayout(topLayout)

        #field layout
        self.fields = []
        self.fieldlayout = QGridLayout()
        self.fieldlayout.setSpacing(0)

        self.masterLayout.addLayout(self.fieldlayout)
        self.centralWidget.setLayout(self.masterLayout)

        #Building the fields:
        self.fields = []
        for r in range(FIELD_ROWS):
            row = []
            for c in range(FIELD_COLS):
                b = Field(r, c)
                b.setFixedSize(32, 32)
                row.append(b)
                b.clicked.connect(self.field_clicked)
                b.setContextMenuPolicy(Qt.CustomContextMenu)
                b.customContextMenuRequested.connect(self.right_click)
                self.fieldlayout.addWidget(b, r, c)
            self.fields.append(row)

        self.place_mines()

    def load_images(self):
        self.happy_smiley_icon = QIcon(HAPPY_SMILEY_IMG)
        self.mine_icon = QIcon(MINE_IMG)
        self.sad_smiley_icon = QIcon(HAPPY_SMILEY_IMG)
        self.flag_with_cross_icon = QIcon(FLAG_WITH_CROSS_IMG)
        self.flag_icon = QIcon(FLAG_IMG)

    def new_game(self):
        """
            Resets all fields, flag_label, timer and start_button
        """
        self.start_button.setIcon(self.happy_smiley_icon)
        self.total_flags = 0
        self.total_mines = BOMBS
        self.update_flag_label()
    
        self.time.currentTime()
        self.timer.stop()
        self.timerRunning = False
        self.time_label.setText("0.0 Secounds")
    
        # Resetting fields:
        for row in self.fields:
            for b in row:
                b.set_isMine(False)
                b.set_flag(False)
                b.setFlat(False)
                b.setEnabled(True)
                b.setIcon(QIcon())
                b.setText("")
                b.setStyleSheet("")
        self.place_mines()
        return
    
    def place_mines(self):
        """
            Place mines, at random
        """
        # Creating a 1D array of 
        fields1d = []
        for row in self.fields:
            fields1d.extend(row)
        random.shuffle(fields1d)
        
        i = j = 0
        for i in range(self.total_mines):
            fields1d[i].set_isMine(True)
            i += 1;
            if i >= len(self.fields) - 1:
                i = 0;
                j += 1;
        
        for r in self.fields:
            for b in r:
                self.count_mines(b)
        self.update_flag_label()
    
    def count_mines(self, field):
        """
            Counting nearby mines of every Field, and adds the number to the Field's mine_count.
            :param field: class Field.
        """
        row = field.get_row()
        col = field.get_col()
        mine_count = 0
        field = self.fields[row][col]
        for r in range(row - 1, row + 2):
            for c in range(col - 1, col + 2):
                if r >= 0 and c >=0:
                    try:
                        temp = self.fields[r][c]
                        if temp.get_isMine():
                            mine_count += 1
                    except IndexError:
                        None
        field.set_mine_count(mine_count)
    
    def field_clicked(self):
        """
            If a field is clicked, timer starts running, if field is a mine game ends, else CSF is called.
        """
        field = self.sender()
        if not self.timerRunning:
            self.time.start()
            self.timer.start(100)
            self.timerRunning = True
            # self.update_timer()
    
        if not field.get_flag():
            field.setFlat(True)
            field.setEnabled(False)
    
            if field.get_isMine():
                field.setIcon(self.mine_icon)
                self.end_game("loose")
            else:
                self.CSF(field)
    
    def CSF(self, field):
        """
            Checks all the surroudning fields mine_count value, and sets their text as that number.
            :param field: field from the call Field.
        """
        if field.get_mine_count() != 0:
            field.setText(str(field.get_mine_count()))
        row = field.get_row()
        col = field.get_col()
        for r in range(row - 1, row + 2):
            for c in range(col - 1, col + 2):
                if c >= 0 and r >= 0:
                    try:
                        temp = self.fields[r][c]
                        if not temp.get_flag() and not temp.get_isMine():
                            self.set_field_stylesheet(temp)
                            if temp.isEnabled():
                                if temp.get_mine_count() != 0:
                                    temp.setEnabled(False)
                                    temp.setFlat(True)
                                    if temp.get_mine_count() != 0:
                                        temp.setText(str(temp.get_mine_count()))
                                elif temp.get_mine_count() == 0:
                                    temp.setEnabled(False)
                                    temp.setFlat(True)
                                    self.CSF(temp)
                    except IndexError:
                        None
    
    def right_click(self):
        """
            If field has flag, removes flag, else places flag.
            Checks if all mines have been flagged, if ture calls end_game().
        """
        field = self.sender()
        if not field.get_flag():
            field.setFlat(True)
            field.setIcon(self.flag_icon)
            field.set_flag(True)
            self.set_field_stylesheet(field)
            self.total_flags += 1
            self.update_flag_label()
        else:
            field.setFlat(False)
            field.setIcon(QIcon())
            field.set_flag(False)
            field.setStyleSheet("")
            self.total_flags -= 1
            self.update_flag_label()
        if self.is_game_over():
            self.add_score_to_file()
            self.end_game("win")
    
    def is_game_over(self):
        """
            Checks if all mines have been flagged
        """
        for r in self.fields:
            for b in r:
                if b.get_flag() and not b.get_isMine() or b.get_isMine() and not b.get_flag():
                    return False
        return True
    
    def end_game(self, WL):
        """
            Ends game by revealing all Fields, and either updating the smiley to a sad one if the game is lost or
            opening the win_dialog if the game is won.
            :param WL: String, "loose" if the game is lost or "win" if the game is won.
        """
        self.timer.stop()
        # Reveal all fields:
        for rows in self.fields:
            for b in rows:
                self.set_field_stylesheet(b)
                b.setEnabled(False)
                b.setFlat(True)
                if b.get_isMine() and not b.get_flag():
                    b.setIcon(self.mine_icon)
                elif not b.get_isMine() and b.get_flag():
                    b.setIcon(self.flag_with_cross_icon)
                elif not b.get_isMine() and not b.get_flag():
                    if b.get_mine_count() != 0:
                        b.setText(str(b.get_mine_count()))
    
        # Display sad smiley or open win dialog if the game has been won:
        if WL == "loose":
            self.start_button.setIcon(self.sad_smiley_icon)
        else:
            high_scores = []
            with open("High_Scores.txt", "r") as file:
                for line in file.readlines()[1:]:
                    high_scores.append(line.split())
            high_scores.sort(key=lambda x: -float(x[0]))
            self.win_dialog(high_scores[0:5])

    
    def update_timer(self):
        """
            Updates time_label
        """
        secs = self.time.elapsed() / 1000.0
        self.time_label.setText(str(round(secs, 1)) + " Secounds")
    
    def update_flag_label(self):
        """
            Updates flag_label, every time a flag has be placed or removed.
        """
        self.flag_label.setText(str(self.total_flags) + "/" + str(self.total_mines) + " Flags")

    
    def set_field_stylesheet(self, field):
        """
            Sets the field stylesheet depending on the mine_count value.
        """
        if field.get_mine_count() == 0 or field.get_isMine() or field.get_flag():
            field.setStyleSheet("QPushButton {border: 1px solid; color: black}")
        else:
            for num, col in zip((1, 2, 3, 4, 5, 6, 7), ("blue", "green", "red", "darkblue", "darkred", "pink", "yellow")):
                if field.mine_count == num:
                    field.setStyleSheet("QPushButton {font: bold 20px; color: " + col + "; border: 1px solid}")
    
    def win_dialog(self, high_scores):
        """
            Sets up and displays the win dialog.
            :param high_scores: a list of lists containing the top 5 high scores.
        """
        dialog = QDialog()
        dialog.setWindowTitle("You Won!")
        
        score_layout = QGridLayout()
        for col, text in enumerate(("Score:", "Time:", "Bombs:")):
            score_layout.addWidget(QLabel(text), 0, col)
        for row, string in enumerate(high_scores):
            for col, text in enumerate(string):
                score_layout.addWidget(QLabel(text), row+1, col)
    
        scoreLabel = QLabel("Your Score:")
        scoreLabel.setStyleSheet("QLabel {font: Bold 13px; color: black}")
        score_layout.addWidget(scoreLabel, 6, 0)
        score_layout.addWidget(QLabel(str(self.score)), 7, 0)
        score_layout.addWidget(QLabel(str(self.time_label.text()).split()[0]), 7, 1)
        score_layout.addWidget(QLabel(str(self.total_mines)), 7, 2)
    
        NG_btn = QPushfield("New Game")
        exit_btn = QPushfield("Exit")
        NG_btn.clicked.connect(self.new_game)
        NG_btn.clicked.connect(dialog.close)
        exit_btn.clicked.connect(dialog.close)
        exit_btn.clicked.connect(self.close)
        
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(NG_btn)
        btn_layout.addWidget(exit_btn)
    
        master_layout = QVBoxLayout()
        ts_label = QLabel("Top Scores:")
        ts_label.setStyleSheet("QLabel {font: Bold 20px; color: black}")
        master_layout.addWidget(ts_label, alignment=Qt.AlignCenter)
        master_layout.addLayout(score_layout)
        master_layout.addLayout(btn_layout)
    
        dialog.setLayout(master_layout)
        dialog.exec_()
        return

    def add_score_to_file(self):
        time = self.time_label.text().split()[0]
        self.score = int(self.total_mines / float(time) * 1000)
        with open("High_scores.txt", "a") as file:
            file.write(str(self.score) + " " + str(time) + " " + str(self.total_mines) + "\n")

if __name__ == "__main__":
    app = QApplication(sys.argv)

    game = MainWindow()
    game.show()
    app.exec_()

