from app import create_app, db
from sqlalchemy.schema import CreateTable
from sqlalchemy.dialects import postgresql

def export_schema():
    app = create_app()
    with app.app_context():
        # Ensure all models are loaded so they are in metadata
        # Importing main models to trigger registration
        from app.models.user import User
        from app.models.course import Course, UserCourse
        from app.models.session import StudySession, ScheduleBlock
        from app.models.broadcast import Broadcast
        from app.models.system_alert import SystemAlert
        # Add any other models if necessary, e.g. AuditLog if it exists

        print("-- Auto-generated Schema for DrawSQL --\n")
        
        # Iterating sorted tables handles foreign key dependency order
        for table in db.metadata.sorted_tables:
            # Compile using PostgreSQL dialect
            create_table_sql = CreateTable(table).compile(dialect=postgresql.dialect())
            
            # Print with semicolon
            print(f"{create_table_sql};")
            print() # Newline for readability

if __name__ == "__main__":
    export_schema()
