import sys
import os  # Add this at the top with other imports
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QGridLayout, QPushButton, QLabel, 
                            QLineEdit, QFileDialog, QFrame, QSizePolicy,
                            QTextEdit, QTabWidget, QScrollArea, QFormLayout, QSpinBox, 
                            QComboBox, QTableWidget, QTableWidgetItem) 
from PyQt5.QtCore import Qt, QFile, QTextStream
from PyQt5.QtGui import QColor, QPalette, QFont


class FlowLayout(QVBoxLayout):
    """A custom layout that mimics a FlowLayoutPanel from WinForms"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSpacing(2) 
        self.setContentsMargins(2, 2, 2, 2)


class DarkThemeApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Set window properties
        self.setWindowTitle("CMScrape v2")
        self.setMinimumSize(1000, 600)  # Increased width for the split view
        
        # Set dark theme
        self.set_dark_theme()
        
        # Initialize selected button trackers
        self.selected_buttons = {
            "Selenium Mode": None,
            "Human Behavior": None,
            "Ulixee Hero Mode": None,
            "Playwright": None,
            "Headless": None,
            "Behavior Intensity": None
        }
        
        # Create buttons for each row
        self.button_groups = {
            "Selenium Mode": [],
            "Ulixee Hero Mode": [],
            "Human Behavior": [],
            "Playwright": [],
            "Headless": [],
            "Behavior Intensity": []
        }
        
        # Create main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setSpacing(10)
        
        # Create components
        self.create_file_section()
        self.create_button_grid()
        self.create_plugin_dropdown()
        self.create_run_button()
        
        # Create split view for tabs and data analysis
        self.create_split_view()
        
        # Show the window
        self.show()
    
    def set_dark_theme(self):
        # Set the application style to Fusion which is more customizable
        app = QApplication.instance()
        app.setStyle("Fusion")
        
        # Set dark palette
        dark_palette = QPalette()
        
        # Define colors
        bg_color = QColor(30, 30, 30)
        text_color = QColor(255, 255, 255)
        accent_color = QColor(255, 102, 0)  # Dark orange
        
        # Set colors for various UI elements
        dark_palette.setColor(QPalette.Window, bg_color)
        dark_palette.setColor(QPalette.WindowText, text_color)
        dark_palette.setColor(QPalette.Base, QColor(45, 45, 45))
        dark_palette.setColor(QPalette.AlternateBase, bg_color)
        dark_palette.setColor(QPalette.ToolTipBase, text_color)
        dark_palette.setColor(QPalette.ToolTipText, text_color)
        dark_palette.setColor(QPalette.Text, text_color)
        dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ButtonText, text_color)
        dark_palette.setColor(QPalette.BrightText, Qt.red)
        dark_palette.setColor(QPalette.Link, accent_color)
        dark_palette.setColor(QPalette.Highlight, accent_color)
        dark_palette.setColor(QPalette.HighlightedText, Qt.black)
        
        # Apply the palette
        app.setPalette(dark_palette)
        
        # Set stylesheet for better styling of specific components
        style_sheet = """
        QMainWindow {
            background-color: #1E1E1E;
        }
        QPushButton {
            background-color: #333333;
            color: #FFFFFF;
            border: none;
            border-radius: 8px;
            padding: 8px;
            min-height: 20px;
            font-size: 13px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #444444;
        }
        QPushButton:pressed {
            background-color: #FF6600;
        }
        QPushButton:disabled {
            background-color: #2A2A2A;
            color: #666666;
        }
        QPushButton.selected {
            background-color: #FF6600;
            color: #000000;
        }
        QPushButton#run_button {
            background-color: #FF6600;
            color: #000000;
            font-size: 16px;
            min-height: 30px;
            font-weight: bold;
        }
        QPushButton#run_button:hover {
            background-color: #FF8533;
        }
        QLineEdit {
            background-color: #2D2D2D;
            color: #FFFFFF;
            border: 1px solid #3D3D3D;
            border-radius: 6px;
            padding: 8px;
            font-size: 13px;
            min-height: 30px;
        }
        QLabel {
            color: #FFFFFF;
            font-size: 13px;
            font-weight: bold;
        }
        QTextEdit {
            background-color: #2D2D2D;
            color: #FFFFFF;
            border: 1px solid #3D3D3D;
            border-radius: 6px;
            padding: 8px;
            font-size: 13px;
        }
        QTabWidget::pane {
            border: 1px solid #3D3D3D;
            background-color: #2D2D2D;
            border-radius: 6px;
        }
        QTabBar::tab {
            background-color: #333333;
            color: #FFFFFF;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
            padding: 8px 16px;
            margin-right: 2px;
        }
        QTabBar::tab:selected {
            background-color: #2D2D2D;
        }
        QTabBar::tab:!selected {
            margin-top: 2px;
        }
        QLabel#in_tab_label {
            background-color: #1E1E1E;
            color: #00FF00;
            border-radius: 4px;
            padding: 2px 4px;
            margin: 1px;
            font-size: 12px;
            max-height: 16px;
        }
        QLabel#warning_tab_label {
            background-color: #1E1E1E;
            color: #FFFF00;
            border-radius: 4px;
            padding: 2px 4px;
            margin: 1px;
            font-size: 12px;
            max-height: 16px;
        }
        QLabel#error_tab_label {
            background-color: #1E1E1E;
            color: #FF0000;
            border-radius: 4px;
            padding: 2px 4px;
            margin: 1px;
            font-size: 12px;
            max-height: 16px;
        }
        QLabel#data_header {
            font-size: 15px;
            font-weight: bold;
        }
        QLabel#data_subheader {
            font-size: 14px;
            font-weight: bold;
        }
        QLabel#data_value {
            font-size: 14px;
        }
        QSpinBox {
            background-color: #2D2D2D;
            color: #FFFFFF;
            border: 1px solid #3D3D3D;
            border-radius: 6px;
            padding: 2px 8px;
            font-size: 13px;
            min-height: 30px;
        }
        QSpinBox::up-button, QSpinBox::down-button {
            background-color: #444444;
            border-radius: 3px;
            width: 16px;
            height: 12px;
        }
        QSpinBox::up-button:hover, QSpinBox::down-button:hover {
            background-color: #555555;
        }
        QSpinBox::up-button:pressed, QSpinBox::down-button:pressed {
            background-color: #FF6600;
        }
        QSpinBox::up-arrow {
            image: url(none);
            width: 0px;
            height: 0px;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-bottom: 6px solid #FFFFFF;
        }
        QSpinBox::down-arrow {
            image: url(none);
            width: 0px;
            height: 0px;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-top: 6px solid #FFFFFF;
        }
        QPushButton#cancel_button {
            background-color: #FF3333;  /* Red color for cancel */
            color: #FFFFFF;
            font-size: 16px;
            min-height: 30px;
            font-weight: bold;
        }
        QPushButton#cancel_button:hover {
            background-color: #FF5555;
        }
         QComboBox {
            background-color: #2D2D2D;
            color: #FFFFFF;
            border: 1px solid #3D3D3D;
            border-radius: 6px;
            padding: 8px;
            font-size: 13px;
            min-height: 30px;
        }
        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 20px;
            border-left: 1px solid #3D3D3D;
            border-top-right-radius: 6px;
            border-bottom-right-radius: 6px;
        }
        QComboBox::down-arrow {
            image: none;
            width: 0px;
            height: 0px;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-top: 6px solid #FFFFFF;
        }
        QComboBox QAbstractItemView {
            background-color: #2D2D2D;
            color: #FFFFFF;
            border: 1px solid #3D3D3D;
            selection-background-color: #FF6600;
            outline: none;
        }
        QTableWidget {
            background-color: #2D2D2D;
            color: #FFFFFF;
            border: 1px solid #3D3D3D;
            gridline-color: #444444;
        }
        QHeaderView::section {
            background-color: #333333;
            color: #FFFFFF;
            padding: 5px;
            border: 1px solid #3D3D3D;
        }
        QTableWidget::item {
            padding: 5px;
        }
        QTableWidget::item:selected {
            background-color: #FF6600;
            color: #000000;
        }
        """
        
        self.setStyleSheet(style_sheet)
    

    def create_plugin_dropdown(self):
        # Create widget and layout for the dropdown
        dropdown_widget = QWidget()
        dropdown_widget.setMinimumHeight(40)  # Ensure minimum height is set
        dropdown_layout = QHBoxLayout(dropdown_widget)
        dropdown_layout.setContentsMargins(5, 5, 5, 5)  # Add some padding
        
        # Create label for plugin dropdown
        plugin_label = QLabel("Parse Mode:")
        dropdown_layout.addWidget(plugin_label)
        
        # Create dropdown (QComboBox) for plugins
        self.plugin_dropdown = QComboBox()
        self.plugin_dropdown.setMinimumHeight(30)  # Set minimum height
        self.plugin_dropdown.setMinimumWidth(200)  # Set minimum width
        
        # Add default option
        self.plugin_dropdown.addItem("Download HTML")
        
        # Add plugin files
        plugin_files = self.get_plugin_files()
        if len(plugin_files) > 0:
            for file in plugin_files:
                self.plugin_dropdown.addItem(file)
        else:
            # For debugging - add a placeholder item to ensure the dropdown shows something
            print("No plugin files found")
        
        dropdown_layout.addWidget(self.plugin_dropdown, 1)  # Add stretch factor of 1
        
        # Add to main layout
        self.main_layout.addWidget(dropdown_widget)
        
        # Add separator line after dropdown for visibility
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: #333333;")
        self.main_layout.addWidget(separator)

    def get_plugin_files(self):
        plugin_dir = "./Plugins/"
        files = []
        
        try:
            # Check if the directory exists
            if os.path.exists(plugin_dir):
                # Get all JSON files in the directory
                files = [file for file in os.listdir(plugin_dir) if file.endswith('.py')]
            else:
                # Try creating the directory
                try:
                    os.makedirs(plugin_dir)
                except Exception as e:
                    print(f"Failed to create plugin directory: {e}")
        except Exception as e:
            print(f"Error reading plugin directory: {e}")
        
        return files
        
    def create_file_section(self):
        # Create vertical layout for file input
        file_frame = QWidget()
        file_layout = QVBoxLayout(file_frame)
        file_layout.setContentsMargins(0, 0, 0, 0)
        
        # Add file label
        file_label = QLabel("urls:")
        file_layout.addWidget(file_label)
        
        # Create horizontal layout for the input and button
        input_layout = QHBoxLayout()
        input_layout.setContentsMargins(0, 0, 0, 0)
        
        # Add file path input as a multiline text edit but with reduced height (30% of original)
        self.file_path_input = QTextEdit()
        self.file_path_input.setMinimumHeight(70)  # Reduced by 70% from 80
        self.file_path_input.setMaximumHeight(70)  # Fix the height
        self.file_path_input.setAcceptRichText(False)  # Plain text only
        input_layout.addWidget(self.file_path_input, 1)  # 1 is the stretch factor
        
        # Add browse button
        self.browse_button = QPushButton("Load URLs")
        self.browse_button.setMinimumHeight(24)  # Match the reduced height
        self.browse_button.setMaximumHeight(24)  # Fix the height
        self.browse_button.setCursor(Qt.PointingHandCursor)  # Set hand cursor
        self.browse_button.clicked.connect(self.browse_file)
        input_layout.addWidget(self.browse_button)
        
        # Add the input layout to the main file layout
        file_layout.addLayout(input_layout)
        
        # Add to main layout
        self.main_layout.addWidget(file_frame)
        
        # Add separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: #333333;")
        self.main_layout.addWidget(separator)
    
    def create_button_grid(self):
        # Create a grid layout for the button table
        grid_widget = QWidget()
        grid_layout = QGridLayout(grid_widget)
        grid_layout.setSpacing(15)
        
        # Row titles and options
        self.rows = {
            "Selenium Mode": ["standard", "stealth", "undetected", "base"],
            "Ulixee Hero Mode": ["standard", "puppeteer", "<- extra", "<- +stealth"],
            "Playwright": ["standard", "puppeteer +stealth"],
            "Human Behavior": ["true", "false"],
            "Headless": ["true", "false"],
            "Behavior Intensity": ["low", "medium", "high"]
        }
        
        # Create buttons for each row
        for row_idx, (row_title, options) in enumerate(self.rows.items()):
            # Row title
            title_label = QLabel(row_title)
            grid_layout.addWidget(title_label, row_idx, 0)
            
            # Create a frame for the buttons in this row
            button_frame = QWidget()
            button_layout = QHBoxLayout(button_frame)
            button_layout.setContentsMargins(0, 0, 0, 0)
            button_layout.setSpacing(10)  # Increased spacing between buttons
            
            # Create buttons for this row that take equal width
            for option in options:
                button = QPushButton(option)
                button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                button.setMinimumHeight(25)  # Reduced button height
                button.setCursor(Qt.PointingHandCursor)  # Set hand cursor
                
                # Store the row title and option in the button data to identify when clicking
                button.setProperty("row_title", row_title)
                button.setProperty("option", option)
                
                button.clicked.connect(lambda checked, b=button: self.select_button_by_sender(b))
                button_layout.addWidget(button)
                self.button_groups[row_title].append(button)
            
            grid_layout.addWidget(button_frame, row_idx, 1)
        
        # Add to main layout
        self.main_layout.addWidget(grid_widget)
        
        # Set default selection (Selenium Mode: standard)
        self.select_button("Selenium Mode", "standard")
        
        # Set default for other rows
        self.select_button("Human Behavior", "false")
        self.select_button("Headless", "true")
        self.select_button("Behavior Intensity", "medium")
        
        # Update intensity buttons based on human behavior
        self.update_intensity_buttons()
    
    def create_run_button(self):
        # Create horizontal layout for run button and timeout
        run_layout = QHBoxLayout()
        
        # Create cancel button (initially hidden)
        self.cancel_button = QPushButton("CANCEL")
        self.cancel_button.setObjectName("cancel_button")
        self.cancel_button.setCursor(Qt.PointingHandCursor)
        self.cancel_button.clicked.connect(self.cancel_scraping)
        self.cancel_button.setVisible(False)  # Initially hidden
        run_layout.addWidget(self.cancel_button, 1)  # Add stretch factor of 1
        
        # Create run button
        self.run_button = QPushButton("RUN")
        self.run_button.setObjectName("run_button")
        self.run_button.setCursor(Qt.PointingHandCursor)
        self.run_button.clicked.connect(self.run_action)
        run_layout.addWidget(self.run_button, 1)  # Add stretch factor of 1
        
        # Create a container widget for timeout controls with fixed width
        timeout_widget = QWidget()
        timeout_widget.setFixedWidth(160)  # Fixed width of 80px
        timeout_layout = QHBoxLayout(timeout_widget)
        timeout_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        
        # Create timeout label
        timeout_label = QLabel("Timeout:")
        timeout_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        timeout_layout.addWidget(timeout_label)
        
        # Create timeout numeric up/down (QSpinBox)
        self.timeout_value = QSpinBox()
        self.timeout_value.setMinimum(0)
        self.timeout_value.setMaximum(999999)
        self.timeout_value.setValue(30)
        self.timeout_value.setSingleStep(1)
        timeout_layout.addWidget(self.timeout_value)
        
        # Add timeout widget to main layout (no stretch)
        run_layout.addWidget(timeout_widget, 0)  # No stretch
        
        # Add to main layout
        self.main_layout.addLayout(run_layout)

    def create_split_view(self):
        # Create horizontal layout for split view
        split_layout = QHBoxLayout()
        
        # Create left side (tab system)
        self.create_tab_system(split_layout)
        
        # Create right side (data analysis)
        self.create_data_analysis(split_layout)
        
        # Add the split layout to the main layout
        self.main_layout.addLayout(split_layout, 1)  # 1 is the stretch factor
    
    def create_tab_system(self, parent_layout):
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Create tabs with different colors
        self.in_tab = QWidget()
        self.warning_tab = QWidget()
        self.error_tab = QWidget()
        
        # Create scroll areas for each tab
        self.in_scroll = QScrollArea()
        self.in_scroll.setWidgetResizable(True)
        self.warning_scroll = QScrollArea()
        self.warning_scroll.setWidgetResizable(True)
        self.error_scroll = QScrollArea()
        self.error_scroll.setWidgetResizable(True)
        
        # Create content widgets for each scroll area
        self.in_content = QWidget()
        self.warning_content = QWidget()
        self.error_content = QWidget()
        
        # Create flow layouts for each content widget
        self.in_layout = FlowLayout(self.in_content)
        self.warning_layout = FlowLayout(self.warning_content)
        self.error_layout = FlowLayout(self.error_content)
        
        # Set content widgets to scroll areas
        self.in_scroll.setWidget(self.in_content)
        self.warning_scroll.setWidget(self.warning_content)
        self.error_scroll.setWidget(self.error_content)
        
        # Set layouts for tabs
        in_tab_layout = QVBoxLayout(self.in_tab)
        in_tab_layout.setContentsMargins(0, 0, 0, 0)
        in_tab_layout.addWidget(self.in_scroll)
        
        warning_tab_layout = QVBoxLayout(self.warning_tab)
        warning_tab_layout.setContentsMargins(0, 0, 0, 0)
        warning_tab_layout.addWidget(self.warning_scroll)
        
        error_tab_layout = QVBoxLayout(self.error_tab)
        error_tab_layout.setContentsMargins(0, 0, 0, 0)
        error_tab_layout.addWidget(self.error_scroll)
        
        # Add tabs to tab widget with custom colors
        self.tab_widget.addTab(self.in_tab, "Done")
        self.tab_widget.setTabToolTip(0, "Successfully processed URLs")
        
        self.tab_widget.addTab(self.warning_tab, "Warning")
        self.tab_widget.setTabToolTip(1, "URLs processed with warnings")
        
        self.tab_widget.addTab(self.error_tab, "Error")
        self.tab_widget.setTabToolTip(2, "URLs that failed to process")
        
        # Style the tabs with colors
        self.tab_widget.tabBar().setTabTextColor(0, QColor("#00FF00"))  # Green
        self.tab_widget.tabBar().setTabTextColor(1, QColor("#FFFF00"))  # Yellow
        self.tab_widget.tabBar().setTabTextColor(2, QColor("#FF0000"))  # Red
        
        # Add tab widget to parent layout
        parent_layout.addWidget(self.tab_widget, 3)  # 3 parts for tab widget (left side)
    
    def create_data_analysis(self, parent_layout):
        # Create widget for data analysis
        self.data_analysis = QWidget()
        data_layout = QVBoxLayout(self.data_analysis)
        data_layout.setSpacing(10)
        
        # Add "done/total" counter at the top
        counter_layout = QHBoxLayout()
        self.done_total_label = QLabel("Processing: 0/0")
        self.done_total_label.setObjectName("data_header")
        counter_layout.addWidget(self.done_total_label)
        counter_layout.addStretch(1)
        data_layout.addLayout(counter_layout)
        
        # Add a separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: #333333;")
        data_layout.addWidget(separator)
        
        # Add results table
        table_label = QLabel("Plugin Results:")
        table_label.setObjectName("data_header")
        data_layout.addWidget(table_label)
        
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(3)  # Name, Value, Description
        self.results_table.setHorizontalHeaderLabels(["Field", "Value", "Description"])
        self.results_table.horizontalHeader().setStretchLastSection(True)
        self.results_table.setColumnWidth(0, 150)  # Set width for Field column
        self.results_table.setColumnWidth(1, 200)  # Set width for Value column
        
        data_layout.addWidget(self.results_table, 1)  # Add stretch factor of 1
        
        # Add data analysis widget to parent layout
        parent_layout.addWidget(self.data_analysis, 2)  # 2 parts for data analysis (right side)
    
    def add_url_to_in_tab(self, url, num=0):
        """Add a URL to the In tab (green)"""
        label = QLabel(url)
        label.setObjectName("in_tab_label")
        label.setFixedHeight(18)  # Set fixed height
        label.setWordWrap(False)  # Prevent word wrapping
        label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)  # Align text properly
        self.in_layout.addWidget(label)
        if num == 0:
            self.tab_widget.setTabText(0, "Done")
        else:
            self.tab_widget.setTabText(0, "Done "+str(num))

    def add_url_to_warning_tab(self, url, num=0):
        """Add a URL to the Warning tab (yellow)"""
        label = QLabel(url)
        label.setObjectName("warning_tab_label")
        label.setFixedHeight(18)  # Set fixed height
        label.setWordWrap(False)  # Prevent word wrapping
        label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)  # Align text properly
        self.warning_layout.addWidget(label)
        if num == 0:
            self.tab_widget.setTabText(1, "Warning")
        else:
            self.tab_widget.setTabText(1, "Warning "+str(num))

    def add_url_to_error_tab(self, url, num=0):
        """Add a URL to the Error tab (red)"""
        label = QLabel(url)
        label.setObjectName("error_tab_label")
        label.setFixedHeight(18)  # Set fixed height
        label.setWordWrap(False)  # Prevent word wrapping
        label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)  # Align text properly
        self.error_layout.addWidget(label)
        if num == 0:
            self.tab_widget.setTabText(2, "Error")
        else:
            self.tab_widget.setTabText(2, "Error "+str(num))
            
    def select_button_by_sender(self, button):
        """
        Handle button clicks and select the appropriate button.
        This version links Selenium Mode and Ulixee Hero Mode rows.
        """
        row_title = button.property("row_title")
        option = button.property("option")
        
        # Special handling for Selenium and Ulixee rows
        if row_title == "Selenium Mode":
            # First, deselect all buttons in Ulixee Hero Mode
            self.deselect_all_buttons("Ulixee Hero Mode")
            self.deselect_all_buttons("Playwright")
            # Then select the button in Selenium Mode
            self.select_button(row_title, option)
        elif row_title == "Ulixee Hero Mode":
            # First, deselect all buttons in Selenium Mode
            self.deselect_all_buttons("Selenium Mode")
            self.deselect_all_buttons("Playwright")
            # Then select the button in Ulixee Hero Mode
            self.select_button(row_title, option)
        elif row_title == "Playwright":
            # First, deselect all buttons in Selenium Mode
            self.deselect_all_buttons("Selenium Mode")
            self.deselect_all_buttons("Ulixee Hero Mode")
            # Then select the button in Ulixee Hero Mode
            self.select_button(row_title, option)
        else:
            # For other rows, just select the button normally
            self.select_button(row_title, option)
    
    def show_message_dialog(self, message):
        """
        Shows a styled message dialog with the same dark theme as the main application.
        
        Parameters:
        message (str): The message to display in the dialog
        """
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QFont
        
        # Create dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Message")
        dialog.setMinimumWidth(350)
        dialog.setWindowFlags(dialog.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        # Create layout
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Create message label
        message_label = QLabel(message)
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setWordWrap(True)
        
        # Set font for message
        font = QFont()
        font.setPointSize(12)
        message_label.setFont(font)
        
        # Add message to layout
        layout.addWidget(message_label)
        
        # Create button layout
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 10, 0, 0)
        
        # Add spacer to center the button
        button_layout.addStretch()
        
        # Create OK button
        ok_button = QPushButton("OK")
        ok_button.setMinimumWidth(100)
        ok_button.setMinimumHeight(30)
        ok_button.setCursor(Qt.PointingHandCursor)
        ok_button.clicked.connect(dialog.accept)
        
        # Add button to layout
        button_layout.addWidget(ok_button)
        button_layout.addStretch()
        
        # Add button layout to main layout
        layout.addLayout(button_layout)
        
        # Style the dialog
        dialog.setStyleSheet("""
            QDialog {
                background-color: #1E1E1E;
                border: 2px solid #444444;
                border-radius: 10px;
            }
            QLabel {
                color: #FF6600;
                font-weight: bold;
            }
            QPushButton {
                background-color: #333333;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                padding: 8px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #444444;
            }
            QPushButton:pressed {
                background-color: #FF6600;
                color: #000000;
            }
        """)
        
        # Show dialog
        dialog.exec_()

    def deselect_all_buttons(self, row_title):
        """Deselect all buttons in a specific row"""
        for button in self.button_groups[row_title]:
            button.setProperty("class", "")
            button.setStyleSheet("")
        
        # Update the selected buttons tracker
        self.selected_buttons[row_title] = None
    
    def select_button(self, row_title, option):
        # Update all buttons in this row
        for button in self.button_groups[row_title]:
            if button.text() == option:
                button.setProperty("class", "selected")
                button.setStyleSheet("background-color: #FF6600; color: #000000; border-radius: 8px;")
                self.selected_buttons[row_title] = option
            else:
                button.setProperty("class", "")
                button.setStyleSheet("")
        
        # Special handling for human behavior affecting intensity buttons
        if row_title == "Human Behavior":
            self.update_intensity_buttons()
    
    def update_intensity_buttons(self):
        # Enable/disable intensity buttons based on human behavior
        intensity_buttons = self.button_groups["Behavior Intensity"]
        enable = self.selected_buttons["Human Behavior"] == "true"
        
        for button in intensity_buttons:
            button.setEnabled(enable)
            
        # If disabled and something was previously selected, keep selection visually
        if not enable:
            # Deselect all intensity buttons visually but keep the selection in memory
            for button in intensity_buttons:
                button.setProperty("class", "")
                button.setStyleSheet("background-color: #2A2A2A; color: #666666; border-radius: 8px;")
        else:
            # Re-apply selection to the previously selected button if any
            selected_intensity = self.selected_buttons["Behavior Intensity"]
            if selected_intensity:
                for button in intensity_buttons:
                    if button.text() == selected_intensity:
                        button.setProperty("class", "selected")
                        button.setStyleSheet("background-color: #FF6600; color: #000000; border-radius: 8px;")
            else:
                # If there was no previous selection, select the first button
                if intensity_buttons:
                    self.select_button("Behavior Intensity", intensity_buttons[0].text())
    
    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select File", "", "All Files (*)"
        )
        if file_path:
            self.file_path_input.setText(file_path)
    
    def run_action(self):
        # Get all the selected options
        options = {k: v for k, v in self.selected_buttons.items() if v is not None}
        
        # If behavior is false, set intensity to N/A
        if options.get("Human Behavior") == "false":
            options["Behavior Intensity"] = "N/A"
        
        # Get file paths from the text edit
        file_paths = self.file_path_input.toPlainText().strip()
        
        # Example: Add some test URLs to tabs instead of console output
        if file_paths:
            urls = file_paths.split('\n')
            for i, url in enumerate(urls):
                if url.strip():
                    # Just for demonstration: distribute URLs across tabs
                    if i % 3 == 0:
                        self.add_url_to_in_tab(url.strip())
                    elif i % 3 == 1:
                        self.add_url_to_warning_tab(url.strip())
                    else:
                        self.add_url_to_error_tab(url.strip())
        
    def cancel_scraping(self):
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DarkThemeApp()
    sys.exit(app.exec_())