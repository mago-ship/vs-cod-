import os
import smtplib
import logging
import csv
import pandas as pd
import time
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from routes import *

# Inicialização do banco de dados
with app.app_context():
    db.create_all()
    logging.info("Banco de dados inicializado")

if __name__ == '__main__':
    logging.info("Iniciando aplicação Flask...")
    logging.info("Sistema configurado com banco de dados SQLite e Mercado Pago")
    app.run(host='0.0.0.0', port=5000, debug=True)
import time
