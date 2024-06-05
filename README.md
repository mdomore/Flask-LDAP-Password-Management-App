# Flask LDAP Password Management App

This Flask application provides functionality for managing passwords in an Active Directory (LDAP) environment. It allows users to change their own passwords and reset passwords for other users.

## Features

- **Change Password**: Allows users to change their own passwords.
- **Reset Password**: Allows administrators to reset passwords for other users.

## Prerequisites

Before running the application, make sure you have the following:

- Python installed on your system (version 3.6 or higher).
- An Active Directory (LDAP) server accessible from the application.

## Configuration

Follow these steps to configure the application:

1. **Install Dependencies**: Install the required Python packages using pip:
   ```
   pip install -r requirements.txt
   ```

2. **Set Environment Variables**: Create a .env file in the root directory of the project with the following variables:
    ```
    DOMAIN=your_domain
    ADMIN_USER=your_admin_username
    ADMIN_PASSWD=your_admin_password
    SEARCH_BASE=your_search_base
    ```
Replace your_domain, your_admin_username, your_admin_password, and your_search_base with the appropriate values for your LDAP environment.

3. **Run the Application**: Start the Flask application by running app.py:

    ```
    flask run
    ```

The application should now be running and accessible at http://localhost:5000.