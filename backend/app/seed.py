from sqlalchemy import select
from .database import Base, engine, SessionLocal
from .models import User, Project, ProjectMember, Task, Comment
from .security import hash_password

Base.metadata.create_all(bind=engine)
db = SessionLocal()
try:
    if db.scalar(select(User.id).limit(1)) is None:
        users = [
            User(name="Olivia Chen", email="admin@northstar.local", password_hash=hash_password("Demo123!"), role="Admin"),
            User(name="Marcus Reed", email="manager@northstar.local", password_hash=hash_password("Demo123!"), role="Project Manager"),
            User(name="Sam Rivera", email="member@northstar.local", password_hash=hash_password("Demo123!"), role="Team Member"),
            User(name="Taylor Brooks", email="viewer@northstar.local", password_hash=hash_password("Demo123!"), role="Viewer"),
        ]
        db.add_all(users); db.flush()
        project = Project(name="Q4 Product Launch", description="Coordinate launch readiness across product, design and growth.", owner_id=users[1].id, status="Active")
        db.add(project); db.flush()
        db.add_all([ProjectMember(project_id=project.id, user_id=users[1].id, role="Project Manager"), ProjectMember(project_id=project.id, user_id=users[2].id, role="Team Member"), ProjectMember(project_id=project.id, user_id=users[3].id, role="Viewer")])
        tasks = [
            Task(project_id=project.id, title="Finalize launch messaging", description="Review the landing page copy and product value proposition.", status="In progress", priority="High", assignee_id=users[2].id, due_date="2026-10-28"),
            Task(project_id=project.id, title="QA onboarding flow", description="Test the first-run experience on desktop and mobile.", status="To do", priority="Medium", assignee_id=users[2].id, due_date="2026-10-29"),
            Task(project_id=project.id, title="Approve release checklist", description="Confirm support, analytics and rollout readiness.", status="Done", priority="Low", assignee_id=users[1].id, due_date="2026-10-21"),
        ]
        db.add_all(tasks); db.flush()
        db.add(Comment(task_id=tasks[0].id, author_id=users[1].id, body="Please share the final draft before Thursday's review."))
        db.commit()
        print("Seeded demo users, project, tasks, and comment.")
    else:
        print("Database already contains users; skipping seed.")
finally:
    db.close()
