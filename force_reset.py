from app import app, db
from sqlalchemy import text

with app.app_context():
    print("Dropping old pricing table...")
    try:
        # distinct commit to ensure drop happens before create in case of transaction weirdness
        db.session.execute(text("DROP TABLE IF EXISTS pricing_plans;"))
        db.session.commit()
        print("Dropped.")
    except Exception as e:
        print(f"Error dropping table: {e}")
        db.session.rollback()

    print("Recreating table with new columns (border_color, has_timer, etc.)...")
    db.create_all()
    print("Success! Table reset.")
