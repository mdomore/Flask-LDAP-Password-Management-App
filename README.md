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

## Usage
Once the application is running, you can access it in a web browser:

To change your own password, navigate to http://localhost:5000/change_password.
To reset a user's password, navigate to http://localhost:5000/reset_password.

## Security Considerations
Ensure that the .env file containing sensitive information is not exposed publicly.
Use strong, unique passwords for the ADMIN_USER and ADMIN_PASSWD variables.
Regularly review and update access control settings for the application.

## Contributing
Contributions are welcome! If you encounter any issues or have suggestions for improvements, please open an issue or submit a pull request.

## License
This project is licensed under the MIT License - see the LICENSE file for details.
