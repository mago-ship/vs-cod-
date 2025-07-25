# Arquivo main.py - Ponto de entrada para execução local
# Para produção com Gunicorn, use: gunicorn app:app

from app import app

if __name__ == '__main__':
    # Execução local (não use debug=True em produção)
    app.run(host='0.0.0.0', port=5000, debug=True)