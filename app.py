import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QTableWidget, 
                            QTableWidgetItem, QDialog, QLineEdit, QComboBox, 
                            QTextEdit, QSpinBox, QMessageBox, QTabWidget,
                            QDateEdit, QCompleter, QFrame, QToolBar,
                            QFileDialog, QHeaderView)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont, QIcon, QPainter, QPalette, QColor, QAction
from PySide6.QtCharts import QChart, QChartView, QPieSeries
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import pandas as pd

# Database setup
Base = declarative_base()
engine = create_engine('sqlite:///inventory.db')
Session = sessionmaker(bind=engine)

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

# Create all tables
Base.metadata.drop_all(engine)  # Drop existing tables
Base.metadata.create_all(engine)  # Create new tables

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
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)

        # Model
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("Model:"))
        self.model_input = QLineEdit()
        self.model_input.setMinimumWidth(400)
        model_layout.addWidget(self.model_input)
        layout.addLayout(model_layout)

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
        self.model_input.setText(item.model)
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

    def get_item_data(self):
        return {
            'name': self.name_input.text(),
            'model': self.model_input.text(),
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
            item_list.append(f"{item.name} - {item.serial_number} - {item.model} - {item.project_category}")
        session.close()

        completer = QCompleter(item_list)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.item_input.setCompleter(completer)

        # Connect signal to handle item selection
        self.item_input.textChanged.connect(self.handle_item_selection)

    def handle_item_selection(self, text):
        if text and " - " in text:
            parts = text.split(" - ")
            if len(parts) >= 4:
                self.category_input.setText(parts[3])  # Set project category

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

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("THRUZIM Inventory Management")
        self.setMinimumSize(1400, 800)
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
        
        # Stats cards
        stats_layout = QHBoxLayout()
        
        # Total Items Card
        total_card = QFrame()
        total_card.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 8px;
                padding: 20px;
                min-width: 200px;
            }
        """)
        total_layout = QVBoxLayout(total_card)
        self.total_items_label = QLabel("Total Items: 0")
        self.total_items_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        self.total_items_label.setStyleSheet("color: #2c3e50;")
        total_layout.addWidget(self.total_items_label)
        stats_layout.addWidget(total_card)
        
        # Active Items Card
        active_card = QFrame()
        active_card.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 8px;
                padding: 20px;
                min-width: 200px;
            }
        """)
        active_layout = QVBoxLayout(active_card)
        self.active_items_label = QLabel("Active Items: 0")
        self.active_items_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        self.active_items_label.setStyleSheet("color: #27ae60;")
        active_layout.addWidget(self.active_items_label)
        stats_layout.addWidget(active_card)
        
        # Inactive Items Card
        inactive_card = QFrame()
        inactive_card.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 8px;
                padding: 20px;
                min-width: 200px;
            }
        """)
        inactive_layout = QVBoxLayout(inactive_card)
        self.inactive_items_label = QLabel("Inactive Items: 0")
        self.inactive_items_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        self.inactive_items_label.setStyleSheet("color: #7f8c8d;")
        inactive_layout.addWidget(self.inactive_items_label)
        stats_layout.addWidget(inactive_card)
        
        # Damaged Items Card
        damaged_card = QFrame()
        damaged_card.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 8px;
                padding: 20px;
                min-width: 200px;
            }
        """)
        damaged_layout = QVBoxLayout(damaged_card)
        self.damaged_items_label = QLabel("Damaged Items: 0")
        self.damaged_items_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        self.damaged_items_label.setStyleSheet("color: #e74c3c;")
        damaged_layout.addWidget(self.damaged_items_label)
        stats_layout.addWidget(damaged_card)
        
        dashboard_layout.addLayout(stats_layout)

        # Recent items table
        recent_label = QLabel("Recently Added Items")
        recent_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        recent_label.setStyleSheet("color: #2c3e50; margin-top: 20px;")
        dashboard_layout.addWidget(recent_label)
        
        self.recent_items_table = QTableWidget()
        self.recent_items_table.setColumnCount(7)
        self.recent_items_table.setHorizontalHeaderLabels([
            "Name", "Model", "Serial Number", "Project Name", 
            "Quantity", "Location", "Date Added"
        ])
        self.recent_items_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        dashboard_layout.addWidget(self.recent_items_table)

        # Items tab
        items_tab = QWidget()
        items_layout = QVBoxLayout(items_tab)
        
        # Items table
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(8)
        self.items_table.setHorizontalHeaderLabels([
            "Name", "Model", "Serial Number", "Project Name", 
            "Quantity", "Location", "Date Added", "Actions"
        ])
        self.items_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        items_layout.addWidget(self.items_table)

        # Stock Movement tab
        movement_tab = QWidget()
        movement_layout = QVBoxLayout(movement_tab)
        
        # Movement table
        self.movement_table = QTableWidget()
        self.movement_table.setColumnCount(8)
        self.movement_table.setHorizontalHeaderLabels([
            "Date", "Item", "Type", "From", "To", 
            "Project Name", "Quantity", "Status"
        ])
        self.movement_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        movement_layout.addWidget(self.movement_table)

        # Add tabs
        tabs.addTab(dashboard_tab, "Dashboard")
        tabs.addTab(items_tab, "Items")
        tabs.addTab(movement_tab, "Stock Movement")

        # Right side - Quick actions
        right_widget = QWidget()
        right_widget.setMaximumWidth(300)
        right_layout = QVBoxLayout(right_widget)
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

        export_btn = QPushButton("Export Data")
        export_btn.clicked.connect(self.export_data)
        actions_layout.addWidget(export_btn)

        # Sort options
        sort_label = QLabel("Sort By")
        sort_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        sort_label.setStyleSheet("color: #2c3e50; margin-top: 20px;")
        actions_layout.addWidget(sort_label)

        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Date Added", "Project Name"])
        self.sort_combo.currentTextChanged.connect(self.sort_items)
        actions_layout.addWidget(self.sort_combo)

        right_layout.addWidget(actions_card)
        right_layout.addStretch()

        # Add left and right widgets to main layout
        content_layout.addWidget(left_widget, stretch=7)
        content_layout.addWidget(right_widget, stretch=3)

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
                padding: 12px;
                border-radius: 5px;
                font-weight: bold;
                margin: 5px 0;
                min-height: 40px;
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
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #3498db;
                color: white;
                padding: 10px;
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
                padding: 10px 20px;
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
                padding: 8px;
                border: 1px solid #e0e0e0;
                border-radius: 5px;
                background-color: white;
                min-height: 40px;
                min-width: 400px;
            }
            QLineEdit, QTextEdit, QSpinBox {
                padding: 8px;
                border: 1px solid #e0e0e0;
                border-radius: 5px;
                background-color: white;
                min-height: 40px;
                min-width: 400px;
            }
            QDialog {
                min-width: 800px;
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

    def load_data(self):
        session = Session()
        
        # Load items
        items = session.query(Item).all()
        self.items_table.setRowCount(len(items))
        for i, item in enumerate(items):
            self.items_table.setItem(i, 0, QTableWidgetItem(item.name))
            self.items_table.setItem(i, 1, QTableWidgetItem(item.model))
            self.items_table.setItem(i, 2, QTableWidgetItem(item.serial_number))
            self.items_table.setItem(i, 3, QTableWidgetItem(item.project_category))
            self.items_table.setItem(i, 4, QTableWidgetItem(str(item.quantity)))
            self.items_table.setItem(i, 5, QTableWidgetItem(item.storage_location))
            self.items_table.setItem(i, 6, QTableWidgetItem(str(item.date_added)))

            # Add action buttons
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            
            edit_btn = QPushButton("Edit")
            edit_btn.clicked.connect(lambda checked, item=item: self.edit_item(item))
            delete_btn = QPushButton("Delete")
            delete_btn.clicked.connect(lambda checked, item=item: self.delete_item(item))
            
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            self.items_table.setCellWidget(i, 7, actions_widget)

        # Load recent items (last 5)
        recent_items = session.query(Item).order_by(Item.date_added.desc()).limit(5).all()
        self.recent_items_table.setRowCount(len(recent_items))
        for i, item in enumerate(recent_items):
            self.recent_items_table.setItem(i, 0, QTableWidgetItem(item.name))
            self.recent_items_table.setItem(i, 1, QTableWidgetItem(item.model))
            self.recent_items_table.setItem(i, 2, QTableWidgetItem(item.serial_number))
            self.recent_items_table.setItem(i, 3, QTableWidgetItem(item.project_category))
            self.recent_items_table.setItem(i, 4, QTableWidgetItem(str(item.quantity)))
            self.recent_items_table.setItem(i, 5, QTableWidgetItem(item.storage_location))
            self.recent_items_table.setItem(i, 6, QTableWidgetItem(str(item.date_added)))

        # Load movements
        movements = session.query(StockMovement).order_by(StockMovement.date.desc()).all()
        self.movement_table.setRowCount(len(movements))
        for i, movement in enumerate(movements):
            self.movement_table.setItem(i, 0, QTableWidgetItem(str(movement.date)))
            self.movement_table.setItem(i, 1, QTableWidgetItem(movement.item.name))
            self.movement_table.setItem(i, 2, QTableWidgetItem(movement.movement_type))
            self.movement_table.setItem(i, 3, QTableWidgetItem(movement.from_location))
            self.movement_table.setItem(i, 4, QTableWidgetItem(movement.to_location))
            self.movement_table.setItem(i, 5, QTableWidgetItem(movement.project_category))
            self.movement_table.setItem(i, 6, QTableWidgetItem(str(movement.quantity)))
            self.movement_table.setItem(i, 7, QTableWidgetItem(movement.status))

        # Update dashboard stats
        total_items = session.query(Item).count()
        active_items = session.query(Item).filter(Item.quantity > 0).count()
        inactive_items = session.query(Item).filter(Item.quantity == 0).count()
        damaged_items = session.query(Item).filter(Item.status == "Damaged").count()
        
        self.total_items_label.setText(f"Total Items: {total_items}")
        self.active_items_label.setText(f"Active Items: {active_items}")
        self.inactive_items_label.setText(f"Inactive Items: {inactive_items}")
        self.damaged_items_label.setText(f"Damaged Items: {damaged_items}")

        session.close()

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
        
        search_input = QLineEdit()
        search_input.setPlaceholderText("Search by name, model, or serial number...")
        layout.addWidget(search_input)
        
        # Add search results table
        results_table = QTableWidget()
        results_table.setColumnCount(6)
        results_table.setHorizontalHeaderLabels([
            "Name", "Model", "Serial Number", "Project Name", 
            "Quantity", "Location"
        ])
        layout.addWidget(results_table)
        
        # Add search functionality
        def perform_search():
            query = search_input.text().lower()
            session = Session()
            items = session.query(Item).filter(
                (Item.name.ilike(f'%{query}%')) |
                (Item.model.ilike(f'%{query}%')) |
                (Item.serial_number.ilike(f'%{query}%'))
            ).all()
            
            results_table.setRowCount(len(items))
            for i, item in enumerate(items):
                results_table.setItem(i, 0, QTableWidgetItem(item.name))
                results_table.setItem(i, 1, QTableWidgetItem(item.model))
                results_table.setItem(i, 2, QTableWidgetItem(item.serial_number))
                results_table.setItem(i, 3, QTableWidgetItem(item.project_category))
                results_table.setItem(i, 4, QTableWidgetItem(str(item.quantity)))
                results_table.setItem(i, 5, QTableWidgetItem(item.storage_location))
            
            session.close()
        
        search_input.textChanged.connect(perform_search)
        
        dialog.exec()

    def export_data(self):
        try:
            session = Session()
            items = session.query(Item).all()
            
            # Convert to DataFrame
            data = []
            for item in items:
                data.append({
                    'Name': item.name,
                    'Model': item.model,
                    'Serial Number': item.serial_number,
                    'Project Name': item.project_category,
                    'Quantity': item.quantity,
                    'Location': item.storage_location,
                    'Date Added': item.date_added,
                    'Supplier': item.supplier,
                    'Description': item.description
                })
            
            df = pd.DataFrame(data)
            
            # Save to file
            file_name, _ = QFileDialog.getSaveFileName(
                self, "Export Data", "", "Excel Files (*.xlsx);;CSV Files (*.csv)"
            )
            
            if file_name:
                if file_name.endswith('.xlsx'):
                    df.to_excel(file_name, index=False)
                else:
                    df.to_csv(file_name, index=False)
                QMessageBox.information(self, "Success", "Data exported successfully!")
            
            session.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error exporting data: {str(e)}")

    def sort_items(self, sort_by):
        session = Session()
        if sort_by == "Date Added":
            items = session.query(Item).order_by(Item.date_added.desc()).all()
        else:
            items = session.query(Item).order_by(Item.project_category).all()
        
        self.items_table.setRowCount(len(items))
        for i, item in enumerate(items):
            self.items_table.setItem(i, 0, QTableWidgetItem(item.name))
            self.items_table.setItem(i, 1, QTableWidgetItem(item.model))
            self.items_table.setItem(i, 2, QTableWidgetItem(item.serial_number))
            self.items_table.setItem(i, 3, QTableWidgetItem(item.project_category))
            self.items_table.setItem(i, 4, QTableWidgetItem(str(item.quantity)))
            self.items_table.setItem(i, 5, QTableWidgetItem(item.storage_location))
            self.items_table.setItem(i, 6, QTableWidgetItem(str(item.date_added)))
            
            # Add action buttons
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            
            edit_btn = QPushButton("Edit")
            edit_btn.clicked.connect(lambda checked, item=item: self.edit_item(item))
            delete_btn = QPushButton("Delete")
            delete_btn.clicked.connect(lambda checked, item=item: self.delete_item(item))
            
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            self.items_table.setCellWidget(i, 7, actions_widget)
        
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

                # Update item quantity and location
                if movement_data['movement_type'] == 'In':
                    item.quantity += movement_data['quantity']
                elif movement_data['movement_type'] == 'Out':
                    item.quantity -= movement_data['quantity']
                item.storage_location = movement_data['to_location']

                session.add(movement)
                session.commit()
                self.load_data()
                QMessageBox.information(self, "Success", "Movement recorded successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error recording movement: {str(e)}")
            finally:
                session.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec()) 