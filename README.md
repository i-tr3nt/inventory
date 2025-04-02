# THRUZIM Inventory Management System

A desktop application for managing inventory, built with Python and PyQt6.

## Features

- User authentication with role-based access control
- Inventory management (add, edit, delete items)
- Stock tracking and alerts
- Sales and purchase management
- Reports generation
- Data persistence using SQLite database

## Requirements

- Python 3.8 or higher
- PyQt6
- SQLite3
- Other dependencies listed in `requirements.txt`

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/thruzim-inventory.git
cd thruzim-inventory
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Activate the virtual environment if not already activated:
```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Run the application:
```bash
python main.py
```

## Building the Executable

To create a standalone executable:

1. Install PyInstaller:
```bash
pip install pyinstaller
```

2. Build the executable:
```bash
pyinstaller --onefile --windowed --icon=assets/icon.ico main.py
```

The executable will be created in the `dist` directory.

## Default Login Credentials

- Username: admin
- Password: admin123

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request 