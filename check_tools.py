from app import app, db, Tool

def check():
    with app.app_context():
        tools = Tool.query.all()
        print(f"Total Tools in DB: {len(tools)}")
        print("-" * 30)
        for t in tools:
            status = 'Locked' if t.is_locked else 'Unlocked'
            print(f"[{t.id}] {t.name} ({status})")

if __name__ == '__main__':
    check()
