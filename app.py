import os
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'portfolio-super-secret-key-129847192')

# Ensure messages are logged in a file for demo purposes
MESSAGES_FILE = os.path.join(os.path.dirname(__file__), 'messages.txt')

# Social media links
SOCIAL_LINKS = {
    'github':    'https://github.com/augustev005',
    'facebook':  'https://www.facebook.com/share/18EdXQv75E/?mibextid=wwXIfr',
    'instagram': 'https://www.instagram.com/akossiwa_agos?igsh=MTBjMGNuYnl3ZnpzaQ%3D%3D&utm_source=qr',
    'twitter':   'https://x.com/augustusevans8?s=11',
}

def get_messages():
    if not os.path.exists(MESSAGES_FILE):
        return []
    
    with open(MESSAGES_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Split by '--- New Message ---' separator
    parts = content.split('--- New Message ---')
    messages = []
    
    for part in parts:
        part = part.strip()
        if not part:
            continue
            
        lines = part.split('\n')
        msg_data = {
            'name': '',
            'email': '',
            'phone': '',
            'date': '',
            'message': ''
        }
        
        in_message_body = False
        msg_lines = []
        
        for line in lines:
            if in_message_body:
                msg_lines.append(line)
            elif line.startswith('Name:'):
                msg_data['name'] = line[len('Name:'):].strip()
            elif line.startswith('Email:'):
                msg_data['email'] = line[len('Email:'):].strip()
            elif line.startswith('Phone:'):
                msg_data['phone'] = line[len('Phone:'):].strip()
            elif line.startswith('Date:'):
                msg_data['date'] = line[len('Date:'):].strip()
            elif line.startswith('Message:'):
                msg_data['message'] = line[len('Message:'):].strip()
                in_message_body = True
        
        if in_message_body and msg_lines:
            if msg_data['message']:
                msg_data['message'] += '\n' + '\n'.join(msg_lines)
            else:
                msg_data['message'] = '\n'.join(msg_lines)
                
        if msg_data['name'] or msg_data['email']:
            messages.append(msg_data)
            
    return messages

def save_all_messages(messages):
    try:
        with open(MESSAGES_FILE, 'w', encoding='utf-8') as f:
            for msg in messages:
                f.write("--- New Message ---\n")
                f.write(f"Name: {msg.get('name', '')}\n")
                f.write(f"Email: {msg.get('email', '')}\n")
                f.write(f"Phone: {msg.get('phone', '')}\n")
                f.write(f"Date: {msg.get('date', '')}\n")
                f.write(f"Message: {msg.get('message', '')}\n\n")
        return True
    except Exception as e:
        print(f"Error saving messages: {e}")
        return False

def send_email_notification(name, email, phone, message):
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = os.getenv('SMTP_PORT')
    smtp_username = os.getenv('SMTP_USERNAME')
    smtp_password = os.getenv('SMTP_PASSWORD')
    receiver_email = os.getenv('RECEIVER_EMAIL', 'augustev005@gmail.com')
    
    if not smtp_server or not smtp_port or not smtp_username or not smtp_password:
        print("SMTP is not fully configured in .env. Skipping email notification.")
        return False
        
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"🔔 New Portfolio Message from {name}"
        msg['From'] = smtp_username
        msg['To'] = receiver_email
        
        text = f"""
        New Portfolio Inquiry Received:
        ---------------------------------
        Name: {name}
        Email: {email}
        Phone: {phone}
        Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        Message:
        {message}
        """
        
        html = f"""
        <html>
          <body style="font-family: 'Plus Jakarta Sans', sans-serif; background-color: #08070b; color: #ffffff; padding: 20px; margin: 0;">
            <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px; background-color: #120f1a; border: 1px solid rgba(157, 78, 221, 0.2); border-radius: 16px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.5);">
              <tr>
                <td style="background-color: #9d4edd; padding: 30px; text-align: center;">
                  <h1 style="color: #ffffff; margin: 0; font-size: 24px; font-weight: 700; letter-spacing: -0.02em;">New Inquiry Received!</h1>
                </td>
              </tr>
              <tr>
                <td style="padding: 40px 30px; color: #9592a6; font-size: 16px; line-height: 1.6;">
                  <p style="margin-top: 0; color: #ffffff;">Hello Akossiwa,</p>
                  <p>You have received a new contact submission from your portfolio website. Here are the details:</p>
                  
                  <table cellpadding="0" cellspacing="0" width="100%" style="margin: 24px 0; border-collapse: collapse;">
                    <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
                      <td style="padding: 10px 0; font-weight: 600; color: #ffffff; width: 120px;">Name:</td>
                      <td style="padding: 10px 0; color: #9592a6;">{name}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
                      <td style="padding: 10px 0; font-weight: 600; color: #ffffff;">Email:</td>
                      <td style="padding: 10px 0;"><a href="mailto:{email}" style="color: #9d4edd; text-decoration: none;">{email}</a></td>
                    </tr>
                    <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
                      <td style="padding: 10px 0; font-weight: 600; color: #ffffff;">Phone:</td>
                      <td style="padding: 10px 0;"><a href="tel:{phone}" style="color: #9d4edd; text-decoration: none;">{phone}</a></td>
                    </tr>
                    <tr>
                      <td style="padding: 10px 0; font-weight: 600; color: #ffffff;">Date:</td>
                      <td style="padding: 10px 0; color: #9592a6;">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</td>
                    </tr>
                  </table>
                  
                  <div style="background-color: #181524; border: 1px solid rgba(255,255,255,0.05); padding: 20px; border-radius: 12px; margin-top: 20px;">
                    <h4 style="margin: 0 0 10px 0; color: #ffffff; font-size: 14px; text-transform: uppercase; letter-spacing: 0.05em;">Message:</h4>
                    <p style="margin: 0; color: #ffffff; white-space: pre-wrap;">{message}</p>
                  </div>
                </td>
              </tr>
              <tr>
                <td style="background-color: rgba(8, 7, 11, 0.6); padding: 20px; text-align: center; font-size: 12px; color: #5e5a75; border-top: 1px solid rgba(255,255,255,0.05);">
                  <p style="margin: 0;">This is an automated notification from your portfolio application.</p>
                </td>
              </tr>
            </table>
          </body>
        </html>
        """
        
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')
        msg.attach(part1)
        msg.attach(part2)
        
        port = int(smtp_port)
        if port == 465:
            server = smtplib.SMTP_SSL(smtp_server, port)
        else:
            server = smtplib.SMTP(smtp_server, port)
            server.starttls()
            
        server.login(smtp_username, smtp_password)
        server.sendmail(smtp_username, receiver_email, msg.as_string())
        server.quit()
        print("Notification email sent successfully!")
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

@app.route('/')
def index():
    return render_template('index.html', social=SOCIAL_LINKS)

@app.route('/send-message', methods=['POST'])
def send_message():
    data = request.form
    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone')
    message = data.get('message')

    if not name or not email or not phone or not message:
        return jsonify({
            'status': 'error',
            'message': 'All fields are required. Please fill in your name, email, phone number, and message.'
        }), 400

    date_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Save message to file
    try:
        with open(MESSAGES_FILE, 'a', encoding='utf-8') as f:
            f.write(f"--- New Message ---\n")
            f.write(f"Name: {name}\n")
            f.write(f"Email: {email}\n")
            f.write(f"Phone: {phone}\n")
            f.write(f"Date: {date_str}\n")
            f.write(f"Message: {message}\n\n")
    except Exception as e:
        print(f"Error saving message: {e}")

    # Send email notification
    send_email_notification(name, email, phone, message)

    return jsonify({
        'status': 'success',
        'message': f'Hey {name}, your message has been sent successfully!'
    })

@app.before_request
def admin_maintenance():
    if request.path.startswith('/admin'):
        return "<div style='text-align: center; margin-top: 100px; font-family: sans-serif;'><h1>Admin Area Under Maintenance 🛠️</h1><p>We are currently performing scheduled maintenance. Please try again later.</p></div>", 503

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if session.get('logged_in'):
        return redirect(url_for('admin_dashboard'))
        
    error = None
    if request.method == 'POST':
        password = request.form.get('password')
        expected_password = os.getenv('ADMIN_PASSWORD', 'admin123')
        
        if password == expected_password:
            session['logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            error = 'Invalid password. Please try again.'
            
    return render_template('admin_login.html', error=error)

@app.route('/admin')
def admin_dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('admin_login'))
        
    messages = get_messages()
    return render_template('admin_dashboard.html', messages=messages)

@app.route('/admin/delete/<int:msg_id>', methods=['POST'])
def delete_message_route(msg_id):
    if not session.get('logged_in'):
        return redirect(url_for('admin_login'))
        
    messages = get_messages()
    if 0 <= msg_id < len(messages):
        messages.pop(msg_id)
        save_all_messages(messages)
        
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/logout')
def admin_logout():
    session.pop('logged_in', None)
    return redirect(url_for('admin_login'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
