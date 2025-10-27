import os
from dotenv import load_dotenv

# Obtenir le chemin absolu du fichier .env
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_file = os.path.join(base_dir, '.env')

print(f"Base directory: {base_dir}")
print(f"Looking for .env file at: {env_file}")
print(f"File exists: {os.path.exists(env_file)}")

# Charger les variables d'environnement
load_dotenv(env_file)

print("\nEnvironment variables:")
print("--------------------")
print("DATABASE_URL:", os.environ.get('DATABASE_URL'))
print("FLASK_ENV:", os.environ.get('FLASK_ENV'))
print("DB_TYPE:", os.environ.get('DB_TYPE'))
print("DB_HOST:", os.environ.get('DB_HOST'))

print("DATABASE_URL:", os.environ.get('DATABASE_URL'))
print("FLASK_ENV:", os.environ.get('FLASK_ENV'))
print("DB_TYPE:", os.environ.get('DB_TYPE'))
print("DB_HOST:", os.environ.get('DB_HOST'))