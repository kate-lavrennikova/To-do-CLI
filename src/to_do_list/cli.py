import click
from to_do_list.custom_types import DAY
from to_do_list.models import Task, User
from to_do_list.service import TaskService, UserService
from to_do_list.repository import TaskRepository, UserRepository, SessionRepository
from to_do_list.exceptions import SessionHasExpiredException, UserAlreadyExistsExeption, \
    UserNotLoggedInException, DatabaseIsNotInitializedException, DatabaseIsNotAvailableException, TaskNotFoundException
from to_do_list.database import db_init

task_service = TaskService(TaskRepository())
user_service = UserService(UserRepository(), SessionRepository())

@click.group()
def cli():
    """To-do list CLI app"""

@cli.command()
def init():
    """Initialize database"""
    try:
        db_init()
    except DatabaseIsNotAvailableException as e:
        click.echo(e.message)


@cli.command("show")
@click.option("-d", "--day", type = DAY, default="today", help="A day to show. Possible values: today (by default), yesterday, tommorrow, particular day in format YYYY-MM-dd")
@click.option("--done/--not-done", default=None, help="Show only done/not done tasks")
@click.option("--important/--not-important", default=None, help="Show only important/not important items")
def show(day, done, important):
    """Show a list of tasks for a particular day (for today by default)"""
    try:
        user_id = user_service.get_current_user()
        kwargs = {"task_date": day, "user_id": user_id}
        if (done != None):
            kwargs["done"] = done
        if (important != None):
            kwargs["important"] = important
        result = task_service.get_tasks(**kwargs)
        for task in result:
            click.echo(task, nl=True)
        if len(result) == 0:
            click.echo(f"No tasks found for {day}")

    except (SessionHasExpiredException, UserNotLoggedInException, DatabaseIsNotInitializedException, DatabaseIsNotAvailableException) as e:
        click.echo(e.message)

    except:
         click.echo("Something went wrong...")


@cli.command("add")
@click.argument("description")
@click.option("-d", "--day", type = DAY, default="today", help="Possible values: today (by default), yesterday, tommorrow, particular day in format YYYY-MM-dd")
@click.option("--done", is_flag=True, help="Marks task as done")
@click.option("-i", "--important", is_flag=True, help="Marks task as important")
def add(description, day, done, important):
    """Create a task"""
    try:
        if (len(description) > 150):
            click.echo("Too long task. It should contain no more than 150 symbols.")
            return
        user_id = user_service.get_current_user()
        task = Task(task_description=description, task_date=day, done=done, important=important, user_id=user_id)
        task_service.create(task)

    except (SessionHasExpiredException, UserNotLoggedInException, DatabaseIsNotInitializedException, DatabaseIsNotAvailableException) as e:
        click.echo(e.message)

    except:
         click.echo("Something went wrong...")


@cli.command("update")
@click.argument("date_and_id", type=click.Tuple([DAY, int]))
@click.option("-d", "--day", type = DAY, default=None, help="New day for task. Possible values: today (by default), yesterday, tommorrow, particular day in format YYYY-MM-dd")
@click.option("--done/--not-done", default=None, help="Mark task as done/not done")
@click.option("--important/--not-important", default=None, help="Mark task as important/not important")
@click.option("--desc",  help="New description for task")
def update(date_and_id, day, done, important, desc):
    """Update a task by date and id"""
    try:
        if (day == None and done == None and important == None and desc == None):
            click.echo("Define at least one parameter to change")
            return
        if (desc != None and len(desc) > 150):
            click.echo("Too long description. It should contain no more than 150 symbols.")
            return
        user_id = user_service.get_current_user()
        kwargs = {}
        if (day != None):
            kwargs["task_date"] = day
        if (done != None):
            kwargs["done"] = done
        if (important != None):
            kwargs["important"] = important
        if (desc != None):
            kwargs["task_description"] = desc
        task_service.update(date_and_id[0], date_and_id[1], user_id, **kwargs)

    except (SessionHasExpiredException, UserNotLoggedInException, \
            DatabaseIsNotInitializedException, DatabaseIsNotAvailableException, TaskNotFoundException) as e:
        click.echo(e.message)

    except:
         click.echo("Something went wrong...")

@cli.command("delete")
@click.argument("date_and_id", type=click.Tuple([DAY, int]))
def delete(date_and_id):
    """Delete a task by date and id"""
    try:
        user_id = user_service.get_current_user()
        task_service.delete(date_and_id[0], date_and_id[1], user_id)

    except (SessionHasExpiredException, UserNotLoggedInException, \
            DatabaseIsNotInitializedException, DatabaseIsNotAvailableException, TaskNotFoundException) as e:
        click.echo(e.message)

    except:
        click.echo("Something went wrong...")

@cli.command("create-user")
@click.option("--username", prompt="Username")
@click.password_option("--password", prompt="Password")
def create_user(username, password):
    """Create new user"""
    try:
        user = User(user_name=username, user_password=password)
        user_service.create(user)
        click.echo("User successfully created!")
    except (UserAlreadyExistsExeption, DatabaseIsNotInitializedException, DatabaseIsNotAvailableException) as e:
        click.echo(e.message)

@cli.command("login")
@click.option("--username", prompt="Username")
@click.option("--password", prompt="Password", hide_input=True)
def login(username, password):
    """Log in"""
    try:
        if user_service.login(username.strip(), password.strip()):
            click.echo(f"Welcome, {username}!")
        else: click.echo(f"Wrong username or password")
    except (DatabaseIsNotInitializedException, DatabaseIsNotAvailableException) as e:
        click.echo(e.message)


@cli.command("logout")
def logout():
    """Log out"""
    try:
        user_service.logout()
        if click.confirm(f"Are you sure?"):
            user_service.logout()
            click.echo(f"You successfully logged out.")
        else:
            click.echo("Aborted!")
    except (DatabaseIsNotInitializedException, DatabaseIsNotAvailableException) as e:
        click.echo(e.message)
