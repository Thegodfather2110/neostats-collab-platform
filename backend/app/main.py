import os
from fastapi import FastAPI, Depends, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, update
from sqlalchemy.orm import Session, joinedload
from .database import Base, engine, get_db
from .models import User, Project, ProjectMember, Task, Comment
from .schemas import LoginIn, ProjectIn, TaskIn, TaskUpdate, CommentIn
from .security import current_user, verify_password, create_token, require_roles

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Northstar Project API", version="1.0.0")
configured_origins = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000,http://127.0.0.1:3000")
allowed_origins = [origin.strip() for origin in configured_origins.split(",") if origin.strip()]
allowed_origins.extend(["http://localhost:3000", "http://127.0.0.1:3000", "http://[::1]:3000"])
allowed_origins = list(dict.fromkeys(allowed_origins))
app.add_middleware(CORSMiddleware, allow_origins=allowed_origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "northstar-api"}

@app.post("/api/auth/login")
def login(data: LoginIn, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == data.email.lower()))
    if not user or not user.active or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Email or password is incorrect.")
    return {"access_token": create_token(user), "token_type": "bearer", "user": {"id": user.id, "name": user.name, "email": user.email, "role": user.role}}

@app.get("/api/auth/me")
def me(user: User = Depends(current_user)):
    return {"id": user.id, "name": user.name, "email": user.email, "role": user.role}

def can_view_project(db: Session, user: User, project_id: int) -> bool:
    if user.role == "Admin": return True
    if user.role == "Project Manager":
        project = db.get(Project, project_id)
        return bool(project and (project.owner_id == user.id or db.scalar(select(ProjectMember.id).where(ProjectMember.project_id == project_id, ProjectMember.user_id == user.id))))
    return db.scalar(select(ProjectMember.id).where(ProjectMember.project_id == project_id, ProjectMember.user_id == user.id)) is not None

def can_manage_project(db: Session, user: User, project_id: int) -> bool:
    if user.role == "Admin": return True
    project = db.get(Project, project_id)
    return bool(user.role == "Project Manager" and project and (project.owner_id == user.id or db.scalar(select(ProjectMember.id).where(ProjectMember.project_id == project_id, ProjectMember.user_id == user.id, ProjectMember.role == "Project Manager"))))

def project_dict(p: Project, db: Session):
    tasks = db.scalars(select(Task).where(Task.project_id == p.id)).all()
    return {"id": p.id, "name": p.name, "description": p.description, "status": p.status, "owner_id": p.owner_id, "member_count": len(p.members), "task_count": len(tasks), "completed_count": sum(t.status == "Done" for t in tasks)}

def task_dict(t: Task):
    return {"id": t.id, "project_id": t.project_id, "title": t.title, "description": t.description, "status": t.status, "priority": t.priority, "assignee_id": t.assignee_id, "assignee": t.assignee.name if t.assignee else None, "due_date": t.due_date, "version": t.version, "updated_at": t.updated_at.isoformat() if t.updated_at else None}

@app.get("/api/projects")
def list_projects(db: Session = Depends(get_db), user: User = Depends(current_user)):
    projects = db.scalars(select(Project).options(joinedload(Project.members)).order_by(Project.created_at.desc())).unique().all()
    return [project_dict(p, db) for p in projects if can_view_project(db, user, p.id)]

@app.post("/api/projects", status_code=201)
def create_project(data: ProjectIn, db: Session = Depends(get_db), user: User = Depends(require_roles("Admin", "Project Manager"))):
    p = Project(name=data.name.strip(), description=data.description.strip(), owner_id=user.id)
    db.add(p); db.flush()
    db.add(ProjectMember(project_id=p.id, user_id=user.id, role=user.role))
    db.commit(); db.refresh(p)
    return project_dict(p, db)

