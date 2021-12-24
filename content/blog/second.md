Title: Apache Superset from Scratch: Day 2 (Metadata Database)
Date: 2021-12-24 10:20
Category: Review

In Day 1, I setup the backend Python depedencies. Now, I'm going to start the metadata database. The next step, as laid out in [CONTRIBUTING.MD](https://github.com/apache/superset/blob/master/CONTRIBUTING.md#setup-local-environment-for-development), is to run:

```
superset db upgrade
```

### Superset CLI

Before we do that, I want to get more familiar with the Superset CLI. If you recall from the last post, running `superset` in the command line exposes a number of interesting commands we could run:

![Superset CLI]({filename}/images/superset_cli2.png)

Some interesting commands that stick out:

- db: Perform database migrations.
- export-dashboards: Export dashboards to JSON
- fab: FAB flask group commands
- init: Inits the Superset application

Where does the code for these CLI commands live? After some searches in the Superset codebase, it's clear they live in the `superset/cli.py` file. The CLI commands listed above map to function definitions. For example, here's the function definition for `superset init`:

```
@superset.command()
@with_appcontext
def init() -> None:
    """Inits the Superset application"""
    appbuilder.add_permissions(update_perms=True)
    security_manager.sync_role_definitions()
```

It looks like there's no function declaration that maps to the `superset db` CLI command, but instead the `db` namespace is imported from another file:

```
from superset.extensions import celery_app, db
```

If we jump to `superset/extensions.py`, we then see:

```
db = SQLA()
```

SQLA() sounds like SQLAlchemy, where is it defined or imported?

```
from flask_appbuilder import AppBuilder, SQLA
```

Neat! I know that Superset is built on top of Flask App Builder (or FAB for short), so this must be one of the important touchpoints. We'll avoid continuing down the rabbit hole for now, and dive deeper into FAB another day.

Let's ask the CLI to list out all of the available commands within `superset db`:

![Superset CLI db]({filename}/images/superset_cli_db.png)

Neat! Let's run `superset db upgrade` now. As expected, a bunch of historical database migrations were run and applied.

![Superset db upgrade]({filename}/images/superset_db_upgrade.png)

### Where does the metadata database live?

Apparently, _some_ database somewhere was upgraded. But where does that database actually live? After some exploring online, it seems that by default this database resides as a single SQLite database file over in my home directory:

```
cat ~/.superset/superset.db
```

Running this command returns a long list of all the schema definitions. This is cool! I look forward to understanding the schemas later.

### Creating default roles

Next up, we need to create an admin user in our metadata database (fancy word for our little SQLite database!):

```
superset fab create-admin
```

Before we run the full command, what CLI commands are available within the `superset fab` namespace?

![Superset CLI fab]({filename}/images/superset_cli_fab.png)

The commands here let us create admin users, create regular users, create database objects, reset a user's password, and more. Let's create an admin user by running `superset fab create-admin`. To keep this simple during exploration, I just answered **admin** for every line in the wizard:

![Superset fab create-admin]({filename}/images/fab_create_admin.png)

We now have an admin username (**admin**) and password (**admin**) combination for logging in to Superset, when the time is right. Next, let's create the rest of the roles and permissions:

```
superset init
```

It's interesting that this command isn't part of the `superset fab` command list.

### Example Data

Let's load up the example datasets and dashboards, many of which were actually created by yours truly!

```
superset load-examples
```

### Starting Flask Server

The last step now is to fire up the Flask server and see how Superset looks in the web browser.

```
FLASK_ENV=development superset run -p 8088 --with-threads --reload --debugger
```

By default, Flask will run on port 8088 but we can change the port number by changing the value we put in the invocation.

![Flask Server]({filename}/images/flask_server.png)

We're shown a somewhat incomplete and outdated login screen. This is interesting.

![Superset Login]({filename}/images/superset_login.png)

My guess here is that somewhere, the frontend assets need to be built. This seems to align with the comments listed before the flask server initialization instructions:

```
# Start the Flask dev web server from inside your virtualenv.
# Note that your page may not have CSS at this point.
# See instructions below how to build the front-end assets.
```

Let's save frontend for Day 3!