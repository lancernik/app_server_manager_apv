# Future development
[Open document](https://docs.google.com/document/d/19MyOS0zblQ0VwOaxu6iRE_wqpx3NT8vm/edit?usp=sharing&ouid=113492287543668581143&rtpof=true&sd=true)

# Implementation details
[Open document](https://docs.google.com/document/d/1975Pbkz57NKbvTx7nYQCgphNuqRuSJwE/edit?usp=sharing&ouid=113492287543668581143&rtpof=true&sd=true)

# Project Setup

## Prerequisites

- Python 3.10
- Virtualenv
- Poetry

https://docs.google.com/document/d/19MyOS0zblQ0VwOaxu6iRE_wqpx3NT8vm/edit?usp=sharing&ouid=113492287543668581143&rtpof=true&sd=true

## Environment Setup

1. Create a virtual environment:
   ```bash
   virtualenv venv --python=python3.10
   ```

2. Activate the virtual environment:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS and Linux:
     ```bash
     source venv/bin/activate
     ```

3. Install dependencies using Poetry:
   ```bash
   poetry install
   ```

## Database Setup

1. Create database migrations:
   ```bash
   python manage.py makemigrations
   ```

2. Apply the migrations:
   ```bash
   python manage.py migrate
   ```

## Create a Superuser

To access the admin panel, create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

## Running the Application

Start the development server:
   ```bash
   python manage.py runserver
   ```

## Additional Notes
- Ensure that the virtual environment is activated when running the commands.
- Access the `http://127.0.0.1:8000/` or any url after starting the server to login with login panel
