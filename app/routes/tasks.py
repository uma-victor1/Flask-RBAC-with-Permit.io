from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from ..models.models import Task, User
from ..extensions import db
from ..utils.permit_helper import check_permission, get_permit
from datetime import datetime

tasks = Blueprint("tasks", __name__, url_prefix="/tasks")


@tasks.route("/")
@login_required
@check_permission(action="readall", resource="task")
async def list_tasks():
    """List tasks based on permissions"""
    try:
        permit = get_permit()
        # Check for readall permission instead of role
        has_readall = await permit.check(
            str(current_user.id), "readall", {"type": "task"}
        )

        if has_readall:
            tasks = Task.query.all()
        else:
            tasks = Task.query.filter_by(user_id=current_user.id).all()

        return render_template("tasks/list.html", tasks=tasks)
    except Exception as e:
        flash("Error loading tasks.", "danger")
        return redirect(url_for("main.index"))


@tasks.route("/create", methods=["GET", "POST"])
@login_required
@check_permission(action="create", resource="task")
async def create_task():
    """Create a new task"""
    if request.method == "POST":
        try:
            task = Task(
                title=request.form.get("title"),
                description=request.form.get("description"),
                due_date=datetime.strptime(request.form.get("due_date"), "%Y-%m-%d")
                if request.form.get("due_date")
                else None,
                priority=request.form.get("priority", "medium"),
                user_id=current_user.id,
            )

            # Check if user can assign tasks to others
            permit = get_permit()
            can_assign = await permit.check(
                str(current_user.id), "assign", {"type": "task"}
            )

            if can_assign and request.form.get("assigned_to"):
                task.assigned_to = request.form.get("assigned_to")

            db.session.add(task)
            db.session.commit()
            flash("Task created successfully!", "success")
            return redirect(url_for("tasks.list_tasks"))
        except Exception as e:
            db.session.rollback()
            flash("Error creating task.", "danger")
            return redirect(url_for("tasks.create_task"))

    # Get users list based on assignment permission
    permit = get_permit()
    can_assign = await permit.check(str(current_user.id), "create", {"type": "task"})
    users = User.query.all() if can_assign else [current_user]

    return render_template("tasks/create.html", users=users)


@tasks.route("/<int:id>")
@login_required
@check_permission(action="read", resource="task")
async def view_task(id):
    """View a specific task"""
    task = Task.query.get_or_404(id)

    # Check readall permission or ownership
    permit = get_permit()
    has_readall = await permit.check(str(current_user.id), "readall", {"type": "task"})

    if not has_readall and task.user_id != current_user.id:
        abort(403)

    return render_template("tasks/view.html", task=task)


@tasks.route("/<int:id>/edit", methods=["GET", "POST"])
@login_required
@check_permission(action="update", resource="task")
async def edit_task(id):
    """Edit a task"""
    task = Task.query.get_or_404(id)
    permit = get_permit()

    # Check updateany permission
    has_updateany = await permit.check(
        str(current_user.id), "updateany", {"type": "task"}
    )

    if not has_updateany and task.user_id != current_user.id:
        abort(403)

    if request.method == "POST":
        try:
            task.title = request.form.get("title")
            task.description = request.form.get("description")
            task.due_date = (
                datetime.strptime(request.form.get("due_date"), "%Y-%m-%d")
                if request.form.get("due_date")
                else None
            )
            task.priority = request.form.get("priority", "medium")
            task.status = request.form.get("status", "pending")

            # Check assignment permission
            can_assign = await permit.check(
                str(current_user.id), "update", {"type": "task"}
            )

            if can_assign and request.form.get("assigned_to"):
                task.assigned_to = request.form.get("assigned_to")

            db.session.commit()
            flash("Task updated successfully!", "success")
            return redirect(url_for("tasks.view_task", id=id))
        except Exception as e:
            db.session.rollback()
            flash("Error updating task.", "danger")
            return redirect(url_for("tasks.edit_task", id=id))

    # Get users list based on assignment permission
    can_assign = await permit.check(str(current_user.id), "assign", {"type": "task"})
    users = User.query.all() if can_assign else [current_user]

    return render_template("tasks/edit.html", task=task, users=users)


@tasks.route("/<int:id>/delete", methods=["POST"])
@login_required
@check_permission(action="delete", resource="task")
async def delete_task(id):
    """Delete a task"""
    task = Task.query.get_or_404(id)
    permit = get_permit()

    # Check deleteany permission or ownership
    has_deleteany = await permit.check(
        str(current_user.id), "deleteany", {"type": "task"}
    )

    if not has_deleteany and task.user_id != current_user.id:
        abort(403)

    try:
        db.session.delete(task)
        db.session.commit()
        flash("Task deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash("Error deleting task.", "danger")

    return redirect(url_for("tasks.list_tasks"))


@tasks.route("/dashboard")
@login_required
@check_permission(action="readall", resource="task")
async def dashboard():
    """Admin dashboard showing all tasks"""
    tasks = Task.query.join(User, Task.user_id == User.id).all()

    # Calculate statistics
    total_tasks = len(tasks)
    pending_tasks = sum(1 for task in tasks if task.status == "pending")
    completed_tasks = sum(1 for task in tasks if task.status == "completed")

    # Get statistics by user
    users = User.query.all()
    user_stats = []
    for user in users:
        user_tasks = [task for task in tasks if task.user_id == user.id]
        user_stats.append(
            {
                "username": user.username,
                "total_tasks": len(user_tasks),
                "pending_tasks": sum(
                    1 for task in user_tasks if task.status == "pending"
                ),
                "completed_tasks": sum(
                    1 for task in user_tasks if task.status == "completed"
                ),
            }
        )

    return render_template(
        "tasks/dashboard.html",
        tasks=tasks,
        total_tasks=total_tasks,
        pending_tasks=pending_tasks,
        completed_tasks=completed_tasks,
        user_stats=user_stats,
    )
