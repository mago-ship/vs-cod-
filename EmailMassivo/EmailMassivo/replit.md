# Email Mass Sender Application

## Overview

This is a Flask-based web application designed for sending bulk emails with user authentication and subscription-based access control. The system supports both .txt and .csv email list uploads, Gmail SMTP integration, and includes user registration with payment workflow management. All interfaces are in Portuguese and use Bootstrap styling for a modern, responsive experience.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Template Engine**: Jinja2 (Flask's default)
- **CSS Framework**: Bootstrap 5.3.0 for responsive design
- **Icons**: Font Awesome 6.4.0 for visual elements
- **Styling**: Custom CSS with gradient themes and modern UI components
- **File Upload**: HTML5 file input with client-side validation

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **File Handling**: Werkzeug utilities for secure file uploads
- **Email Service**: Python's built-in `smtplib` for SMTP email sending
- **Validation**: Custom regex-based email validation
- **Session Management**: Flask's built-in session handling with secret key

## Key Components

### Core Application (app.py)
- **Flask App Configuration**: Session management, upload settings, and security configurations
- **Authentication System**: Session-based login with predefined user credentials and new user registration
- **Subscription Management**: Email-based plan control with 'pendente' and 'ilimitado' status levels
- **File Upload Handler**: Secure file processing with extension validation (txt and csv files)
- **Email Validation**: Regex-based email format validation with duplicate detection
- **Email Parsing**: File reading functionality to extract email addresses from TXT and CSV files
- **SMTP Integration**: Email sending functionality using user-provided credentials from web form
- **Payment Workflow**: Simple payment confirmation system for plan activation

### Frontend Interface (templates/)
- **Responsive Design**: Bootstrap-based layout optimized for all device sizes
- **Authentication UI**: Modern login page with user info display and logout functionality
- **Registration System**: Complete user registration form with validation (register.html)
- **Subscription Interface**: Payment and plan management page with PIX integration (plano.html)
- **Form Components**: File upload, email composition, and recipient management
- **Visual Design**: Modern gradient styling with hover effects, animations, and custom logo
- **User Experience**: Interactive elements with Font Awesome icons and enhanced file support
- **Portuguese Language**: All interfaces fully localized in Portuguese

### Security Features
- **Authentication**: Session-based login system with predefined user credentials
- **Access Control**: Protected routes requiring authentication to access main functionality
- **File Security**: Secure filename handling and extension validation (txt, csv)
- **Upload Limits**: 16MB maximum file size restriction
- **Input Validation**: Email format validation, sanitization, and duplicate removal
- **Session Management**: Secure session handling with logout functionality

## Data Flow

1. **User Registration**: New users create accounts with username, email, and password
2. **Plan Assignment**: System automatically assigns 'pendente' plan status to new users
3. **Authentication**: Users log in and are directed based on their plan status
4. **Plan Verification**: Users with 'pendente' status are redirected to payment page
5. **Payment Processing**: Users confirm payment to activate 'ilimitado' plan
6. **File Upload**: Authorized users upload .txt or .csv files containing email addresses
7. **File Processing**: Application validates file type and reads email addresses
8. **Email Validation**: Each email address is validated using regex patterns with duplicate removal
9. **Email Composition**: User creates email content through web interface
10. **Bulk Sending**: Application sends emails via SMTP to all valid recipients
11. **Feedback**: User receives success/error feedback through Flash messages

## External Dependencies

### Python Packages
- **Flask**: Web framework for routing and templating
- **Werkzeug**: WSGI utilities for secure file handling
- **smtplib**: Built-in SMTP client for email sending
- **email.mime**: Built-in email message formatting

### Frontend Dependencies
- **Bootstrap 5.3.0**: CSS framework from CDN
- **Font Awesome 6.4.0**: Icon library from CDN

### Email Service Integration
- **SMTP Configuration**: Supports Gmail and other SMTP providers
- **Authentication**: App password or OAuth-based authentication
- **Form-based Credentials**: Email and password provided directly through web interface

## Deployment Strategy

### Configuration Management
- **Session-based Security**: Only session keys stored as environment variables; email credentials provided by user per session
- **Development Fallbacks**: Default values provided for development environment
- **Upload Directory**: Automatic creation of upload folder structure

### File Storage
- **Local Storage**: Uploaded files stored in local 'uploads' directory
- **Temporary Processing**: Files processed and can be cleaned up after email sending
- **Size Limitations**: Built-in file size restrictions for performance

### Logging and Debugging
- **Debug Mode**: Comprehensive logging configured for development
- **Error Handling**: Flash message system for user feedback
- **File Validation**: Multiple layers of input validation

### Production Considerations
- **Secret Key**: Environment-based secret key configuration
- **SMTP Security**: Secure email authentication methods
- **File Cleanup**: Potential need for uploaded file cleanup strategy
- **Rate Limiting**: May need rate limiting for email sending in production