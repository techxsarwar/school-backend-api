from app import app, db
from models import PricingPlan

with app.app_context():
    # If not seeded, we might need to query first to trigger the seeding in app.py's context?
    # No, app.py runs on import, but the with app.app_context() block at the bottom of app.py runs immediately.
    # The first time app.py was imported by reset_pricing.py, the table wasn't dropped yet (or it was, but the seeding logic ran BEFORE the drop/create in reset_pricing).
    # Wait. reset_pricing.py:
    # 1. imports app (runs app.py top-to-bottom). 
    # 2. app.py lines 166+ run immediately. If table exists, count > 0, no seeding.
    # 3. reset_pricing.py then drops table and recreates it. Table is now empty.
    # 4. Process exits.
    
    # So now, if we run THIS script:
    # 1. imports app. app.py runs top-to-bottom.
    # 2. app.py lines 166+ run. Table exists (created by reset_pricing.py). Count is 0 (because we dropped and recreated empty).
    # 3. Seeding logic runs!
    # 4. We can then query to verify.
    
    # Effectively, simply running this script should trigger the seed and let us check.
    
    plans = PricingPlan.query.all()
    print(f"Total Plans Found: {len(plans)}")
    for p in plans:
        print(f"- {p.name}: {p.price.encode('ascii', 'ignore').decode()} (Featured: {p.is_featured})")
