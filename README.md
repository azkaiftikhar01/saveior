# Saveior - Personal Savings Tracker

Saveior is a Django-based web application that helps users track their savings goals, manage daily savings plans, and monitor their progress over time.

## Features

- Create and manage multiple savings goals
- Track progress towards each savings goal
- Generate daily savings plans with random amounts
- Record transactions and track your savings history
- Support for multiple currencies
- Responsive design for desktop and mobile

## Technologies Used

- Django 5.0
- Python 3.12
- Bootstrap 5
- SQLite (default database)
- HTML/CSS/JavaScript

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/saveior.git
   cd saveior
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Apply migrations:
   ```
   python manage.py migrate
   ```

5. Create a superuser (admin):
   ```
   python manage.py createsuperuser
   ```

6. Run the development server:
   ```
   python manage.py runserver
   ```

7. Open your browser and navigate to `http://127.0.0.1:8000/`

## Usage

- Register a new account or log in with existing credentials
- Create savings goals with target amounts and dates
- Add transactions to track your savings
- View your progress and daily savings plan
- Delete goals when completed or no longer needed

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Django framework
- Bootstrap for the UI components
- Exchange rate API for currency conversion

## Project Structure

- `saveior/` - Main project directory
- `savings/` - Main app directory
  - `models.py` - Database models
  - `views.py` - View functions
  - `forms.py` - Form definitions
  - `templates/` - HTML templates
  - `static/` - CSS, JavaScript, and other static files

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request 