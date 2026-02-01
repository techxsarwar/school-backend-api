from app import app, db
from models import PricingPlan

with app.app_context():
    print("Dropping pricing_plans table...")
    PricingPlan.__table__.drop(db.engine)
    print("Recreating pricing_plans table...")
    db.create_all()
    print("Pricing Plans table reset success.")
