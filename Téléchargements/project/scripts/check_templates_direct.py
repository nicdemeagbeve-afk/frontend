import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

base_dir = os.path.dirname(os.path.abspath(__file__))
# assume .env.new is at project root
project_root = os.path.dirname(base_dir)
env_path = os.path.join(project_root, '.env.new')
print('Loading env from', env_path, 'exists=', os.path.exists(env_path))
load_dotenv(env_path)

DATABASE_URL = os.environ.get('DATABASE_URL')
print('DATABASE_URL=', DATABASE_URL)

if not DATABASE_URL:
    print('No DATABASE_URL found in env')
    raise SystemExit(1)

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    try:
        res = conn.execute(text('SELECT COUNT(*) as c FROM template'))
        count = res.scalar()
        print('template count =', count)
        res = conn.execute(text('SELECT id, name, is_active FROM template LIMIT 10'))
        rows = res.fetchall()
        for r in rows:
            print(r)
    except Exception as e:
        print('Error querying template table:', e)
        # Try to list tables
        try:
            r2 = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = DATABASE()"))
            tables = [row[0] for row in r2.fetchall()]
            print('Tables in DB:', tables)
        except Exception as e2:
            print('Also failed to read information_schema:', e2)
