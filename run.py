"""
AutoVision.AI - Single Launcher
=================================
Chay file nay de khoi dong toan bo project:
  python run.py

Lan dau chay se tu dong:
  1. Cai thu vien
  2. Setup database (SQL Server)
  3. Train model AI
  4. Khoi dong web server

Mo trinh duyet tai: http://localhost:5000
"""
import subprocess
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(BASE_DIR, 'backend')

def install_deps():
    """Install Python dependencies"""
    try:
        import flask, sklearn, pandas
    except ImportError:
        print('[1/3] Installing dependencies...')
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', '-r',
            os.path.join(BACKEND_DIR, 'requirements.txt'), '--quiet'
        ])
        print('  Done!')
        return
    print('[1/3] Dependencies OK')

def setup_database():
    """Setup SQL Server database (optional)"""
    print('[2/3] Setting up SQL Server...')
    try:
        import pyodbc
        result = subprocess.run(
            [sys.executable, os.path.join(BACKEND_DIR, 'setup_database.py')],
            capture_output=True, text=True, cwd=BACKEND_DIR
        )
        if result.returncode == 0:
            print('  SQL Server OK!')
            for line in result.stdout.strip().split('\n')[-3:]:
                print(f'  {line}')
        else:
            print('  SQL Server not available, using CSV fallback.')
    except ImportError:
        print('  pyodbc not installed, using CSV fallback.')

def train_model():
    """Train ML model if not exists"""
    model_path = os.path.join(BACKEND_DIR, 'model', 'car_price_model.pkl')
    if os.path.exists(model_path):
        print('[3/3] Model already trained')
        return
    
    print('[3/3] Training AI model...')
    result = subprocess.run(
        [sys.executable, os.path.join(BACKEND_DIR, 'model', 'train_model.py')],
        capture_output=True, text=True, cwd=BACKEND_DIR
    )
    if result.returncode == 0:
        for line in result.stdout.strip().split('\n')[-4:]:
            print(f'  {line}')
    else:
        print(f'  Error: {result.stderr}')

def start_server():
    """Start Flask server"""
    print('\n=== AutoVision.AI ===')
    print('Open:  http://localhost:5000')
    print('Press Ctrl+C to stop')
    print('====================\n')
    
    os.chdir(BACKEND_DIR)
    subprocess.call([sys.executable, 'app.py'])

if __name__ == '__main__':
    print('AutoVision.AI - Starting...\n')
    install_deps()
    setup_database()
    train_model()
    start_server()
