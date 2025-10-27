from app import create_app, db
from app.models import Template

app = create_app()

with app.app_context():
    print("SQLALCHEMY_DATABASE_URI:", app.config.get('SQLALCHEMY_DATABASE_URI'))
    try:
        templates = Template.query.all()
        print(f"Found {len(templates)} templates")
        for t in templates:
            print(f"- {t.id}: {t.name} (active={t.is_active})")
    except Exception as e:
        print("Error querying Template:", e)
