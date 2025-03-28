# Inventory Management System

A modern and simple inventory management system built with Python and PyQt6. This desktop application is designed for stock keeping and management, featuring a clean and intuitive interface.

## Features

- Modern desktop interface with tabs
- Dashboard with key metrics and charts
- Item management with detailed tracking
- Stock movement tracking (in, out, damaged, transferred)
- Category distribution visualization
- Low stock alerts
- Multiple storage location support

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd inventory-management
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
venv\Scripts\activate  # On Windows
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Start the application:
```bash
python app.py
```

## Usage

### Dashboard
- View total items count
- Monitor low stock items
- View category distribution chart
- Quick access to add items and record movements

### Items Management
- Add new items with detailed information
- View all items in a table format
- Track item quantities
- Monitor storage locations
- View and edit item details

### Stock Movement
- Record stock movements (in, out, damaged, transferred)
- Track movement history
- Add notes to movements
- View movement timeline

## Storage Locations

The system supports the following storage locations:
- Stores
- Office
- Container
- Data Office

## Database

The application uses SQLite as its database. The database file (`inventory.db`) will be automatically created when you first run the application.

## Contributing

Feel free to submit issues and enhancement requests! 