@app.get("/api/projects/{project_id}")
def get_project(project_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    p = db.get(Project, project_id)
    if not p: raise HTTPException(404, "Project not found.")
    if not can_view_project(db, user, project_id): raise HTTPException(403, "You cannot access this project.")
    return project_dict(p, db)

@app.post("/api/projects/{project_id}/members/{user_id}", status_code=201)
def add_member(project_id: int, user_id: int, role: str = "Team Member", db: Session = Depends(get_db), user: User = Depends(current_user)):
    if not can_manage_project(db, user, project_id): raise HTTPException(403, "Only the project manager or admin can manage members.")
    target = db.get(User, user_id)
    if not target or not target.active: raise HTTPException(404, "Active user not found.")
    if role not in ["Project Manager", "Team Member", "Viewer"]: raise HTTPException(422, "Invalid project role.")
    existing = db.scalar(select(ProjectMember).where(ProjectMember.project_id == project_id, ProjectMember.user_id == user_id))
    if existing: existing.role = role
    else: db.add(ProjectMember(project_id=project_id, user_id=user_id, role=role))
    db.commit(); return {"ok": True}

@app.get("/api/tasks")
def list_tasks(project_id: int | None = None, db: Session = Depends(get_db), user: User = Depends(current_user)):
    stmt = select(Task).options(joinedload(Task.assignee)).order_by(Task.updated_at.desc())
    if project_id is not None: stmt = stmt.where(Task.project_id == project_id)
    tasks = db.scalars(stmt).unique().all()
    return [task_dict(t) for t in tasks if can_view_project(db, user, t.project_id) and (user.role != "Team Member" or t.assignee_id == user.id or project_id is not None)]

@app.post("/api/tasks", status_code=201)
def create_task(data: TaskIn, db: Session = Depends(get_db), user: User = Depends(current_user)):
    if not can_manage_project(db, user, data.project_id): raise HTTPException(403, "Only the project manager or admin can create tasks.")
    if data.status not in ["To do", "In progress", "In review", "Done"]: raise HTTPException(422, "Invalid task status.")
    t = Task(**data.model_dump()); db.add(t); db.commit(); db.refresh(t)
    return task_dict(db.scalar(select(Task).options(joinedload(Task.assignee)).where(Task.id == t.id)))

@app.patch("/api/tasks/{task_id}")
def update_task(task_id: int, data: TaskUpdate, db: Session = Depends(get_db), user: User = Depends(current_user)):
    t = db.get(Task, task_id)
    if not t: raise HTTPException(404, "Task not found.")
    if not can_view_project(db, user, t.project_id): raise HTTPException(403, "You cannot access this task.")
    if user.role == "Viewer": raise HTTPException(403, "Viewer access is read-only.")
    if user.role == "Team Member" and t.assignee_id != user.id: raise HTTPException(403, "Team members can update only their assigned tasks.")
    changes = data.model_dump(exclude={"version"}, exclude_unset=True)
    if "status" in changes and changes["status"] not in ["To do", "In progress", "In review", "Done"]: raise HTTPException(422, "Invalid task status.")
    result = db.execute(update(Task).where(Task.id == task_id, Task.version == data.version).values(**changes, version=Task.version + 1))
    if result.rowcount == 0:
        db.rollback(); raise HTTPException(status_code=409, detail="This task changed since you opened it. Refresh and review the latest version.")
    db.commit()
    fresh = db.scalar(select(Task).options(joinedload(Task.assignee)).where(Task.id == task_id))
    return task_dict(fresh)

@app.delete("/api/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    t = db.get(Task, task_id)
    if not t: raise HTTPException(404, "Task not found.")
    if not can_manage_project(db, user, t.project_id): raise HTTPException(403, "Only the project manager or admin can delete tasks.")
    db.delete(t); db.commit(); return Response(status_code=204)

@app.get("/api/tasks/{task_id}/comments")
def list_comments(task_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    t = db.get(Task, task_id)
    if not t: raise HTTPException(404, "Task not found.")
    if not can_view_project(db, user, t.project_id): raise HTTPException(403, "You cannot access this task.")
    comments = db.scalars(select(Comment).options(joinedload(Comment.author)).where(Comment.task_id == task_id).order_by(Comment.created_at)).unique().all()
    return [{"id": c.id, "body": c.body, "author": c.author.name, "created_at": c.created_at.isoformat()} for c in comments]

@app.post("/api/tasks/{task_id}/comments", status_code=201)
def add_comment(task_id: int, data: CommentIn, db: Session = Depends(get_db), user: User = Depends(current_user)):
    t = db.get(Task, task_id)
    if not t: raise HTTPException(404, "Task not found.")
    if not can_view_project(db, user, t.project_id): raise HTTPException(403, "You cannot access this task.")
    c = Comment(task_id=task_id, author_id=user.id, body=data.body.strip()); db.add(c); db.commit(); db.refresh(c)
    return {"id": c.id, "body": c.body, "author": user.name, "created_at": c.created_at.isoformat()}

@app.delete("/api/comments/{comment_id}", status_code=204)
def delete_comment(comment_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    c = db.get(Comment, comment_id)
    if not c: raise HTTPException(404, "Comment not found.")
    if c.author_id != user.id and user.role != "Admin": raise HTTPException(403, "You can delete only your own comments.")
    db.delete(c); db.commit(); return Response(status_code=204)

@app.get("/api/users")
def list_users(db: Session = Depends(get_db), user: User = Depends(require_roles("Admin"))):
    return [{"id": u.id, "name": u.name, "email": u.email, "role": u.role, "active": u.active} for u in db.scalars(select(User).order_by(User.name)).all()]
