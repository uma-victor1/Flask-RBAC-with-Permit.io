# Flask Task Manager with RBAC

A secure task management application built with Flask and Permit.io for Role-Based Access Control (RBAC). This application demonstrates how to implement proper authorization in a Flask application using modern security practices.

## Features

- User authentication with Flask-Login
- Role-Based Access Control using Permit.io
- Task management (CRUD operations)
- User management with different permission levels
- Dashboard with task statistics
- Responsive design using Bootstrap

## Prerequisites

- Python 3.7+
- PostgreSQL
- Permit.io account
- Git

## Installation

1. Clone the repository:

```bash
git clone https://github.com/uma-victor1/Flask-RBAC-with-Permit.io.git
cd Flask-RBAC-with-Permit
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

4. Set up environment variables:
   Create a `.env` file in the project root and add:

```
SECRET_KEY=your_secret_key
DATABASE_URL=postgresql://username:password@localhost/task_manager
PERMIT_API_KEY=your_permit_api_key
PERMIT_PDP_URL=your_permit_pdp_url
```

5. Initialize the database:

```bash
flask init-db
```

## Running the Application

1. Start the development server:

```bash
python run.py
```

2. Visit `http://localhost:5000` in your browser

## Project Structure

```
task_manager/
├── app/
│   ├── __init__.py
│   ├── models/
│   ├── routes/
│   ├── templates/
│   ├── static/
│   └── utils/
├── config.py
├── requirements.txt
└── run.py
```

## Setting Up RBAC with Permit.io

1. Create a Permit.io account
2. Create a new project
3. Set up resources and roles as described in the tutorial
4. Configure permissions for each role
5. Add your Permit.io credentials to the `.env` file

## Available Roles

- Admin: Full access to all features
- Regular User: Limited access to their own tasks

## Contributing

1. Fork the repository
2. Create a new branch for your feature
3. Commit your changes
4. Push to your branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Flask documentation
- Permit.io documentation
- Bootstrap team
