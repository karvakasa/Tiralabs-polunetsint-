from invoke import task


@task
def interactive(ctx):
    ctx.run("poetry run python3 -m pathfinding interactive", pty=True)

@task
def start(ctx):
    ctx.run("poetry run python3 -m pathfinding run --map ./maps/tiny.map --start 1,1 --goal 7,4 --algorithm astar --show",
     pty=True)

@task
def format(ctx):
    ctx.run("autopep8 --in-place --recursive app", pty=True)

@task
def test(ctx):
    ctx.run("poetry run python3 -m pytest", pty=True)

@task
def coverage(ctx):
    ctx.run("poetry run coverage run --branch -m pytest app; poetry run coverage html", pty=True)

@task
def lint(ctx):
    ctx.run("poetry run pylint app", pty=True)
