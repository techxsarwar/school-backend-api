from app import app, db
from models import PricingPlan

with app.app_context():
    print("Dropping pricing_plans table...")
    PricingPlan.__table__.drop(db.engine)
    print("Creating all tables (including new pricing_plans)...")
    db.create_all()
    print("Database schema fixed!")
