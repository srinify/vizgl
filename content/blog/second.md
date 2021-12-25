Title: Apache Superset from Scratch: Day 2 (Metadata Database)
Date: 2021-12-24 10:20
Category: Review

In Day 1, I setup the backend Python depedencies. Now, I'm going to start the metadata database. The next step, as laid out in [CONTRIBUTING.MD](https://github.com/apache/superset/blob/master/CONTRIBUTING.md#setup-local-environment-for-development), is to run:

```
superset db upgrade
```

### Superset CLI

Before we do that, I want to get more familiar with the Superset CLI. If you recall from the last post, running `superset` in the command line exposes a number of interesting commands we could run:

![Superset CLI]({static}/images/superset_cli2.png)

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

![Superset CLI db]({static}/images/superset_cli_db.png)

Neat! Let's run `superset db upgrade` now. As expected, a bunch of historical database migrations were run and applied.

![Superset db upgrade]({static}/images/superset_db_upgrade.png)

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

![Superset CLI fab]({static}/images/superset_cli_fab.png)

The commands here let us create admin users, create regular users, create database objects, reset a user's password, and more. Let's create an admin user by running `superset fab create-admin`. To keep this simple during exploration, I just answered **admin** for every line in the wizard:

![Superset fab create-admin]({static}/images/fab_create_admin.png)

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

What all is loaded? How does this actually work? For fun, let's dive into the functions & relevant codepaths. Let's start with the function definition for `superset load-examples`. To follow Pythonic syntax, we need to instead look for `load_examples()` in `superset/cli.py`. Here's the function declaration:

```python
@with_appcontext
@superset.command()
@click.option("--load-test-data", "-t", is_flag=True, help="Load additional test data")
@click.option("--load-big-data", "-b", is_flag=True, help="Load additional big data")
@click.option(
    "--only-metadata", "-m", is_flag=True, help="Only load metadata, skip actual data",
)
@click.option(
    "--force", "-f", is_flag=True, help="Force load data even if table already exists",
)
def load_examples(
    load_test_data: bool,
    load_big_data: bool,
    only_metadata: bool = False,
    force: bool = False,
) -> None:
    """Loads a set of Slices and Dashboards and a supporting dataset"""
    load_examples_run(load_test_data, load_big_data, only_metadata, force)
```

While most of the code focuses on the possible CLI options & function parameters, the actual function definition is a single line:

```
load_examples_run(load_test_data, load_big_data, only_metadata, force)
```

If we jump to that function declaration, it's much much longer. This must be where the meat of the logic is for loading examples. Here's a screenshot of just the first half!

![Load Examples Run]({static}/images/load_examples_run.png)

This line looks interesting:

```
from superset import examples
```

If I poke through the file structure for Superset, I find a folder dedicated to examples (`superset/examples`). The `__init__.py` file for this folder defines each function mapping:


![Examples Directory]({static}/images/examples_directory.png)

Cool! What should I look at next?

```
examples.load_css_templates()
```

Superset ships with two default CSS templates for dashboards, so this code is likely how that data is loaded. Let's crack open the `def load_css_tesmplates()` function, which lives in `superset/examples/load_css_templates.py`.

![Load CSS Templates]({static}/images/load_css_templates.png)

Each CSS template is loaded one after another. Let's step through the key parts of the code to better understand it.

```
obj = db.session.query(CssTemplate).filter_by(template_name="Flat").first()
```

Here we see the `db` object again, from earlier. Unsurprisingly, there's a matching import statement for it:

```
from superset import db
from superset.models.core import CssTemplate
```

The CssTemplate data model itself looks very simple, as defined in `superset/models/core.py`:

```
class CssTemplate(Model, AuditMixinNullable):

    """CSS templates for dashboards"""

    __tablename__ = "css_templates"
    id = Column(Integer, primary_key=True)
    template_name = Column(String(250))
    css = Column(Text, default="")
```

As a mental note to myself, this table is named **css_templates** in the metadata database.

The rest of the code _smells_ a lot like SQLAlchemy syntax:

```
db.session.query(CssTemplate).filter_by(template_name="Flat").first()
```

While I'm not too familiar with the Superset data model yet, this code likely:

- Attaches to a SQLAlchemy session / transaction
- Queries the metadata database, searching for a matching CssTemplate object with the name **Flat**
- And the `first()` at the end is probably just for good measure, in case there are duplicate results

The goal likely here is to search for an existing entry in the metadata database for the **Flat** CSS template. If an existing entry in the metadata database wasn't found, a new CssTemplate object is instantiated for the purpose of inserting later:

```
if not obj:
	obj = CssTemplate(template_name="Flat")
```

Then, the CSS itself is defined as a hard-coded string (shortened extensively below):

```
css = textwrap.dedent(
	"""\
    .navbar {
        transition: opacity 0.5s ease;
        opacity: 0.05;
    }
    ....
    """
    )
```

Finally, the string is set to the instianted CssTemplate object's `css` column and inserted into the metadata database:

```
obj.css = css
    db.session.merge(obj)
    db.session.commit()
```

This whole process is then repeated to add the **Courier Black** CSS template.

Phew! This was just the CSS templates. No example datasets or example dashboards yet. Because I'm running out of time today, I'll circle back to the code paths for those a later day.

### Starting Flask Server

The last step now is to fire up the Flask server and see how Superset looks in the web browser.

```
FLASK_ENV=development superset run -p 8088 --with-threads --reload --debugger
```

By default, Flask will run on port 8088 but we can change the port number by changing the value we put in the invocation.

![Flask Server]({static}/images/flask_server.png)

We're shown a somewhat incomplete and outdated login screen. This is interesting.

![Superset Login]({static}/images/superset_login.png)

My guess here is that somewhere, the frontend assets need to be built. This seems to align with the comments listed before the flask server initialization instructions:

```
# Start the Flask dev web server from inside your virtualenv.
# Note that your page may not have CSS at this point.
# See instructions below how to build the front-end assets.
```

Let's save frontend for Day 3!