import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QTableWidget, 
                            QTableWidgetItem, QDialog, QLineEdit, QComboBox, 
                            QTextEdit, QSpinBox, QMessageBox, QTabWidget,
                            QDateEdit, QCompleter, QFrame, QToolBar,
                            QFileDialog, QHeaderView)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont, QIcon, QPainter, QPalette, QColor, QAction, QPixmap
from PySide6.QtCharts import QChart, QChartView, QPieSeries
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import pandas as pd

# Get the user's AppData folder path
app_data_path = os.path.join(os.getenv('APPDATA'), 'THRUZIM Inventory')
os.makedirs(app_data_path, exist_ok=True)

# Update database path to use AppData
DB_PATH = os.path.join(app_data_path, 'inventory.db')

# Get the application directory for resources
APP_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(APP_DIR, "thruzim .png")

# Database setup
Base = declarative_base()
engine = create_engine(f"sqlite:///{DB_PATH}")
Session = sessionmaker(bind=engine)

# Create all tables if they don't exist
Base.metadata.create_all(engine)

class Item(Base):
    __tablename__ = 'item'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    model = Column(String(100))
    serial_number = Column(String(100), unique=True)
    description = Column(Text)
    project_category = Column(String(100))
    quantity = Column(Integer, default=0)
    supplier = Column(String(100))
    storage_location = Column(String(50))
    date_added = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default="Active")
    notes = Column(Text)
    movements = relationship("StockMovement", back_populates="item")

class StockMovement(Base):
    __tablename__ = 'stock_movement'
    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, ForeignKey('item.id'), nullable=False)
    movement_type = Column(String(20), nullable=False)
    from_location = Column(String(50))
    to_location = Column(String(50))
    project_category = Column(String(100))
    quantity = Column(Integer, nullable=False)
    status = Column(String(20))
    date = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text)
    item = relationship("Item", back_populates="movements")

class AddItemDialog(QDialog):
    def __init__(self, parent=None, item=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Item")
        self.setModal(True)
        self.setup_ui()
        if item:
            self.populate_form(item)

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Name:"))
        self.name_input = QLineEdit()
        self.name_input.setMinimumWidth(400)
        self.name_input.textChanged.connect(lambda text: self.name_input.setText(text.title()))
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)

        # Serial Number
        serial_layout = QHBoxLayout()
        serial_layout.addWidget(QLabel("Serial Number:"))
        self.serial_input = QLineEdit()
        self.serial_input.setMinimumWidth(400)
        serial_layout.addWidget(self.serial_input)
        layout.addLayout(serial_layout)

        # Project Category
        category_layout = QHBoxLayout()
        category_layout.addWidget(QLabel("Project Category:"))
        self.category_input = QLineEdit()
        self.category_input.setMinimumWidth(400)
        self.category_input.textChanged.connect(lambda text: self.category_input.setText(text.title()))
        category_layout.addWidget(self.category_input)
        layout.addLayout(category_layout)

        # Description
        desc_layout = QVBoxLayout()
        desc_layout.addWidget(QLabel("Description:"))
        self.desc_input = QTextEdit()
        self.desc_input.setMinimumHeight(100)
        desc_layout.addWidget(self.desc_input)
        layout.addLayout(desc_layout)

        # Notes
        notes_layout = QVBoxLayout()
        notes_layout.addWidget(QLabel("Notes:"))
        self.notes_input = QTextEdit()
        self.notes_input.setMinimumHeight(100)
        notes_layout.addWidget(self.notes_input)
        layout.addLayout(notes_layout)

        # Quantity
        quantity_layout = QHBoxLayout()
        quantity_layout.addWidget(QLabel("Quantity:"))
        self.quantity_input = QSpinBox()
        self.quantity_input.setMinimum(0)
        self.quantity_input.setMinimumWidth(400)
        quantity_layout.addWidget(self.quantity_input)
        layout.addLayout(quantity_layout)

        # Supplier
        supplier_layout = QHBoxLayout()
        supplier_layout.addWidget(QLabel("Supplier:"))
        self.supplier_input = QLineEdit()
        self.supplier_input.setMinimumWidth(400)
        self.supplier_input.textChanged.connect(lambda text: self.supplier_input.setText(text.title()))
        supplier_layout.addWidget(self.supplier_input)
        layout.addLayout(supplier_layout)

        # Storage Location
        location_layout = QHBoxLayout()
        location_layout.addWidget(QLabel("Storage Location:"))
        self.location_input = QComboBox()
        self.location_input.addItems(["Data Office", "Stores", "Container", "Field Work"])
        self.location_input.setMinimumWidth(400)
        location_layout.addWidget(self.location_input)
        layout.addLayout(location_layout)

        # Date Added
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Date Added:"))
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setMinimumWidth(400)
        date_layout.addWidget(self.date_input)
        layout.addLayout(date_layout)

        # Buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def populate_form(self, item):
        self.name_input.setText(item.name)
        self.serial_input.setText(item.serial_number)
        self.category_input.setText(item.project_category)
        self.desc_input.setText(item.description)
        self.quantity_input.setValue(item.quantity)
        self.supplier_input.setText(item.supplier)
        self.location_input.setCurrentText(item.storage_location)
        if isinstance(item.date_added, datetime):
            self.date_input.setDate(QDate(item.date_added.year, item.date_added.month, item.date_added.day))
        else:
            self.date_input.setDate(QDate.currentDate())
        self.notes_input.setText(item.notes)

    def get_item_data(self):
        return {
            'name': self.name_input.text(),
            'serial_number': self.serial_input.text(),
            'project_category': self.category_input.text(),
            'description': self.desc_input.toPlainText(),
            'quantity': self.quantity_input.value(),
            'supplier': self.supplier_input.text(),
            'storage_location': self.location_input.currentText(),
            'date_added': self.date_input.date().toPython(),
            'notes': self.notes_input.toPlainText()
        }

class StockMovementDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Record Stock Movement")
        self.setModal(True)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Item (with autocomplete)
        item_layout = QHBoxLayout()
        item_layout.addWidget(QLabel("Item:"))
        self.item_input = QLineEdit()
        self.item_input.setPlaceholderText("Start typing to search items...")
        self.item_input.setMinimumWidth(400)
        item_layout.addWidget(self.item_input)
        layout.addLayout(item_layout)

        # Movement Type
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Movement Type:"))
        self.type_input = QComboBox()
        self.type_input.addItems(["In", "Out", "Transferred"])
        self.type_input.setMinimumWidth(400)
        type_layout.addWidget(self.type_input)
        layout.addLayout(type_layout)

        # From Location
        from_layout = QHBoxLayout()
        from_layout.addWidget(QLabel("From:"))
        self.from_input = QComboBox()
        self.from_input.addItems(["Data Office", "Stores", "Container", "Field Work"])
        self.from_input.setMinimumWidth(400)
        from_layout.addWidget(self.from_input)
        layout.addLayout(from_layout)

        # To Location
        to_layout = QHBoxLayout()
        to_layout.addWidget(QLabel("To:"))
        self.to_input = QComboBox()
        self.to_input.addItems(["Data Office", "Stores", "Container", "Field Work"])
        self.to_input.setMinimumWidth(400)
        to_layout.addWidget(self.to_input)
        layout.addLayout(to_layout)

        # Project Category
        category_layout = QHBoxLayout()
        category_layout.addWidget(QLabel("Project Category:"))
        self.category_input = QLineEdit()
        self.category_input.setMinimumWidth(400)
        self.category_input.textChanged.connect(lambda text: self.category_input.setText(text.title()))
        category_layout.addWidget(self.category_input)
        layout.addLayout(category_layout)

        # Quantity
        quantity_layout = QHBoxLayout()
        quantity_layout.addWidget(QLabel("Quantity:"))
        self.quantity_input = QSpinBox()
        self.quantity_input.setMinimum(1)
        self.quantity_input.setMinimumWidth(400)
        quantity_layout.addWidget(self.quantity_input)
        layout.addLayout(quantity_layout)

        # Status
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("Status:"))
        self.status_input = QComboBox()
        self.status_input.addItems(["Active", "Inactive", "Damaged"])
        self.status_input.setMinimumWidth(400)
        status_layout.addWidget(self.status_input)
        layout.addLayout(status_layout)

        # Date
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Date:"))
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setMinimumWidth(400)
        date_layout.addWidget(self.date_input)
        layout.addLayout(date_layout)

        # Notes
        notes_layout = QVBoxLayout()
        notes_layout.addWidget(QLabel("Notes:"))
        self.notes_input = QTextEdit()
        self.notes_input.setMinimumHeight(100)
        notes_layout.addWidget(self.notes_input)
        layout.addLayout(notes_layout)

        # Buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        # Setup autocomplete for items
        self.setup_item_autocomplete()

    def setup_item_autocomplete(self):
        session = Session()
        items = session.query(Item).all()
        item_list = []
        for item in items:
            item_list.append(f"{item.name} - {item.serial_number} - {item.project_category}")
        session.close()

        completer = QCompleter(item_list)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.item_input.setCompleter(completer)

        # Connect signal to handle item selection
        self.item_input.textChanged.connect(self.handle_item_selection)

    def handle_item_selection(self, text):
        if text and " - " in text:
            parts = text.split(" - ")
            if len(parts) >= 3:
                self.category_input.setText(parts[2])  # Set project category

    def get_movement_data(self):
        return {
            'item_name': self.item_input.text().split(" - ")[0] if " - " in self.item_input.text() else self.item_input.text(),
            'movement_type': self.type_input.currentText(),
            'from_location': self.from_input.currentText(),
            'to_location': self.to_input.currentText(),
            'project_category': self.category_input.text(),
            'quantity': self.quantity_input.value(),
            'status': self.status_input.currentText(),
            'date': self.date_input.date().toPython(),
            'notes': self.notes_input.toPlainText()
        }

