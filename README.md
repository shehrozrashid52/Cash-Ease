# BankApp - Full-Stack Banking Web Application

A comprehensive banking web application built with Django, featuring secure authentication, transaction management, and admin panel.

## 🚀 Features

### User Features
- **Secure Authentication**: Registration with OTP verification, login with optional 2FA
- **User Dashboard**: Balance tracking, transaction history, quick actions
- **Money Transfers**: Send money to other users via phone number
- **Money Requests**: Request money from other users
- **Bill Payments**: Pay utility bills (electricity, gas, water, internet, mobile)
- **QR Code Payments**: Generate and scan QR codes for payments
- **Profile Management**: Update personal information and profile picture
- **KYC Verification**: Upload identity documents for verification
- **Notifications**: Real-time notifications for transactions and account updates
- **PIN Security**: Transaction verification with 4-digit PIN

### Admin Features
- **User Management**: View, block/unblock users
- **Transaction Monitoring**: View all transactions with filtering
- **KYC Review**: Approve/reject user documents
- **Financial Reports**: Transaction analytics and user statistics
- **Fraud Detection**: Basic fraud detection alerts

### Security Features
- **OTP Verification**: Phone number verification during registration
- **PIN Protection**: All transactions require PIN verification
- **Fraud Detection**: Monitors for suspicious transaction patterns
- **Session Management**: Secure user sessions
- **Input Validation**: Comprehensive form validation

## 🛠️ Technology Stack

- **Backend**: Django 4.2.7
- **Database**: MySQL
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Authentication**: Django OTP, Custom User Model
- **File Handling**: Django File Storage
- **QR Codes**: Python QRCode library

## 📦 Installation

### Prerequisites
- Python 3.8+
- MySQL Server
- pip (Python package manager)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd bank_webapp
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure MySQL Database**
   - Start MySQL server
   - Update database credentials in `.env` file:
   ```
   DB_NAME=bankapp_db
   DB_USER=root
   DB_PASSWORD=your_mysql_password
   DB_HOST=localhost
   DB_PORT=3306
   ```

4. **Run Database Setup**
   ```bash
   python setup_database.py
   ```

5. **Start the Development Server**
   ```bash
   python manage.py runserver
   ```

6. **Access the Application**
   - Main App: http://127.0.0.1:8000/
   - Admin Panel: http://127.0.0.1:8000/admin/

## 👥 Default Login Credentials

### Admin Account
- **Username**: admin
- **Password**: admin123
- **Access**: Full admin panel access

### Sample User Accounts
- **Username**: john_doe, jane_smith, bob_wilson
- **Password**: password123
- **Features**: All user features available

## 📱 Usage Guide

### For Users

1. **Registration**
   - Create account with phone number
   - Verify phone with OTP
   - Complete profile setup

2. **Dashboard**
   - View current balance
   - See recent transactions
   - Access quick actions
   - Check notifications

3. **Send Money**
   - Enter recipient's phone number
   - Specify amount and description
   - Confirm with PIN

4. **Request Money**
   - Enter requester's phone number
   - Specify amount and message
   - Wait for approval

5. **Pay Bills**
   - Select bill type
   - Enter bill number and amount
   - Confirm payment with PIN

6. **QR Payments**
   - Generate QR code for receiving payments
   - Scan QR codes to make payments
   - Flexible or fixed amount options

### For Admins

1. **User Management**
   - View all registered users
   - Block/unblock suspicious accounts
   - Monitor user activity

2. **Transaction Monitoring**
   - View all transactions
   - Filter by status, date, type
   - Investigate suspicious activities

3. **KYC Review**
   - Review uploaded documents
   - Approve or reject with comments
   - Ensure compliance

4. **Financial Reports**
   - View transaction statistics
   - Monitor daily/monthly volumes
   - Generate reports

## 🔒 Security Features

### Fraud Detection
- Multiple large transactions in short time
- Single transaction above threshold
- Unusual transaction patterns

### Data Protection
- PIN encryption
- Secure session management
- Input sanitization
- CSRF protection

### Authentication
- Phone number verification
- OTP-based registration
- PIN-based transaction verification
- Session timeout

## 📊 Database Schema

### Core Models
- **User**: Extended Django user with phone verification
- **Profile**: User profile with balance and account details
- **Transaction**: All money transfers and payments
- **Bill**: Bill payment records
- **MoneyRequest**: Money request management
- **KYCDocument**: Identity verification documents
- **Notification**: User notifications
- **QRCode**: QR code generation records

## 🚀 Deployment

### Production Setup
1. Update `DEBUG = False` in settings
2. Configure production database
3. Set up static file serving
4. Configure email backend for OTP
5. Set up SSL certificates
6. Configure web server (nginx/Apache)

### Environment Variables
```
SECRET_KEY=your-secret-key
DEBUG=False
DB_NAME=bankapp_db
DB_USER=db_user
DB_PASSWORD=db_password
DB_HOST=db_host
DB_PORT=3306
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Add tests
5. Submit pull request

## 📄 License

This project is licensed under the MIT License.

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Contact: support@bankapp.com

## 🔄 Updates

### Version 1.0.0
- Initial release
- Core banking features
- Admin panel
- Security implementation
- Mobile responsive design

---

**Note**: This is a demonstration banking application. For production use, additional security measures, compliance features, and thorough testing are required.