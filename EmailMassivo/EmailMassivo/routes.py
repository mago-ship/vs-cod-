from flask import render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from app import app, db, PLANOS_DISPONIVEIS, sdk
from models import User, Subscription
from datetime import datetime
import os, logging
from app import allowed_file, is_valid_email, read_emails_from_file, send_mass_email, create_mercadopago_payment

# Decorator para verificar plano ativo
def plan_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return app.login_manager.unauthorized()
        if not current_user.has_active_subscription():
            flash('Seu plano está pendente ou expirado. Faça a assinatura.', 'warning')
            return redirect(url_for('plano'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/register', methods=['GET', 'POST'])
def register():
    <input type="file" name="attachments" multiple>    if current_user.is_authenticated:
        return redirect(url_for('enviar'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        if not username:
            flash('Por favor, insira o nome de usuário.', 'error')
            return render_template('register.html')
        if not email:
            flash('Por favor, insira o e-mail.', 'error')
            return render_template('register.html')
        if not password:
            flash('Por favor, insira a senha.', 'error')
            return render_template('register.html')
        if not confirm_password:
            flash('Por favor, confirme a senha.', 'error')
            return render_template('register.html')
        if not is_valid_email(email):
            flash('Por favor, insira um e-mail válido.', 'error')
            return render_template('register.html')
        if password != confirm_password:
            flash('As senhas não conferem.', 'error')
            return render_template('register.html')
        if User.query.filter_by(username=username).first():
            flash('Este nome de usuário já está em uso.', 'error')
            return render_template('register.html')
        if User.query.filter_by(email=email).first():
            flash('Este e-mail já está registrado.', 'error')
            return render_template('register.html')
        try:
            user = User()
            user.username = username
            user.email = email
            user.set_password(password)
            db.session.add(user)
            db.session.flush()
            if email == 'ofigura.2012@gmail.com':
                subscription = Subscription()
                subscription.user_id = user.id
                subscription.plano = 'vip'
                subscription.status = 'ativo'
                subscription.data_inicio = datetime.utcnow()
            else:
                subscription = Subscription()
                subscription.user_id = user.id
                subscription.plano = 'pendente'
                subscription.status = 'pendente'
            db.session.add(subscription)
            db.session.commit()
            flash('Cadastro realizado com sucesso! Faça login para continuar.', 'success')
            logging.info(f"Novo usuário registrado: {username} ({email})")
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            logging.error(f"Erro ao registrar usuário: {str(e)}")
            flash('Erro interno. Tente novamente.', 'error')
            return render_template('register.html')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('enviar'))
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()
        if not email:
            flash('Por favor, insira o e-mail.', 'error')
            return render_template('login.html')
        if not password:
            flash('Por favor, insira a senha.', 'error')
            return render_template('login.html')
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            if user.has_active_subscription():
                flash(f'Bem-vindo, {user.username}!', 'success')
                logging.info(f"Login bem-sucedido para usuário: {user.username} ({user.email})")
                return redirect(url_for('enviar'))
            else:
                flash(f'Bem-vindo, {user.username}! Seu plano está pendente.', 'warning')
                logging.info(f"Login bem-sucedido para usuário: {user.username} ({user.email}) - Plano pendente")
                return redirect(url_for('plano'))
        else:
            flash('E-mail ou senha incorretos.', 'error')
            logging.warning(f"Tentativa de login inválida para e-mail: {email}")
            return render_template('login.html')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    username = current_user.username
    logout_user()
    flash(f'Você foi desconectado com sucesso, {username}.', 'info')
    logging.info(f"Logout realizado para usuário: {username}")
    return redirect(url_for('login'))

@app.route('/plano', methods=['GET', 'POST'])
@login_required
def plano():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'ja_paguei':
            try:
                plano_tipo = request.form.get('plano_tipo', 'mensal')
                if not current_user.subscription:
                    subscription = Subscription()
                    subscription.user_id = current_user.id
                    db.session.add(subscription)
                    current_user.subscription = subscription
                current_user.subscription.activate_plan(plano_tipo)
                db.session.commit()
                flash('Pagamento confirmado! Seu plano foi ativado com sucesso.', 'success')
                logging.info(f"Plano {plano_tipo} ativado manualmente para usuário: {current_user.username}")
                return redirect(url_for('enviar'))
            except Exception as e:
                db.session.rollback()
                logging.error(f"Erro ao ativar plano manualmente: {str(e)}")
                flash('Erro ao ativar plano. Tente novamente.', 'error')
        elif action == 'criar_pagamento':
            plano_tipo = request.form.get('plano_tipo')
            if plano_tipo in PLANOS_DISPONIVEIS:
                payment_data = create_mercadopago_payment(plano_tipo, current_user.email)
                if payment_data:
                    return redirect(payment_data['init_point'])
                else:
                    flash('Erro ao criar pagamento. Tente novamente.', 'error')
            else:
                flash('Plano inválido selecionado.', 'error')
    subscription_info = current_user.get_subscription_info()
    return render_template('plano.html', user=current_user, subscription_info=subscription_info, planos_disponiveis=PLANOS_DISPONIVEIS)

@app.route('/retorno_pagamento')
@login_required
def retorno_pagamento():
    status = request.args.get('status')
    plano_tipo = request.args.get('plano')
    payment_id = request.args.get('payment_id')
    if status == 'success' and plano_tipo:
        try:
            if not current_user.subscription:
                subscription = Subscription()
                subscription.user_id = current_user.id
                db.session.add(subscription)
                current_user.subscription = subscription
            current_user.subscription.activate_plan(plano_tipo)
            current_user.subscription.mercadopago_id = payment_id
            if plano_tipo in PLANOS_DISPONIVEIS:
                current_user.subscription.valor_pago = PLANOS_DISPONIVEIS[plano_tipo]['preco']
            db.session.commit()
            flash('Pagamento aprovado! Seu plano foi ativado com sucesso.', 'success')
            logging.info(f"Plano {plano_tipo} ativado via Mercado Pago para usuário: {current_user.username}")
            return redirect(url_for('enviar'))
        except Exception as e:
            db.session.rollback()
            logging.error(f"Erro ao ativar plano via Mercado Pago: {str(e)}")
            flash('Erro ao processar pagamento. Entre em contato com o suporte.', 'error')
    elif status == 'pending':
        flash('Pagamento pendente. Aguarde a confirmação.', 'info')
    else:
        flash('Pagamento não aprovado ou cancelado.', 'warning')
    return redirect(url_for('plano'))

@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.has_active_subscription():
            return redirect(url_for('enviar'))
        else:
            return redirect(url_for('plano'))
    else:
        return redirect(url_for('login'))

@app.route('/enviar', methods=['GET', 'POST'])
@plan_required
def enviar():
    if request.method == 'POST':
        subject = request.form.get('subject', '').strip()
        body = request.form.get('body', '').strip()
        sender_email = request.form.get('sender_email', '').strip()
        sender_password = request.form.get('sender_password', '').strip()
        # Anexos
        attachments = request.files.getlist('attachments')

        if not subject:
            flash('Por favor, insira o assunto do email.', 'error')
            return redirect(url_for('enviar'))
        if not body:
            flash('Por favor, insira o corpo da mensagem.', 'error')
            return redirect(url_for('enviar'))
        if not sender_email:
            flash('Por favor, insira o email remetente.', 'error')
            return redirect(url_for('enviar'))
        if not sender_password:
            flash('Por favor, insira a senha de aplicativo.', 'error')
            return redirect(url_for('enviar'))
        if not is_valid_email(sender_email):
            flash('Por favor, insira um email remetente válido.', 'error')
            return redirect(url_for('enviar'))
        if 'email_file' not in request.files:
            flash('Por favor, selecione um arquivo com a lista de emails.', 'error')
            return redirect(url_for('enviar'))
        file = request.files['email_file']
        if file.filename == '':
            flash('Nenhum arquivo foi selecionado.', 'error')
            return redirect(url_for('enviar'))
        if not allowed_file(file.filename):
            flash('Apenas arquivos .txt, .csv e .xlsx são permitidos.', 'error')
            return redirect(url_for('enviar'))
        filename = secure_filename(file.filename or 'uploaded_file.txt')
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        try:
            file.save(filepath)
            logging.info(f"Arquivo salvo temporariamente: {filepath}")
            email_list = read_emails_from_file(filepath)
            if email_list is None:
                flash('Erro ao ler o arquivo. Verifique se o formato está correto.', 'error')
                return redirect(url_for('enviar'))
            if not email_list:
                flash('Nenhum email válido foi encontrado no arquivo.', 'error')
                return redirect(url_for('enviar'))
            logging.info(f"Encontrados {len(email_list)} emails válidos no arquivo")
            # Envio dos emails com anexos
            successful_sends = 0
            errors = []
            try:
                import smtplib
                from email.mime.text import MIMEText
                from email.mime.multipart import MIMEMultipart
                from email.mime.base import MIMEBase
                from email import encoders
                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login(sender_email, sender_password)
                for i, email_destinatario in enumerate(email_list):
                    try:
                        msg = MIMEMultipart()
                        msg['From'] = sender_email
                        msg['To'] = email_destinatario
                        msg['Subject'] = subject
                        msg.attach(MIMEText(body, 'plain'))
                        # Adiciona anexos
                        for attachment in attachments:
                            if attachment.filename:
                                part = MIMEBase('application', 'octet-stream')
                                part.set_payload(attachment.read())
                                encoders.encode_base64(part)
                                part.add_header('Content-Disposition', f'attachment; filename={secure_filename(attachment.filename)}')
                                msg.attach(part)
                        server.sendmail(sender_email, email_destinatario, msg.as_string())
                        successful_sends += 1
                        import time
                        time.sleep(2)
                    except Exception as e:
                        errors.append((email_destinatario, str(e)))
                server.quit()
            except Exception as e:
                errors.append(str(e))
            # Feedback
            if successful_sends == len(email_list):
                flash(f'Sucesso! {successful_sends} emails foram enviados com sucesso.', 'success')
            else:
                flash(f'Parcialmente concluído: {successful_sends} de {len(email_list)} emails foram enviados.', 'warning')
                if errors:
                    for error in errors[:3]:
                        flash(str(error), 'error')
        except Exception as e:
            logging.error(f"Erro no processamento: {str(e)}")
            flash(f'Erro interno: {str(e)}', 'error')
        finally:
            try:
                if os.path.exists(filepath):
                    os.remove(filepath)
                    logging.debug(f"Arquivo temporário removido: {filepath}")
            except Exception as e:
                logging.warning(f"Erro ao remover arquivo temporário: {str(e)}")
        return redirect(url_for('enviar'))
    return render_template('enviar.html', user=current_user, subscription_info=current_user.get_subscription_info())

@app.route('/health')
def health():
    return {'status': 'healthy', 'service': 'flask-mass-email'}, 200