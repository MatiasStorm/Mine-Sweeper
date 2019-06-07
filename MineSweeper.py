import sys
from PyQt5.QtWidgets import QApplication, QLabel, QPushButton, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QDialog
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTime, QTimer, QObject, Qt, QSize
import random


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

        self.setWindowTitle("Mine Sweeper")
        self.setWindowIcon(MINE_ICON)
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.masterLayout = QVBoxLayout(self.centralWidget)

        # Top buttons/widgets:
        topLayout = QHBoxLayout()
        topLayout.setSpacing(100)

        #Time label:
        self.timeLabel = QLabel("0.0 Secounds")
        self.timeLabel.setStyleSheet("font: bold 18px")
        self.time = QTime(0, 0, 0)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)

        #Start button and flag label
        self.startButton = QPushButton()
        self.startButton.setFixedSize(45,45)
        self.startButton.setStyleSheet("QPushButton {background-color: white}")
        self.startButton.setIcon(QIcon("Happy_smiley.png"))
        self.startButton.setIconSize(QSize(45,45))
        self.startButton.clicked.connect(self.new_game)
        self.total_mines = 0
        self.total_flags = 0
        self.flagLabel = QLabel()
        self.flagLabel.setStyleSheet("font: bold 18px")

        topLayout.addWidget(self.timeLabel)
        topLayout.addWidget(self.startButton)
        topLayout.addWidget(self.flagLabel)
        
        self.masterLayout.addLayout(topLayout)

        #Button layout
        self.buttons = []
        self.buttonlayout = QGridLayout()
        self.buttonlayout.setSpacing(0)

        self.masterLayout.addLayout(self.buttonlayout)
        self.centralWidget.setLayout(self.masterLayout)

        #Building the buttons:
        self.buttons = []
        for r in range(15):
            row = []
            for c in range(15):
                b = Field(r, c)
                b.setFixedSize(32, 32)
                row.append(b)
                b.clicked.connect(self.button_clicked)
                b.setContextMenuPolicy(Qt.CustomContextMenu)
                b.customContextMenuRequested.connect(self.right_click)
                self.buttonlayout.addWidget(b, r, c)
            self.buttons.append(row)

        self.place_mines()

    def new_game(self):
        """
        Resets all buttons, flagLabel, timer and startButton
        :return:
        """
        self.startButton.setIcon(QIcon("Happy_smiley.png"))
        self.total_flags = 0
        self.total_mines = 0
        self.update_flagLabel()
    
        self.time.currentTime()
        self.timer.dumpObjectInfo()
        self.timer.stop()
        self.timerRunning = False
        self.timeLabel.setText("0.0 Secounds")
    
        # Resetting buttons:
        for row in self.buttons:
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
        Place mines, at random depending on the BOMB_RATIO
        :return:
        """
        for i in range(2):
            if i == 0:
                for r in self.buttons:
                    for b in r:
                        if random.random() < BOMB_RATIO:
                            b.set_isMine(True)
                            self.total_mines += 1
            else:
                for r in self.buttons:
                    for b in r:
                        self.count_mines(b)
        self.update_flagLabel()
    
    def count_mines(self, button):
        """
        Counting nearby mines of every Field, and adds the number to the Field function set_mine_count.
        :param button: A button in the game, from the class Field.
        :return:
        """
        row = button.get_row()
        col = button.get_col()
        mine_count = 0
        button = self.buttons[row][col]
        for r in range(row - 1, row + 2):
            for c in range(col - 1, col + 2):
                if r >= 0 and c >=0:
                    try:
                        temp = self.buttons[r][c]
                        if temp.get_isMine():
                            mine_count += 1
                    except IndexError:
                        None
        button.set_mine_count(mine_count)
        return
    
    def button_clicked(self):
        """
        If a button is clicked, timer starts running, if button is a mine game ends, else CSB is called.
        :return:
        """
        button = self.sender()
        if not self.timerRunning:
            self.time.start()
            self.timer.start(100)
            self.timerRunning = True
            # self.update_timer()
    
        if not button.get_flag():
            button.setFlat(True)
            button.setEnabled(False)
    
            if button.get_isMine():
                button.setIcon(MINE_ICON)
                self.end_game("loose")
            else:
                self.CSB(button)
            return
        return
    
    def CSB(self, button):
        """
        Checks all the surroudning buttons mine_count value, and sets their text as that number.
        :param button: Button from the call Field.
        :return:
        """
        if button.get_mine_count() != 0:
            button.setText(str(button.get_mine_count()))
        row = button.get_row()
        col = button.get_col()
        for r in range(row - 1, row + 2):
            for c in range(col - 1, col + 2):
                if c >= 0 and r >= 0:
                    try:
                        temp = self.buttons[r][c]
                        if not temp.get_flag() and not temp.get_isMine():
                            self.set_button_stylesheet(temp)
                            if temp.isEnabled():
                                if temp.get_mine_count() != 0:
                                    temp.setEnabled(False)
                                    temp.setFlat(True)
                                    if temp.get_mine_count() != 0:
                                        temp.setText(str(temp.get_mine_count()))
                                elif temp.get_mine_count() == 0:
                                    temp.setEnabled(False)
                                    temp.setFlat(True)
                                    self.CSB(temp)
                    except IndexError:
                        None
        return
    
    def right_click(self):
        """
        If button has flag, removes flag, else places flag.
        Checks if all mines have been flagged, if ture calls end_game().
        :return:
        """
        button = self.sender()
        if not button.get_flag():
            button.setFlat(True)
            button.setIcon(QIcon("flag.png"))
            button.set_flag(True)
            self.set_button_stylesheet(button)
            self.total_flags += 1
            self.update_flagLabel()
        else:
            button.setFlat(False)
            button.setIcon(QIcon())
            button.set_flag(False)
            button.setStyleSheet("")
            self.total_flags -= 1
            self.update_flagLabel()
        if self.is_game_over():
            self.add_score_to_file()
            self.end_game("win")
    
    def is_game_over(self):
        """
        Checks if all mines have been flagged
        :return:
        """
        for r in self.buttons:
            for b in r:
                if b.get_flag() and not b.get_isMine() or b.get_isMine() and not b.get_flag():
                    return False
        return True
    
    def end_game(self, WL):
        """
        Ends game by revealing all Fields, and either updating the smiley to a sad one if the game is lost or
        opening the win_dialog if the game is won.
        :param WL: String, "loose" if the game is lost or "win" if the game is won.
        :return:
        """
        self.timer.stop()
        # Reveals all buttons:
        for rows in self.buttons:
            for b in rows:
                self.set_button_stylesheet(b)
                b.setEnabled(False)
                b.setFlat(True)
                if b.get_isMine() and not b.get_flag():
                    b.setIcon(MINE_ICON)
                elif not b.get_isMine() and b.get_flag():
                    b.setIcon(QIcon("flag_with_cross.png"))
                elif not b.get_isMine() and not b.get_flag():
                    if b.get_mine_count() != 0:
                        b.setText(str(b.get_mine_count()))
    
        # Displays sad smiley or opens win dialog if the game has been won:
        if WL == "loose":
            self.startButton.setIcon(QIcon("Sad_smiley.jpg"))
        else:
            high_scores = []
            with open("High_Scores.txt", "r") as file:
                for line in file.readlines()[1:]:
                    high_scores.append(line.split())
            high_scores.sort(key=lambda x: -float(x[0]))
            self.win_dialog(high_scores[0:5])
    
        return
    
    def update_timer(self):
        """
        Updates timeLabel
        """
        secs = self.time.elapsed() / 1000.0
        self.timeLabel.setText(str(round(secs, 1)) + " Secounds")
    
    def update_flagLabel(self):
        """
        Updates flagLabel, every time a flag has be placed or removed.
        :return:
        """
        self.flagLabel.setText(str(self.total_flags) + "/" + str(self.total_mines) + " Flags")
        return
    
    def set_button_stylesheet(self, button):
        """
        Sets the button stylesheet depending on the mine_count value.
        :param button:
        :return:
        """
        if button.get_mine_count() == 0 or button.get_isMine() or button.get_flag():
            button.setStyleSheet("QPushButton {border: 1px solid; color: black}")
        else:
            for num, col in zip((1, 2, 3, 4, 5, 6, 7), ("blue", "green", "red", "darkblue", "darkred", "pink", "yellow")):
                if button.mine_count == num:
                    button.setStyleSheet("QPushButton {font: bold 20px; color: " + col + "; border: 1px solid}")
        return
    
    def win_dialog(self, high_scores):
        """
        Sets up and displays the win dialog.
        :param high_scores: a list of lists containing the 5 highest scores.
        :return:
        """
        dialog = QDialog()
    
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
        score_layout.addWidget(QLabel(str(self.timeLabel.text()).split()[0]), 7, 1)
        score_layout.addWidget(QLabel(str(self.total_mines)), 7, 2)
    
        NG_btn = QPushButton("New Game")
        exit_btn = QPushButton("Exit")
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
        time = self.timeLabel.text().split()[0]
        self.score = int(self.total_mines / float(time) * 1000)
        with open("High_scores.txt", "a") as file:
            file.write(str(self.score) + " " + str(time) + " " + str(self.total_mines) + "\n")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    MINE_ICON = QIcon("Mine.png")
    BOMB_RATIO = 0.01

    game = MainWindow()
    game.show()
    app.exec_()

