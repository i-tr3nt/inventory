import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QTableWidget, 
                            QTableWidgetItem, QDialog, QLineEdit, QComboBox, 
                            QTextEdit, QSpinBox, QMessageBox, QTabWidget)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon, QPainter
from PySide6.QtCharts import QChart, QChartView, QPieSeries
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

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
    created_at = Column(DateTime, default=datetime.utcnow)
    movements = relationship("StockMovement", back_populates="item")

class StockMovement(Base):
    __tablename__ = 'stock_movement'
    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, ForeignKey('item.id'), nullable=False)
    movement_type = Column(String(20), nullable=False)
    quantity = Column(Integer, nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text)
    item = relationship("Item", back_populates="movements")

Base.metadata.create_all(engine)

class AddItemDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Item")
        self.setModal(True)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Name:"))
        self.name_input = QLineEdit()
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)

        # Model
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("Model:"))
        self.model_input = QLineEdit()
        model_layout.addWidget(self.model_input)
        layout.addLayout(model_layout)

        # Serial Number
        serial_layout = QHBoxLayout()
        serial_layout.addWidget(QLabel("Serial Number:"))
        self.serial_input = QLineEdit()
        serial_layout.addWidget(self.serial_input)
        layout.addLayout(serial_layout)

        # Project Category
        category_layout = QHBoxLayout()
        category_layout.addWidget(QLabel("Project Category:"))
        self.category_input = QLineEdit()
        category_layout.addWidget(self.category_input)
        layout.addLayout(category_layout)

        # Description
        desc_layout = QVBoxLayout()
        desc_layout.addWidget(QLabel("Description:"))
        self.desc_input = QTextEdit()
        desc_layout.addWidget(self.desc_input)
        layout.addLayout(desc_layout)

        # Quantity
        quantity_layout = QHBoxLayout()
        quantity_layout.addWidget(QLabel("Quantity:"))
        self.quantity_input = QSpinBox()
        self.quantity_input.setMinimum(0)
        quantity_layout.addWidget(self.quantity_input)
        layout.addLayout(quantity_layout)

        # Supplier
        supplier_layout = QHBoxLayout()
        supplier_layout.addWidget(QLabel("Supplier:"))
        self.supplier_input = QLineEdit()
        supplier_layout.addWidget(self.supplier_input)
        layout.addLayout(supplier_layout)

        # Storage Location
        location_layout = QHBoxLayout()
        location_layout.addWidget(QLabel("Storage Location:"))
        self.location_input = QComboBox()
        self.location_input.addItems(["stores", "office", "container", "data office"])
        location_layout.addWidget(self.location_input)
        layout.addLayout(location_layout)

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

    def get_item_data(self):
        return {
            'name': self.name_input.text(),
            'model': self.model_input.text(),
            'serial_number': self.serial_input.text(),
            'project_category': self.category_input.text(),
            'description': self.desc_input.toPlainText(),
            'quantity': self.quantity_input.value(),
            'supplier': self.supplier_input.text(),
            'storage_location': self.location_input.currentText()
        }

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inventory Management System")
        self.setMinimumSize(1000, 600)
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create tab widget
        tabs = QTabWidget()
        layout.addWidget(tabs)

        # Dashboard tab
        dashboard_tab = QWidget()
        dashboard_layout = QVBoxLayout(dashboard_tab)
        
        # Stats cards
        stats_layout = QHBoxLayout()
        self.total_items_label = QLabel("Total Items: 0")
        self.low_stock_label = QLabel("Low Stock Items: 0")
        stats_layout.addWidget(self.total_items_label)
        stats_layout.addWidget(self.low_stock_label)
        dashboard_layout.addLayout(stats_layout)

        # Category distribution chart
        self.chart_view = QChartView()
        self.chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        dashboard_layout.addWidget(self.chart_view)

        # Quick actions
        actions_layout = QHBoxLayout()
        add_item_btn = QPushButton("Add New Item")
        add_item_btn.clicked.connect(self.show_add_item_dialog)
        record_movement_btn = QPushButton("Record Movement")
        record_movement_btn.clicked.connect(self.show_record_movement_dialog)
        actions_layout.addWidget(add_item_btn)
        actions_layout.addWidget(record_movement_btn)
        dashboard_layout.addLayout(actions_layout)

        # Items tab
        items_tab = QWidget()
        items_layout = QVBoxLayout(items_tab)
        
        # Items table
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(7)
        self.items_table.setHorizontalHeaderLabels([
            "Name", "Model", "Serial Number", "Category", 
            "Quantity", "Location", "Actions"
        ])
        items_layout.addWidget(self.items_table)

        # Stock Movement tab
        movement_tab = QWidget()
        movement_layout = QVBoxLayout(movement_tab)
        
        # Movement table
        self.movement_table = QTableWidget()
        self.movement_table.setColumnCount(5)
        self.movement_table.setHorizontalHeaderLabels([
            "Date", "Item", "Type", "Quantity", "Notes"
        ])
        movement_layout.addWidget(self.movement_table)

        # Add tabs
        tabs.addTab(dashboard_tab, "Dashboard")
        tabs.addTab(items_tab, "Items")
        tabs.addTab(movement_tab, "Stock Movement")

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
            
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            view_btn = QPushButton("View")
            edit_btn = QPushButton("Edit")
            actions_layout.addWidget(view_btn)
            actions_layout.addWidget(edit_btn)
            self.items_table.setCellWidget(i, 6, actions_widget)

        # Load movements
        movements = session.query(StockMovement).order_by(StockMovement.date.desc()).all()
        self.movement_table.setRowCount(len(movements))
        for i, movement in enumerate(movements):
            self.movement_table.setItem(i, 0, QTableWidgetItem(str(movement.date)))
            self.movement_table.setItem(i, 1, QTableWidgetItem(movement.item.name))
            self.movement_table.setItem(i, 2, QTableWidgetItem(movement.movement_type))
            self.movement_table.setItem(i, 3, QTableWidgetItem(str(movement.quantity)))
            self.movement_table.setItem(i, 4, QTableWidgetItem(movement.notes))

        # Update dashboard stats
        total_items = session.query(Item).count()
        low_stock = session.query(Item).filter(Item.quantity < 5).count()
        self.total_items_label.setText(f"Total Items: {total_items}")
        self.low_stock_label.setText(f"Low Stock Items: {low_stock}")

        # Update category distribution chart
        categories = session.query(Item.project_category, func.count(Item.id)).group_by(Item.project_category).all()
        series = QPieSeries()
        for category, count in categories:
            series.append(category, count)
        
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Category Distribution")
        self.chart_view.setChart(chart)

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
        # Implement movement dialog
        pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec()) 