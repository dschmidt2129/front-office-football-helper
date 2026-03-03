# Modules
import os
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QTextEdit, QComboBox, QPushButton, QHBoxLayout, QVBoxLayout, QLineEdit, QFileDialog, QSpacerItem, QSizePolicy
    
# main.py, at the very top
import faulthandler
faulthandler.enable()

class FOF8FolderSelector(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.label = QLabel("Please select the Front Office Football 8 installation folder:")
        self.folder_path_edit = QLineEdit()
        self.browse_button = QPushButton("Browse...")
        self.path_display = QLabel("")

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.folder_path_edit)
        layout.addWidget(self.browse_button)
        layout.addWidget(self.path_display)
        self.setLayout(layout)

        self.browse_button.clicked.connect(self.browse_folder)

        # Suggest the default path
        default_path = os.path.join(os.path.expanduser("~"), "AppData", "Local", "Solecismic Software", "Front Office Football Eight")
        self.folder_path_edit.setText(default_path)

    def browse_folder(self):
        folder_path = QFileDialog.getExistingDirectory(
            self.parentWidget(),  # Use the parent widget for the dialog
            "Select Folder",
            self.folder_path_edit.text(),
            QFileDialog.ShowDirsOnly
        )

        if folder_path:
            self.folder_path_edit.setText(folder_path)
            self.path_display.setText(folder_path)
            print(f"Selected FOF8 Folder: {folder_path}")

    def get_selected_path(self):
        """Returns the currently selected folder path."""
        return self.folder_path_edit.text()

class Home(QWidget):
       
    # Constructor
    def __init__(self):
        super().__init__()
        self.initUI()
        self.settings()
        self.button_click()
    
    # App Object and Design
    def initUI(self):
        self.output_box = QTextEdit()
        self.process_game = QPushButton("Process Game Files")
        self.clear_log = QPushButton("Clear Game Log")
        self.select_team = QComboBox()
        teams = ["Cleveland", "Indianapolis", "Las Vegas", "Miami", "Philadelphia"]
        self.select_team.addItems(teams)
        self.label = QLabel("Please select the team to be processed:")
        self.folder_path_edit = QLineEdit()
        self.path_display = QLabel("")
        
        self.master = QHBoxLayout()
        
        col1 = QVBoxLayout()
        col2 = QVBoxLayout()
        
        self.folder_selector = FOF8FolderSelector()

        col1.addWidget(self.label)
        col1.addWidget(self.select_team)        
        # Add a flexible vertical spacer that will take up available space
        spacer2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        col1.addItem(spacer2)
        col1.addWidget(self.folder_selector)
        # Add a flexible vertical spacer that will take up available space
        spacer1 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        col1.addItem(spacer1)
        col1.addWidget(self.process_game)
        col1.addWidget(self.clear_log)
        # Add a flexible vertical spacer that will take up available space
        spacer3 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        col1.addItem(spacer3)
        
        col2.addWidget(self.output_box)
        
        self.master.addLayout(col1, 50)
        self.master.addLayout(col2, 50)
        self.setLayout(self.master)
    
    # App Settings
    def settings(self):
        self.setWindowTitle("FOF8 Helper")
        self.setGeometry(250, 250, 1000, 400)    
    
    # Button Events
    def button_click(self):
        self.process_game.clicked.connect(self.process_game_click)
        self.clear_log.clicked.connect(self.clear_log_click)
    
    # Process Game Button Click
    def process_game_click(self):
        path = self.folder_selector.get_selected_path()
        print(f"Path from selector: {path}", flush=True)
        if not os.path.exists(path):
            print("Invalid path selected", flush=True)
            self.output_box.setText("Invalid path selected. Please select a valid FOF8 installation folder.")
            self.output_box.update()
            return
        print("Processing game files...", flush=True)
        team_combo_index = self.select_team.currentIndex()
        team_combo_text = self.select_team.currentText()
        
        from game_service import game_service
        from front_office_football_service import front_office_football_service
        front_office_service = front_office_football_service(path, self.output_box)
        game_service = game_service(path, self.output_box)
        front_office_football_service = front_office_football_service(path, self.output_box)
        front_office_football_service.iterate_through_gamelog(path, self.select_team, team_combo_index, team_combo_text, self.output_box)
        print("Game files processed.")
    
    def clear_log_click(self):
        """Clears the output box."""
        print("Clearing log...")
        self.output_box.clear()
    
    def print_selected_path(self):
        path = self.folder_selector.get_selected_path()
        print(f"Path from selector: {path}")
    
# Main Run
if __name__ == "__main__":
    app = QApplication([])
    main = Home()
    main.show()
    app.exec_()