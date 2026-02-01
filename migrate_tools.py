from app import app, db, Tool

def migrate():
    with app.app_context():
        # List of tools to migrate
        tools_data = [
            # Link Tools
            {"name": "Invoice Maker", "desc": "Create professional PDF invoices with automatic calculations.", "icon": "fas fa-file-invoice-dollar", "url": "invoice.html", "cat": "Productivity"},
            {"name": "Snippet Studio", "desc": "Turn your code into beautiful, shareable screenshots.", "icon": "fas fa-code", "url": "codeimage.html", "cat": "Developer"},
            {"name": "Thumbnail Preview", "desc": "Test your YouTube thumbnails against competitors.", "icon": "fas fa-image", "url": "thumbnail.html", "cat": "Content"},
            {"name": "Secret Agent", "desc": "Encrypt messages with Base64, Binary, and self-destruct animations.", "icon": "fas fa-user-secret", "url": "encryptor.html", "cat": "Security"},
            {"name": "Bulk Result Card", "desc": "Auto-generate thousands of Student Marks Cards from Excel.", "icon": "fas fa-file-excel", "url": "result-generator.html", "cat": "School"},
            {"name": "Bulk ID Cards", "desc": "Generate Print-Ready Student ID Cards in A4 Batches.", "icon": "fas fa-id-card", "url": "id-generator.html", "cat": "School"},
            {"name": "Time-Table Manager", "desc": "Weekly scheduler with real-time teacher conflict detection.", "icon": "fas fa-calendar-alt", "url": "timetable.html", "cat": "School"},
            {"name": "Villain Mode", "desc": "Minimalist Pomodoro timer for deep work sessions.", "icon": "fas fa-stopwatch", "url": "timer.html", "cat": "Productivity"},
            {"name": "QR Studio", "desc": "Advanced QR Generator with colors, logos, and vector export.", "icon": "fas fa-qrcode", "url": "qrcode.html", "cat": "Utilities"},
            
            # Interactive/Inline Tools (Managed via specialized rendering or ID matching in frontend)
            {"name": "Ad-Free Player", "desc": "Stream YouTube videos without ads and interruptions.", "icon": "fas fa-play-circle", "url": "#video-tool", "cat": "Media"},
            {"name": "Secure Passwords", "desc": "Generate cryptographically strong passwords instantly.", "icon": "fas fa-lock", "url": "#password-tool", "cat": "Security"},
            {"name": "Net Speed", "desc": "Quickly check your internet latency (simulated).", "icon": "fas fa-tachometer-alt", "url": "#speed-tool", "cat": "Utilities"},
        ]

        print(f"Migrating {len(tools_data)} tools...")
        
        count = 0
        for t in tools_data:
            # Check if exists
            exists = Tool.query.filter_by(name=t['name']).first()
            if not exists:
                new_tool = Tool(
                    name=t['name'],
                    description=t['desc'],
                    icon_url=t['icon'],
                    tool_url=t['url'],
                    category=t['cat'],
                    is_locked=False
                )
                db.session.add(new_tool)
                count += 1
        
        db.session.commit()
        print(f"Successfully added {count} new tools.")

if __name__ == '__main__':
    migrate()
