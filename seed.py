from app import create_app, db
from app.models import User, FinancialRecord
from app.config import Config
import datetime
import random

app = create_app()

def seed_database():
    with app.app_context():
        print("Cleaning up old data...")
        db.drop_all()
        db.create_all()

        print("Seeding admin user...")
        # Create Admin
        admin = User(
            name="Admin User",
            email="admin@finance.app",
            role="admin"
        )
        admin.set_password("admin123")
        
        # Create Analyst
        analyst = User(
            name="Data Analyst",
            email="analyst@finance.app",
            role="analyst"
        )
        analyst.set_password("analyst123")

        # Create Viewer
        viewer = User(
            name="Normal Viewer",
            email="viewer@finance.app",
            role="viewer"
        )
        viewer.set_password("viewer123")

        db.session.add_all([admin, analyst, viewer])
        db.session.commit()
        
        print("Seeding sample financial records...")
        categories_expense = ["Food & Dining", "Rent", "Transportation", "Entertainment", "Utilities"]
        categories_income = ["Salary", "Freelance", "Investment"]
        
        records = []
        # Generate some random records for the past 30 days
        for i in range(25):
            is_income = random.choice([True, False, False]) # More expenses than income
            
            record_type = "income" if is_income else "expense"
            category = random.choice(categories_income) if is_income else random.choice(categories_expense)
            amount = round(random.uniform(500, 5000) if is_income else random.uniform(20, 500), 2)
            
            # Days ago
            days_ago = random.randint(0, 30)
            date = datetime.datetime.now() - datetime.timedelta(days=days_ago)
            
            record = FinancialRecord(
                user_id=admin.id,
                amount=amount,
                record_type=record_type,
                category=category,
                description=f"Sample {record_type} for {category}",
                date=date.date()
            )
            records.append(record)
            
        db.session.add_all(records)
        db.session.commit()
        
        print("Database seeded successfully!")
        print("-" * 30)
        print("Credentials for testing:")
        print("Admin: admin@finance.app / admin123")
        print("Analyst: analyst@finance.app / analyst123")
        print("Viewer: viewer@finance.app / viewer123")

if __name__ == '__main__':
    seed_database()