class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("THRUZIM Inventory Management - Login")
        self.setModal(True)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Logo
        logo_label = QLabel()
        pixmap = QPixmap(LOGO_PATH)  # Using absolute path
        scaled_pixmap = pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        logo_label.setPixmap(scaled_pixmap)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo_label)
        
        # Title
        title = QLabel("THRUZIM Inventory Management")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Username
        username_layout = QVBoxLayout()
        username_label = QLabel("Username:")
        username_label.setStyleSheet("color: #2c3e50; font-weight: bold;")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter username")
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_input)
        layout.addLayout(username_layout)
        
        # Password
        password_layout = QVBoxLayout()
        password_label = QLabel("Password:")
        password_label.setStyleSheet("color: #2c3e50; font-weight: bold;")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        layout.addLayout(password_layout)
        
        # Login button
        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self.verify_credentials)
        layout.addWidget(login_btn)
        
        self.setLayout(layout)
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f6fa;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #e0e0e0;
                border-radius: 5px;
                background-color: white;
                min-height: 30px;
                min-width: 250px;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
                min-height: 35px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
    def verify_credentials(self):
        username = self.username_input.text()
        password = self.password_input.text()
        
        if username == "thruzim" and password == "admin2030":
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "Invalid username or password")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("THRUZIM Inventory Management")
        self.setMinimumSize(1400, 800)
        
        # Show login dialog
        login_dialog = LoginDialog(self)
        if login_dialog.exec() != QDialog.DialogCode.Accepted:
            sys.exit()
            
        self.setup_ui()
        
    def setup_ui(self):
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Create toolbar
        toolbar = QToolBar()
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        toolbar.setStyleSheet("""
            QToolBar {
                background-color: #ffffff;
                border-bottom: 1px solid #e0e0e0;
                padding: 8px;
            }
        """)

        # Add logo to toolbar
        logo_label = QLabel()
        pixmap = QPixmap(LOGO_PATH)  # Using absolute path
        scaled_pixmap = pixmap.scaled(30, 30, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        logo_label.setPixmap(scaled_pixmap)
        toolbar.addWidget(logo_label)

        # Add toolbar actions
        search_action = QAction("Search", self)
        search_action.triggered.connect(self.show_search_dialog)
        toolbar.addAction(search_action)

        export_action = QAction("Export", self)
        export_action.triggered.connect(self.export_data)
        toolbar.addAction(export_action)

        # Create main content area
        content_widget = QWidget()
        layout.addWidget(content_widget)
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)

        # Left side - Main content
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        # Create tab widget
        tabs = QTabWidget()
        left_layout.addWidget(tabs)

        # Dashboard tab
        dashboard_tab = QWidget()
        dashboard_layout = QVBoxLayout(dashboard_tab)
        
        # Recent items table
        recent_label = QLabel("Recently Added Items")
        recent_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        recent_label.setStyleSheet("color: #2c3e50; margin-top: 20px;")
        dashboard_layout.addWidget(recent_label)
        
        self.recent_items_table = QTableWidget()
        self.recent_items_table.setColumnCount(7)
        self.recent_items_table.setHorizontalHeaderLabels([
            "Name", "Serial Number", "Project Name", 
            "Quantity", "Location", "Description", "Date"
        ])
        self.recent_items_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        dashboard_layout.addWidget(self.recent_items_table)

        # Items tab
        items_tab = QWidget()
        items_layout = QVBoxLayout(items_tab)
        
        # Add toolbar for items tab
        items_toolbar = QHBoxLayout()
        items_toolbar.setContentsMargins(0, 0, 0, 10)
        
        # Search box
        self.items_search = QLineEdit()
        self.items_search.setPlaceholderText("Search items...")
        self.items_search.setMinimumWidth(300)
        self.items_search.textChanged.connect(self.filter_items)
        items_toolbar.addWidget(self.items_search)
        
        # Sort dropdown
        self.items_sort = QComboBox()
        self.items_sort.addItems(["Date Added", "Project Name", "Name"])
        self.items_sort.currentTextChanged.connect(self.sort_items)
        items_toolbar.addWidget(self.items_sort)
        
        # Export button
        export_btn = QPushButton("Export")
        export_btn.clicked.connect(self.export_data)
        items_toolbar.addWidget(export_btn)
        
        # Add item button
        add_item_btn = QPushButton("Add Item")
        add_item_btn.clicked.connect(self.show_add_item_dialog)
        items_toolbar.addWidget(add_item_btn)
        
        items_layout.addLayout(items_toolbar)
        
        # Items table
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(7)
        self.items_table.setHorizontalHeaderLabels([
            "Name", "Serial Number", "Project Name", 
            "Quantity", "Location", "Description", "Date"
        ])
        self.items_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        items_layout.addWidget(self.items_table)

        # Stock Movement tab
        movement_tab = QWidget()
        movement_layout = QVBoxLayout(movement_tab)
        
        # Add toolbar for movement tab
        movement_toolbar = QHBoxLayout()
        movement_toolbar.setContentsMargins(0, 0, 0, 10)
        
        # Search box
        self.movement_search = QLineEdit()
        self.movement_search.setPlaceholderText("Search movements...")
        self.movement_search.setMinimumWidth(300)
        self.movement_search.textChanged.connect(self.filter_movements)
        movement_toolbar.addWidget(self.movement_search)
        
        # Sort dropdown
        self.movement_sort = QComboBox()
        self.movement_sort.addItems(["Date", "Item", "Type"])
        self.movement_sort.currentTextChanged.connect(self.sort_movements)
        movement_toolbar.addWidget(self.movement_sort)
        
        # Export button
        export_btn = QPushButton("Export")
        export_btn.clicked.connect(self.export_data)
        movement_toolbar.addWidget(export_btn)
        
        # Record movement button
        record_movement_btn = QPushButton("Record Movement")
        record_movement_btn.clicked.connect(self.show_record_movement_dialog)
        movement_toolbar.addWidget(record_movement_btn)
        
        movement_layout.addLayout(movement_toolbar)
        
        # Movement table
        self.movement_table = QTableWidget()
        self.movement_table.setColumnCount(10)
        self.movement_table.setHorizontalHeaderLabels([
            "Date", "Item", "Serial Number", "Type", "From", "To", 
            "Project Name", "Quantity", "Status", "Comments"
        ])
        self.movement_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        movement_layout.addWidget(self.movement_table)

        # Add tabs
        tabs.addTab(dashboard_tab, "Dashboard")
        tabs.addTab(items_tab, "Items")
        tabs.addTab(movement_tab, "Stock Movement")

        # Right side - Quick actions (only for dashboard)
        self.right_widget = QWidget()
        self.right_widget.setMaximumWidth(300)
        right_layout = QVBoxLayout(self.right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)

        # Quick actions card
        actions_card = QFrame()
        actions_card.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        actions_layout = QVBoxLayout(actions_card)

        # Quick actions title
        actions_title = QLabel("Quick Actions")
        actions_title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        actions_title.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
        actions_layout.addWidget(actions_title)

        # Add action buttons
        add_item_btn = QPushButton("Add New Item")
        add_item_btn.clicked.connect(self.show_add_item_dialog)
        actions_layout.addWidget(add_item_btn)

        record_movement_btn = QPushButton("Record Movement")
        record_movement_btn.clicked.connect(self.show_record_movement_dialog)
        actions_layout.addWidget(record_movement_btn)

        search_btn = QPushButton("Search Items")
        search_btn.clicked.connect(self.show_search_dialog)
        actions_layout.addWidget(search_btn)

        actions_layout.addStretch()
        right_layout.addWidget(actions_card)
        right_layout.addStretch()

        # Add widgets to main layout
        content_layout.addWidget(left_widget, stretch=7)
        content_layout.addWidget(self.right_widget, stretch=3)

        # Set style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f6fa;
            }
            QLabel {
                color: #2c3e50;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 5px;
                font-weight: bold;
                margin: 5px 0;
                min-height: 25px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
            }
            QTableWidget::item {
                padding: 6px;
            }
            QHeaderView::section {
                background-color: #3498db;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
            QTabWidget::pane {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #f5f6fa;
                padding: 8px 16px;
                border: 1px solid #e0e0e0;
                border-bottom: none;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: none;
                font-weight: bold;
            }
            QComboBox {
                padding: 6px;
                border: 1px solid #e0e0e0;
                border-radius: 5px;
                background-color: white;
                min-height: 25px;
                min-width: 150px;
            }
            QLineEdit, QTextEdit, QSpinBox {
                padding: 6px;
                border: 1px solid #e0e0e0;
                border-radius: 5px;
                background-color: white;
                min-height: 25px;
                min-width: 150px;
            }
            QDialog {
                min-width: 600px;
            }
            QCompleter {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        
        # Load data after UI is set up
        self.load_data()

        # Connect tab change signal
        tabs.currentChanged.connect(self.on_tab_changed)

        # Add content layout to main widget
        central_widget.setLayout(content_layout)

    def load_data(self):
        session = Session()
        
        # Load items
        items = session.query(Item).all()
        self.items_table.setRowCount(len(items))
        for i, item in enumerate(items):
            self.items_table.setItem(i, 0, QTableWidgetItem(item.name))
            self.items_table.setItem(i, 1, QTableWidgetItem(item.serial_number))
            self.items_table.setItem(i, 2, QTableWidgetItem(item.project_category))
            self.items_table.setItem(i, 3, QTableWidgetItem(str(item.quantity)))
            self.items_table.setItem(i, 4, QTableWidgetItem(item.storage_location))
            self.items_table.setItem(i, 5, QTableWidgetItem(item.description))
            self.items_table.setItem(i, 6, QTableWidgetItem(item.date_added.strftime("%Y-%m-%d")))

            # Add actions dropdown
            actions_combo = QComboBox()
            actions_combo.addItems(["Edit", "Delete"])
            actions_combo.currentTextChanged.connect(lambda text, item=item: self.handle_action(text, item))
            actions_combo.setMaximumWidth(80)  # Set maximum width for actions dropdown
            self.items_table.setCellWidget(i, 7, actions_combo)

        # Load recent items (last 5)
        recent_items = session.query(Item).order_by(Item.date_added.desc()).limit(5).all()
        self.recent_items_table.setRowCount(len(recent_items))
        for i, item in enumerate(recent_items):
            self.recent_items_table.setItem(i, 0, QTableWidgetItem(item.name))
            self.recent_items_table.setItem(i, 1, QTableWidgetItem(item.serial_number))
            self.recent_items_table.setItem(i, 2, QTableWidgetItem(item.project_category))
            self.recent_items_table.setItem(i, 3, QTableWidgetItem(str(item.quantity)))
            self.recent_items_table.setItem(i, 4, QTableWidgetItem(item.storage_location))
            self.recent_items_table.setItem(i, 5, QTableWidgetItem(item.description))
            self.recent_items_table.setItem(i, 6, QTableWidgetItem(item.date_added.strftime("%Y-%m-%d")))

        # Load movements
        movements = session.query(StockMovement).order_by(StockMovement.date.desc()).all()
        self.movement_table.setRowCount(len(movements))
        for i, movement in enumerate(movements):
            self.movement_table.setItem(i, 0, QTableWidgetItem(movement.date.strftime("%Y-%m-%d")))
            self.movement_table.setItem(i, 1, QTableWidgetItem(movement.item.name))
            self.movement_table.setItem(i, 2, QTableWidgetItem(movement.item.serial_number))
            self.movement_table.setItem(i, 3, QTableWidgetItem(movement.movement_type))
            self.movement_table.setItem(i, 4, QTableWidgetItem(movement.from_location))
            self.movement_table.setItem(i, 5, QTableWidgetItem(movement.to_location))
            self.movement_table.setItem(i, 6, QTableWidgetItem(movement.project_category))
            self.movement_table.setItem(i, 7, QTableWidgetItem(str(movement.quantity)))
            
            # Add status dropdown
            status_combo = QComboBox()
            status_combo.addItems(["Active", "Inactive", "Damaged"])
            status_combo.setCurrentText(movement.status)
            status_combo.currentTextChanged.connect(lambda text, m=movement: self.update_movement_status(text, m))
            status_combo.setMaximumWidth(60)  # Make dropdown even smaller
            status_combo.setStyleSheet("""
                QComboBox {
                    padding: 2px;
                    border: 1px solid #e0e0e0;
                    border-radius: 3px;
                    background-color: white;
                    min-height: 20px;
                    font-size: 11px;
                }
            """)
            self.movement_table.setCellWidget(i, 8, status_combo)
            
            self.movement_table.setItem(i, 9, QTableWidgetItem(movement.notes))

        session.close()

    def handle_action(self, action, item):
        if action == "Edit":
            self.edit_item(item)
        elif action == "Delete":
            self.delete_item(item)
        # Reset the combo box
        sender = self.sender()
        if sender:
            sender.setCurrentText("")

    def edit_item(self, item):
        dialog = AddItemDialog(self, item)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                session = Session()
                item_data = dialog.get_item_data()
                for key, value in item_data.items():
                    setattr(item, key, value)
                session.commit()
                self.load_data()
                QMessageBox.information(self, "Success", "Item updated successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error updating item: {str(e)}")
            finally:
                session.close()

    def delete_item(self, item):
        reply = QMessageBox.question(self, "Confirm Delete", 
                                   "Are you sure you want to delete this item?",
                                   QMessageBox.StandardButton.Yes | 
                                   QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                session = Session()
                session.delete(item)
                session.commit()
                self.load_data()
                QMessageBox.information(self, "Success", "Item deleted successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error deleting item: {str(e)}")
            finally:
                session.close()

    def show_search_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Search Items")
        dialog.setModal(True)
        layout = QVBoxLayout(dialog)
        
        # Search type selector
        search_type_layout = QHBoxLayout()
        search_type_layout.addWidget(QLabel("Search by:"))
        search_type = QComboBox()
        search_type.addItems(["Name", "Date", "Project Name", "Serial Number"])
        search_type_layout.addWidget(search_type)
        layout.addLayout(search_type_layout)
        
        search_input = QLineEdit()
        search_input.setPlaceholderText("Enter search term...")
        layout.addWidget(search_input)
        
        # Add search results table
        results_table = QTableWidget()
        results_table.setColumnCount(7)
        results_table.setHorizontalHeaderLabels([
            "Name", "Serial Number", "Project Name", 
            "Quantity", "Location", "Description", "Notes"
        ])
        layout.addWidget(results_table)
        
        # Add search functionality
        def perform_search():
            query = search_input.text().lower()
            search_by = search_type.currentText()
            session = Session()
            
            if search_by == "Name":
                items = session.query(Item).filter(Item.name.ilike(f'%{query}%')).all()
            elif search_by == "Date":
                try:
                    search_date = datetime.strptime(query, "%Y-%m-%d").date()
                    items = session.query(Item).filter(func.date(Item.date_added) == search_date).all()
                except ValueError:
                    items = []
            elif search_by == "Project Name":
                items = session.query(Item).filter(Item.project_category.ilike(f'%{query}%')).all()
            else:  # Serial Number
                items = session.query(Item).filter(Item.serial_number.ilike(f'%{query}%')).all()
            
            results_table.setRowCount(len(items))
            for i, item in enumerate(items):
                results_table.setItem(i, 0, QTableWidgetItem(item.name))
                results_table.setItem(i, 1, QTableWidgetItem(item.serial_number))
                results_table.setItem(i, 2, QTableWidgetItem(item.project_category))
                results_table.setItem(i, 3, QTableWidgetItem(str(item.quantity)))
                results_table.setItem(i, 4, QTableWidgetItem(item.storage_location))
                results_table.setItem(i, 5, QTableWidgetItem(item.description))
                results_table.setItem(i, 6, QTableWidgetItem(item.notes))
            
            session.close()
        
        search_input.textChanged.connect(perform_search)
        
        dialog.exec()

    def export_data(self):
        try:
            session = Session()
            items = session.query(Item).all()
            movements = session.query(StockMovement).all()
            damaged_items = session.query(Item).filter(Item.status == "Damaged").all()
            
            # Convert items to DataFrame
            items_data = []
            for item in items:
                items_data.append({
                    'Name': item.name,
                    'Serial Number': item.serial_number,
                    'Project Name': item.project_category,
                    'Quantity': item.quantity,
                    'Location': item.storage_location,
                    'Description': item.description,
                    'Date Added': item.date_added.strftime("%Y-%m-%d"),
                    'Status': item.status
                })
            
            # Convert movements to DataFrame
            movements_data = []
            for movement in movements:
                movements_data.append({
                    'Date': movement.date.strftime("%Y-%m-%d"),
                    'Item': movement.item.name,
                    'Serial Number': movement.item.serial_number,
                    'Type': movement.movement_type,
                    'From': movement.from_location,
                    'To': movement.to_location,
                    'Project Name': movement.project_category,
                    'Quantity': movement.quantity,
                    'Status': movement.status,
                    'Comments': movement.notes
                })
            
            # Convert damaged items to DataFrame
            damaged_data = []
            for item in damaged_items:
                # Find the movement that marked this item as damaged
                damaged_movement = session.query(StockMovement).filter(
                    StockMovement.item_id == item.id,
                    StockMovement.status == "Damaged"
                ).first()
                
                damaged_data.append({
                    'Name': item.name,
                    'Serial Number': item.serial_number,
                    'Project Name': item.project_category,
                    'Location': item.storage_location,
                    'Description': item.description,
                    'Date Damaged': damaged_movement.date.strftime("%Y-%m-%d") if damaged_movement else "N/A",
                    'Comments': damaged_movement.notes if damaged_movement else "N/A"
                })
            
            items_df = pd.DataFrame(items_data)
            movements_df = pd.DataFrame(movements_data)
            damaged_df = pd.DataFrame(damaged_data)
            
            # Save to file
            file_name, _ = QFileDialog.getSaveFileName(
                self, "Export Data", "", "Excel Files (*.xlsx);;CSV Files (*.csv)"
            )
            
            if file_name:
                if file_name.endswith('.xlsx'):
                    with pd.ExcelWriter(file_name) as writer:
                        items_df.to_excel(writer, sheet_name='Inventory Items', index=False)
                        movements_df.to_excel(writer, sheet_name='Stock Movement', index=False)
                        if not damaged_df.empty:
                            damaged_df.to_excel(writer, sheet_name='Damaged Items', index=False)
                else:
                    items_df.to_csv(file_name.replace('.csv', '_items.csv'), index=False)
                    movements_df.to_csv(file_name.replace('.csv', '_movements.csv'), index=False)
                    if not damaged_df.empty:
                        damaged_df.to_csv(file_name.replace('.csv', '_damaged.csv'), index=False)
                QMessageBox.information(self, "Success", "Data exported successfully!")
            
            session.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error exporting data: {str(e)}")

    def filter_items(self):
        search_text = self.items_search.text().lower()
        for row in range(self.items_table.rowCount()):
            show_row = False
            for col in range(self.items_table.columnCount() - 1):  # Exclude actions column
                item = self.items_table.item(row, col)
                if item and search_text in item.text().lower():
                    show_row = True
                    break
            self.items_table.setRowHidden(row, not show_row)

    def filter_movements(self):
        search_text = self.movement_search.text().lower()
        for row in range(self.movement_table.rowCount()):
            show_row = False
            for col in range(self.movement_table.columnCount()):
                item = self.movement_table.item(row, col)
                if item and search_text in item.text().lower():
                    show_row = True
                    break
            self.movement_table.setRowHidden(row, not show_row)

    def sort_items(self, sort_by):
        session = Session()
        if sort_by == "Date Added":
            items = session.query(Item).order_by(Item.date_added.desc()).all()
        elif sort_by == "Name":
            items = session.query(Item).order_by(Item.name).all()
        else:
            items = session.query(Item).order_by(Item.project_category).all()
        
        self.items_table.setRowCount(len(items))
        for i, item in enumerate(items):
            self.items_table.setItem(i, 0, QTableWidgetItem(item.name))
            self.items_table.setItem(i, 1, QTableWidgetItem(item.serial_number))
            self.items_table.setItem(i, 2, QTableWidgetItem(item.project_category))
            self.items_table.setItem(i, 3, QTableWidgetItem(str(item.quantity)))
            self.items_table.setItem(i, 4, QTableWidgetItem(item.storage_location))
            self.items_table.setItem(i, 5, QTableWidgetItem(item.description))
            self.items_table.setItem(i, 6, QTableWidgetItem(item.date_added.strftime("%Y-%m-%d")))
            
            # Add actions dropdown
            actions_combo = QComboBox()
            actions_combo.addItems(["Edit", "Delete"])
            actions_combo.currentTextChanged.connect(lambda text, item=item: self.handle_action(text, item))
            self.items_table.setCellWidget(i, 7, actions_combo)
        
        session.close()

    def sort_movements(self, sort_by):
        session = Session()
        if sort_by == "Date":
            movements = session.query(StockMovement).order_by(StockMovement.date.desc()).all()
        elif sort_by == "Item":
            movements = session.query(StockMovement).order_by(Item.name).join(Item).all()
        else:  # Type
            movements = session.query(StockMovement).order_by(StockMovement.movement_type).all()
        
        self.movement_table.setRowCount(len(movements))
        for i, movement in enumerate(movements):
            self.movement_table.setItem(i, 0, QTableWidgetItem(movement.date.strftime("%Y-%m-%d")))
            self.movement_table.setItem(i, 1, QTableWidgetItem(movement.item.name))
            self.movement_table.setItem(i, 2, QTableWidgetItem(movement.item.serial_number))
            self.movement_table.setItem(i, 3, QTableWidgetItem(movement.movement_type))
            self.movement_table.setItem(i, 4, QTableWidgetItem(movement.from_location))
            self.movement_table.setItem(i, 5, QTableWidgetItem(movement.to_location))
            self.movement_table.setItem(i, 6, QTableWidgetItem(movement.project_category))
            self.movement_table.setItem(i, 7, QTableWidgetItem(str(movement.quantity)))
            self.movement_table.setItem(i, 8, QTableWidgetItem(movement.status))
            self.movement_table.setItem(i, 9, QTableWidgetItem(movement.notes))
        
        session.close()

    def show_add_item_dialog(self):
        dialog = AddItemDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                session = Session()
                new_item = Item(**dialog.get_item_data())
                session.add(new_item)
                session.commit()
                self.load_data()
                QMessageBox.information(self, "Success", "Item added successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error adding item: {str(e)}")
            finally:
                session.close()

    def show_record_movement_dialog(self):
        dialog = StockMovementDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                session = Session()
                movement_data = dialog.get_movement_data()
                
                # Find the item
                item = session.query(Item).filter(Item.name == movement_data['item_name']).first()
                if not item:
                    raise Exception("Item not found")

                # Create movement record
                movement = StockMovement(
                    item_id=item.id,
                    movement_type=movement_data['movement_type'],
                    from_location=movement_data['from_location'],
                    to_location=movement_data['to_location'],
                    project_category=movement_data['project_category'],
                    quantity=movement_data['quantity'],
                    status=movement_data['status'],
                    date=movement_data['date'],
                    notes=movement_data['notes']
                )

                # Update item quantity based on movement type and locations
                if movement_data['movement_type'] == 'In':
                    if movement_data['from_location'] == 'Field Work':
                        item.quantity += movement_data['quantity']
                elif movement_data['movement_type'] == 'Out':
                    if movement_data['to_location'] == 'Field Work':
                        item.quantity -= movement_data['quantity']
                elif movement_data['movement_type'] == 'Transferred':
                    if movement_data['from_location'] in ['Stores', 'Container', 'Data Office'] and movement_data['to_location'] == 'Field Work':
                        item.quantity -= movement_data['quantity']
                    elif movement_data['from_location'] == 'Field Work' and movement_data['to_location'] in ['Stores', 'Container', 'Data Office']:
                        item.quantity += movement_data['quantity']

                # Update item location
                item.storage_location = movement_data['to_location']

                session.add(movement)
                session.commit()
                self.load_data()
                QMessageBox.information(self, "Success", "Movement recorded successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error recording movement: {str(e)}")
            finally:
                session.close()

    def on_tab_changed(self, index):
        # Show quick actions only on dashboard tab (index 0)
        self.right_widget.setVisible(index == 0)

    def update_movement_status(self, new_status, movement):
        try:
            session = Session()
            movement.status = new_status
            session.commit()
            
            # If status is changed to Damaged, update the item status as well
            if new_status == "Damaged":
                movement.item.status = "Damaged"
                session.commit()
                
            session.close()
            self.load_data()  # Reload data to reflect changes
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error updating status: {str(e)}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec()) 