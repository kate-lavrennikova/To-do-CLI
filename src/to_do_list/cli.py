import click
from sqlalchemy.exc import ProgrammingError, OperationalError, IntegrityError
from .custom_types import DAY
from .models import Task, User
from .service import TaskService, UserService
from .repository import TaskRepository, UserRepository, SessionRepository
from .exceptions import SessionHasExpiredException, UserNotLoggedInException, TaskNotFoundException
from .database import db_init, Session



user_service = UserService(UserRepository(), SessionRepository())
task_service = TaskService(TaskRepository())

@click.group()
def cli():
    """To-do list CLI app"""

@cli.command()
def init():
    """Initialize database"""
    try:
        db_init()
    except OperationalError:
        click.echo("Lost connection with database")


@cli.command("show")
@click.option("-d", "--day", type = DAY, default="today", help="A day to show. Possible values: today (by default), yesterday, tommorrow, particular day in format YYYY-MM-dd")
@click.option("--done/--not-done", default=None, help="Show only done/not done tasks")
@click.option("--important/--not-important", default=None, help="Show only important/not important items")
def show(day, done, important):
    """Show a list of tasks for a particular day (for today by default)"""
    try:
        with Session() as session:
            try:
                user_id = user_service.get_current_user(session)
                kwargs = {"task_date": day, "user_id": user_id}
                if (done != None):
                    kwargs["done"] = done
                if (important != None):
                    kwargs["important"] = important
                result = task_service.get_tasks(session, **kwargs)
                for task in result:
                    click.echo(task, nl=True)
                if len(result) == 0:
                    click.echo(f"No tasks found for {day}")
            except SessionHasExpiredException as e:
                user_service.logout(session)
                session.commit()
                click.echo(e.message)
            except (UserNotLoggedInException) as e:
                click.echo(e.message)
    except ProgrammingError:
        click.echo("Please initialize database first. Use command 'todo init'")
    except OperationalError:
        click.echo("Lost connection with database")

@cli.command("add")
@click.argument("description")
@click.option("-d", "--day", type = DAY, default="today", help="Possible values: today (by default), yesterday, tommorrow, particular day in format YYYY-MM-dd")
@click.option("--done", is_flag=True, help="Marks task as done")
@click.option("-i", "--important", is_flag=True, help="Marks task as important")
def add(description, day, done, important):
    """Create a task"""
    try: 
        with Session() as session:
            try:
                if (len(description) > 150):
                    click.echo("Too long task. It should contain no more than 150 symbols.")
                    return
                user_id = user_service.get_current_user(session)
                task = Task(task_description=description, task_date=day, done=done, important=important, user_id=user_id)
                task_service.create(session, task)
                session.commit()    
            except SessionHasExpiredException as e:
                user_service.logout(session)
                session.commit()
                click.echo(e.message)
            except (UserNotLoggedInException) as e: 
                click.echo(e.message)
    except ProgrammingError:
        click.echo("Please initialize database first. Use command 'todo init'")
    except OperationalError:
        click.echo("Lost connection with database")


@cli.command("update")
@click.argument("date_and_id", type=click.Tuple([DAY, int]))
@click.option("-d", "--day", type = DAY, default=None, help="New day for task. Possible values: today (by default), yesterday, tommorrow, particular day in format YYYY-MM-dd")
@click.option("--done/--not-done", default=None, help="Mark task as done/not done")
@click.option("--important/--not-important", default=None, help="Mark task as important/not important")
@click.option("--desc",  help="New description for task")
def update(date_and_id, day, done, important, desc):
    """Update a task by date and id"""
    try:
        with Session() as session:
            if (day == None and done == None and important == None and desc == None):
                click.echo("Define at least one parameter to change")
                return
            if (desc != None and len(desc) > 150):
                click.echo("Too long description. It should contain no more than 150 symbols.")
                return
            try:
                user_id = user_service.get_current_user(session)
                kwargs = {}
                if (day != None):
                    kwargs["task_date"] = day
                if (done != None):
                    kwargs["done"] = done
                if (important != None):
                    kwargs["important"] = important
                if (desc != None):
                    kwargs["task_description"] = desc
                task_service.update(session, date_and_id[0], date_and_id[1], user_id, **kwargs)
                session.commit()
            except SessionHasExpiredException as e:
                user_service.logout()
                session.commit()
                click.echo(e.message)
            except (UserNotLoggedInException, TaskNotFoundException) as e:
                click.echo(e.message)
    except ProgrammingError:
        click.echo("Please initialize database first. Use command 'todo init'")
    except OperationalError:
        click.echo("Lost connection with database")

@cli.command("delete")
@click.argument("date_and_id", type=click.Tuple([DAY, int]))
def delete(date_and_id):
    """Delete a task by date and id"""
    try:
        with Session() as session:
            try:
                user_id = user_service.get_current_user(session)
                task_service.delete(session, date_and_id[0], date_and_id[1], user_id)
                session.commit()
            except SessionHasExpiredException as e:
                user_service.logout()
                session.commit()
                click.echo(e.message)
            except (UserNotLoggedInException, TaskNotFoundException) as e:
                click.echo(e.message)
    except ProgrammingError:
        click.echo("Please initialize database first. Use command 'todo init'")
    except OperationalError:
        click.echo("Lost connection with database")

@cli.command("create-user")
@click.option("--username", prompt="Username")
@click.password_option("--password", prompt="Password")
def create_user(username, password):
    """Create new user"""
    try:
        with Session() as session:
            try:
                user = User(user_name=username, user_password=password)
                user_service.create(session, user)
                session.commit()
                click.echo("User successfully created!")
            except IntegrityError:
                session.rollback()
                click.echo(f"User '{username} already exists'")
    except ProgrammingError:
        click.echo("Please initialize database first. Use command 'todo init'")
    except OperationalError:
        click.echo("Lost connection with database")


@cli.command("login")
@click.option("--username", prompt="Username")
@click.option("--password", prompt="Password", hide_input=True)
def login(username, password):
    """Log in"""
    try:
        with Session() as session:
            if user_service.login(session, username.strip(), password.strip()):
                click.echo(f"Welcome, {username}!")
            else: click.echo(f"Wrong username or password")
            session.commit()
    except (ProgrammingError):
        click.echo("Please initialize database first. Use command 'todo init'")
    except(OperationalError):
        click.echo("Lost connection with database")


@cli.command("logout")
def logout():
    """Log out"""
    try:
        with Session() as session:     
            try: 
                user_service.get_current_user(session)
                if click.confirm(f"Are you sure?"):
                    user_service.logout(session)
                    click.echo(f"You successfully logged out.")
                    session.commit()
                else:
                    click.echo("Aborted!")
            except UserNotLoggedInException:
                click.echo("You need to log in first")
    except (ProgrammingError):
        click.echo("Please initialize database first. Use command 'todo init'")
    except(OperationalError):
        click.echo("Lost connection with database")
