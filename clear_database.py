from app import app, db, Resource

with app.app_context():
    # Delete all resources
    Resource.query.delete()
    db.session.commit()
    print("Database cleared successfully!")
