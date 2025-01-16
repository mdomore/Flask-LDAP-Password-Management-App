from dotenv import load_dotenv
load_dotenv()
from flask import Flask, request, render_template, redirect, url_for, jsonify
import ldap
import ldap.modlist as modlist
import config  # Import the configuration file
import logging
import secrets
import string
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

def ldap_connect():
    ldap_server = f"ldaps://{config.DOMAIN}:636"
    ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_ALLOW)
    ldap.set_option(ldap.OPT_REFERRALS, 0)
    ldap.set_option(ldap.OPT_DEBUG_LEVEL, 4095)
    conn = ldap.initialize(ldap_server, trace_level=2)
    conn.protocol_version = 3
    try:
        conn.simple_bind_s(f"{config.DOMAIN}\\{config.ADMIN_USER}", config.ADMIN_PASSWD)
    except ldap.INVALID_CREDENTIALS:
        logging.error("Invalid credentials")
        raise ValueError("Invalid credentials")
    except ldap.LDAPError as e:
        logging.error(f"Connection failed: {e}")
        raise ValueError(f"Connection failed: {e}")
    return conn

def get_user_dn_by_samaccountname(conn, samaccountname):
    search_base = config.SEARCH_BASE  # e.g., "DC=yourdomain,DC=com"
    search_filter = f"(sAMAccountName={samaccountname})"
    try:
        result = conn.search_s(search_base, ldap.SCOPE_SUBTREE, search_filter, ['distinguishedName', 'mail'])
        if result:
            user_dn = result[0][0]
            email = result[0][1].get('mail', [b''])[0].decode('utf-8')
            logging.debug(f"User DN found: {user_dn}, Email: {email}")
            return user_dn, email
        else:
            logging.error(f"No such object with sAMAccountName: {samaccountname}")
            raise ldap.NO_SUCH_OBJECT(f"No such object with sAMAccountName: {samaccountname}")
    except ldap.LDAPError as e:
        logging.error(f"LDAP search failed: {e}")
        raise ValueError(f"LDAP search failed: {e}")

def generate_password(length=14):
    alphabet = string.ascii_letters + string.digits + string.punctuation
    while True:
        password = ''.join(secrets.choice(alphabet) for i in range(length))
        if (any(c.islower() for c in password)
                and any(c.isupper() for c in password)
                and any(c.isdigit() for c in password)
                and any(c in string.punctuation for c in password)):
            return password

def send_email(to_address, password):
    from_address = config.EMAIL_FROM
    subject = "Your New Password"
    body = f"Your new password is: {password}\n You can personalise it here : http://10.31.247.63/change_password"
    
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = from_address
    msg['To'] = to_address
    
    with smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT) as server:
        server.sendmail(from_address, [to_address], msg.as_string())

@app.route('/')
def index():
    return render_template('reset_password.html')

@app.route('/change_password')
def change_password_page():
    return render_template('change_password.html')

@app.route('/change_password', methods=['POST'])
def change_password():
    username = request.form.get('username')
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')

    if not all([username, current_password, new_password, confirm_password]):
        error_message = "Missing required parameters"
        return render_template('change_password.html', error=error_message), 400

    if new_password != confirm_password:
        error_message = "New passwords do not match"
        return render_template('change_password.html', error=error_message), 400

    try:
        conn = ldap_connect()
        user_dn, _ = get_user_dn_by_samaccountname(conn, username)

        # Bind with the user's current credentials to verify the current password
        try:
            user_conn = ldap.initialize(f"ldaps://{config.DOMAIN}:636")
            user_conn.simple_bind_s(user_dn, current_password)
        except ldap.INVALID_CREDENTIALS:
            return render_template('change_password.html', error="Current password is incorrect"), 400

        # Prepare the password change
        unicode_current_password = ('"%s"' % current_password).encode('utf-16-le')
        unicode_password = ('"%s"' % new_password).encode('utf-16-le')
        change_modlist = [
            (ldap.MOD_DELETE, 'unicodePwd', [unicode_current_password]),
            (ldap.MOD_ADD, 'unicodePwd', [unicode_password]),
        ]

        # Perform the password reset
        conn.modify_s(user_dn, change_modlist)
        conn.unbind_s()
        success_message = "Password changed successfully"
        logging.info(success_message)
        return render_template('change_password.html', success=success_message), 200

    except ValueError as e:
        logging.error(f"ValueError: {e}")
        return render_template('change_password.html', error=str(e)), 400
    except ldap.NO_SUCH_OBJECT as e:
        logging.error(f"LDAP NO_SUCH_OBJECT: {e}")
        return render_template('change_password.html', error=f"No such object: {e}"), 400
    except ldap.INSUFFICIENT_ACCESS as e:
        logging.error(f"LDAP INSUFFICIENT_ACCESS: {e}")
        return render_template('change_password.html', error=f"Insufficient access rights: {e}"), 403
    except ldap.LDAPError as e:
        logging.error(f"LDAPError: {e}")
        return render_template('change_password.html', error=f"An unexpected LDAP error occurred: {e}"), 500
    except Exception as e:
        logging.error(f"Exception: {e}")
        return render_template('change_password.html', error=f"An unexpected error occurred: {e}"), 500

@app.route('/reset_password')
def reset_password_page():
    return render_template('reset_password.html')

@app.route('/reset_password', methods=['POST'])
def reset_password():
    username = request.form.get('username')

    if not username:
        error_message = "Missing required parameters"
        return render_template('reset_password.html', error=error_message), 400

    try:
        conn = ldap_connect()
        user_dn, email = get_user_dn_by_samaccountname(conn, username)

        # Generate a new password
        new_password = generate_password()

        # Prepare the password change
        unicode_password = ('"%s"' % new_password).encode('utf-16-le')
        add_modlist = [(ldap.MOD_REPLACE, 'unicodePwd', [unicode_password])]

        # Perform the password reset
        conn.modify_s(user_dn, add_modlist)
        conn.unbind_s()

        # Send email with the new password
        send_email(email, new_password)

        success_message = "Password reset successfully and sent to the user's email"
        logging.info(success_message)
        return render_template('reset_password.html', success=success_message), 200

    except ValueError as e:
        logging.error(f"ValueError: {e}")
        return render_template('reset_password.html', error=str(e)), 400
    except ldap.NO_SUCH_OBJECT as e:
        logging.error(f"LDAP NO_SUCH_OBJECT: {e}")
        return render_template('reset_password.html', error=f"No such object: {e}"), 400
    except ldap.INSUFFICIENT_ACCESS as e:
        logging.error(f"LDAP INSUFFICIENT_ACCESS: {e}")
        return render_template('reset_password.html', error=f"Insufficient access rights: {e}"), 403
    except ldap.LDAPError as e:
        logging.error(f"LDAPError: {e}")
        return render_template('reset_password.html', error=f"An unexpected LDAP error occurred: {e}"), 500
    except Exception as e:
        logging.error(f"Exception: {e}")
        return render_template('reset_password.html', error=f"An unexpected error occurred: {e}"), 500

if __name__ == '__main__':
    app.run(debug=True)
