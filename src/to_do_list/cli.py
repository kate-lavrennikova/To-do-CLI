import click
from to_do_list.custom_types import DAY
from to_do_list.models import Task, User
from to_do_list.service import TaskService, UserService
from to_do_list.repository import TaskRepository, UserRepository, SessionRepository
from to_do_list.exceptions import SessionHasExpiredException


task_service = TaskService(TaskRepository())
user_service = UserService(UserRepository(), SessionRepository())

@click.group()
def cli():
    """To-do list CLI app"""

@cli.command("list")
@click.option("-d", "--day", type = DAY, default="today", help="A day to show. Possible values: today (by default), yesterday, tommorrow, particular day in format YYYY-MM-dd")
@click.option("--done/--not-done", default=None, help="Show only done/not done tasks")
@click.option("--important/--not-important", default=None, help="Show only important/not important items")
def list(day, done, important):
    """Show to-do list for a particular day (for today by default)"""
    try:
        user_id = user_service.get_current_user()
        kwargs = {"task_date": day}
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

    except:
        click.echo("Please login to see the list of tasks")


@cli.command("add")
@click.argument("description")
@click.option("--day", type = DAY, default="today", help="Possible values: today (by default), yesterday, tommorrow, particular day in format YYYY-MM-dd")
@click.option("-d", "--done", is_flag=True, help="Marks task as done")
@click.option("-i", "--important", is_flag=True, help="Marks task as important")
def add(description, day, done, important):
    """Create a task"""
    user_id = 1
    task = Task(task_description=description, task_date=day, done=done, important=important, user_id=user_id)
    task_service.create(task)


@cli.command("update")
@click.argument("id")
@click.option("-d", "--day", type = DAY, default=None, help="A day to change. Possible values: today (by default), yesterday, tommorrow, particular day in format YYYY-MM-dd")
@click.option("--done/--not-done", default=None, help="Mark task as done/not done")
@click.option("--important/--not-important", default=None, help="Mark task as important/not important")
def update(id, day, done, important):
    """Update a task by id"""
    if (day == None and done == None and important == None):
        click.echo("Define at least one parameter to change")
    kwargs = {}
    if (day != None):
        kwargs["task_date"] = day
    if (done != None):
        kwargs["done"] = done
    if (important != None):
        kwargs["important"] = important
    
    task_service.update(id, **kwargs)

@cli.command("delete")
@click.argument("id")
def delete(id):
    """Delete a task by id"""
    task_service.delete(id)

@cli.command("create-user")
@click.option("-u", "--username", required=True)
@click.option("-p", "--password", required=True)
def create_user(username, password):
    user = User(user_name=username, user_password=password)
    user_service.create(user)

@cli.command("login")
@click.option("-u", "--username", required=True)
@click.option("-p", "--password", required=True)
def login(username, password):
    if user_service.login(username, password):
        click.echo(f"Welcome, {username}!")
    else: click.echo(f"Wrong username or password")


@cli.command("logout")
def logout(username, password):
    user_service.logout()
