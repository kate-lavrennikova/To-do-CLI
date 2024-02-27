import click
from to_do_list.custom_types import DAY
from to_do_list.models import Task, User
from to_do_list.service import TaskService, UserService
from to_do_list.repository import TaskRepository, UserRepository, SessionRepository
from to_do_list.exceptions import SessionHasExpiredException
from to_do_list.database import db_init

task_service = TaskService(TaskRepository())
user_service = UserService(UserRepository(), SessionRepository())

@click.group()
def cli():
    """To-do list CLI app"""

@cli.command()
def init():
    """Initialize database"""
    db_init()    

@cli.command("list")
@click.option("-d", "--day", type = DAY, default="today", help="A day to show. Possible values: today (by default), yesterday, tommorrow, particular day in format YYYY-MM-dd")
@click.option("--done/--not-done", default=None, help="Show only done/not done tasks")
@click.option("--important/--not-important", default=None, help="Show only important/not important items")
def list(day, done, important):
    """Show a list of tasks for a particular day (for today by default)"""
    try:
        user_id = user_service.get_current_user()
        kwargs = {"task_date": day, "user_id": user_id}
        if (done != None):
            kwargs["done"] = done
        if (important != None):
            kwargs["important"] = important
        result = task_service.get_filtered(**kwargs)
        for task in result:
            click.echo(task, nl=True)
        if len(result) == 0:
            click.echo(f"No tasks found for {day}")

    except SessionHasExpiredException as e:
        click.echo(e.message)

    # except:
    #     click.echo("Please login to see the list of tasks")


@cli.command("add")
@click.argument("description")
@click.option("-d", "--day", type = DAY, default="today", help="Possible values: today (by default), yesterday, tommorrow, particular day in format YYYY-MM-dd")
@click.option("--done", is_flag=True, help="Marks task as done")
@click.option("-i", "--important", is_flag=True, help="Marks task as important")
def add(description, day, done, important):
    """Create a task"""
    try:
        user_id = user_service.get_current_user()
        task = Task(task_description=description, task_date=day, done=done, important=important, user_id=user_id)
        task_service.create(task)

    except SessionHasExpiredException as e:
        click.echo(e.message)

    # except:
    #     click.echo("Please login to add a tasks")


@cli.command("update")
@click.argument("date_and_fake_id", type=click.Tuple([DAY, int]))
@click.option("-d", "--day", type = DAY, default=None, help="New day for task. Possible values: today (by default), yesterday, tommorrow, particular day in format YYYY-MM-dd")
@click.option("--done/--not-done", default=None, help="Mark task as done/not done")
@click.option("--important/--not-important", default=None, help="Mark task as important/not important")
@click.option("--desc",  help="New description for task")
def update(date_and_fake_id, day, done, important, desc):
    """Update a task by id"""
    try:
        if (day == None and done == None and important == None and desc == None):
            click.echo("Define at least one parameter to change")
            return
        user_id = user_service.get_current_user()
        kwargs = {}
        if (day != None):
            kwargs["task_date"] = day
        if (done != None):
            kwargs["done"] = done
        if (important != None):
            kwargs["important"] = important
        if (important != None):
            kwargs["description"] = desc
        task_service.update(date_and_fake_id[0], date_and_fake_id[1], user_id, **kwargs)

    except SessionHasExpiredException as e:
        click.echo(e.message)

    # except:
    #     click.echo("Please login to update a tasks")

@cli.command("delete")
@click.argument("date_and_fake_id", type=click.Tuple([DAY, int]))
def delete(date_and_fake_id):
    """Delete a task by date and id"""
    try:
        user_id = user_service.get_current_user()
        task_service.delete(date_and_fake_id[0], date_and_fake_id[1], user_id)

    except SessionHasExpiredException as e:
        click.echo(e.message)
    # except:
    #     click.echo("Please login to delete a tasks")

@cli.command("create-user")
@click.option("--username", prompt="Username")
@click.password_option("--password", prompt="Password")
def create_user(username, password):
    """Create new user"""
    user = User(user_name=username, user_password=password)
    user_service.create(user)
    click.echo("User successfully created!")

@cli.command("login")
@click.option("--username", prompt="Username")
@click.option("--password", prompt="Password", hide_input=True)
def login(username, password):
    """Log in"""
    try:
        if user_service.login(username.strip(), password.strip()):
            click.echo(f"Welcome, {username}!")
        else: click.echo(f"Wrong username or password")
    except:
        click.echo("Initialize db first. Use command 'init'")


@cli.command("logout")
def logout():
    """Log out"""
    user_service.logout()
    if click.confirm(f"Are you sure?"):
        user_service.logout()
        click.echo(f"You successfully logged out.")
    else:
        click.echo("Aborted!")