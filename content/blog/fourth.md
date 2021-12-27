Title: Apache Superset from Scratch: Day 4 (Superset & Flask Entrypoint)
Date: 2021-12-26 10:20
Category: Review

I ended Day 3 by setting up the backend and frontend servers, but running into the following error.

![Superset UI]({static}/images/superset_ui.png)

For good measure, I'm going to shut down and restart the backend server. Success!

![Superset UI Fixed]({static}/images/superset_ui_fixed.png)

No thumbnails though ☹️. Well I do know from previous experience that thumbnails require setting up a separate celery server. This will need separate investigation.

Now that I have Superset up and running, what should I look into next? I really want to dive deeper into how the example datasets, charts, and dashboards are loaded. This will force me to better understand the internal Superset data model.

### How the Superset Examples Work

The world health dashboard looks interesting and like one of the more complex ones. I'll start by poking deeper into this one:

![World Health Dashboards]({static}/images/world_health_dashboard.png)

Here's the relevant function call from `superset/cli.py`:

```
print("Loading [World Bank's Health Nutrition and Population Stats]")
examples.load_world_bank_health_n_pop(only_metadata, force)
```

Sooo, let's get into it. Where does the second line of code actually point to? As I mentioned in [Day 2](/apache-superset-from-scratch-day-2-metadata-database.html), the `superset/superset/examples/__init__.py` file contains mappings like this one:

```
from .world_bank import load_world_bank_health_n_pop
```

This means that the `load_world_bank_health_n_pop()` function lives in `examples/world_bank.py`! Here's a preview of the first 8 lines:

```
def load_world_bank_health_n_pop(  # pylint: disable=too-many-locals, too-many-statements
    only_metadata: bool = False, force: bool = False, sample: bool = False,
) -> None:
    """Loads the world bank health dataset, slices and a dashboard"""
    tbl_name = "wb_health_population"
    database = utils.get_example_database()
    engine = database.get_sqla_engine()
    schema = inspect(engine).default_schema_name
    table_exists = database.has_table_by_name(tbl_name)
```

The first line almost surely refers to the table name in the examples database.

```
tbl_name = "wb_health_population"
```

How can I confirm this? The fastest way is to probably crack open SQL Lab and inspect the table name for the examples database.

![World Health Table]({static}/images/wb_sqllab.png)

Confirmed. Let's check out the next line:

```
database = utils.get_example_database()
```

Ah yes, the art of the `utils`! The perfect hiding place for some arbitrary functions. Where does this point to?

```
from superset.utils import core as utils
```

So there should be a `utils/core.py` file. Oh boy, this file is 1835 lines of code. But it does have the `get_example_database()` function that's called. The function definition is pretty short so I'm including it here in it's entireity:

```
def get_example_database() -> "Database":
    db_uri = (
        current_app.config.get("SQLALCHEMY_EXAMPLES_URI")
        or current_app.config["SQLALCHEMY_DATABASE_URI"]
    )
    return get_or_create_db("examples", db_uri)
```

Now we're getting somewhere! This function tells the app which database is designated as the **examples** one. First things first, where is `current_app` defined?

```
from flask import current_app, flash, g, Markup, render_template, request
```

The `current_app` object is imported from [flask](https://flask.palletsprojects.com/en/2.0.x/), which is a Python microframework for creating web applications. 

> Note to self: I need to dig into the relationship between Flask and Flask App-builder later on.

After a quick Google search, I found the page in the flask documentation on [the current application context](https://flask.palletsprojects.com/en/2.0.x/appcontext/). Perusing this page, this reminds me a lot of of the `request` object from my Ruby on Rails days. This was a form of passing application state around.

This is essentially a way to reference values specific to the current instance running of the running Superset application.

> The application context keeps track of the application-level data during a request, CLI command, or other activity. Rather than passing the application around to each function, the current_app and g proxies are accessed instead.

> This is similar to The Request Context, which keeps track of request-level data during a request. A corresponding application context is pushed when a request context is pushed.

Well what do you know! There's a call out to the [flask version of the request object](https://flask.palletsprojects.com/en/2.0.x/reqcontext/) that's similar to the one from Rails! My hunch was spot on.

### App Factory Pattern

To take a step back, what actually happens when I run `superset run` from the CLI?

The [flask documentation](https://flask.palletsprojects.com/en/2.0.x/tutorial/factory/) suggests that the `def create_app()` function definition is likely to be the **entrypoint** to the flask application at the core of Superset that is called when `flask run` or an equivalent is run.

A quick search in my text editor found only one non-test-related definition for `create_app()`, found in `superset/superset/app.py`:

![App Py]({static}/images/app_py.png)

These lines especially look relevant to our investigation of how:

- the World Health dashboard is loaded
- how `current_app.config.get("SQLALCHEMY_EXAMPLES_URI")` resolves
- getting closer to `current_app`

```
try:
    # Allow user to override our config completely
    config_module = os.environ.get("SUPERSET_CONFIG", "superset.config")
    app.config.from_object(config_module)
```

### Next Steps

I feel closer to understanding all of the links here, but sadly I'm out of time today. Here are the open questions I still have:

- What's the link between `create_app()` and `current_app`?
- Where is the value for `SQLALCHEMY_EXAMPLES_URI` actually set?
- How does this line of code actually work: `os.environ.get("SUPERSET_CONFIG", "superset.config")`?