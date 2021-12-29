Title: Apache Superset from Scratch: Day 5 (More Flask App)
Date: 2021-12-28 10:20
Category: Review

I ended Day 4 trying to understand how the World Health dashboard was imported. I walked away with a lot of open questions around how the flask app factory pattern worked. After sleeping on it and approaching with fresh eyes, I'm excited to hopefully make more progress today.

### Flask App Context

I spent the morning reading the following articles from the excellent Flask documentation:

- [the Application Context](https://flask.palletsprojects.com/en/2.0.x/appcontext/)
- [class flask.Config](https://flask.palletsprojects.com/en/2.0.x/api/#flask.Config)
- [Application Factories](https://flask.palletsprojects.com/en/2.0.x/patterns/appfactories/)
- [Configuring from Python Files](https://flask.palletsprojects.com/en/2.0.x/config/#configuring-from-python-files)

After going deep into these, I'll attempt to walkthrough everything I learned.

As I mentioned in the last post, the crucial entry-point into the Flask application is the `create_app()` function from `superset/superset/app.py`. Here's the entire function definition:

```
def create_app() -> Flask:
    app = SupersetApp(__name__)

    try:
        # Allow user to override our config completely
        config_module = os.environ.get("SUPERSET_CONFIG", "superset.config")
        app.config.from_object(config_module)

        app_initializer = app.config.get("APP_INITIALIZER", SupersetAppInitializer)(app)
        app_initializer.init_app()

        return app

    # Make sure that bootstrap errors ALWAYS get logged
    except Exception as ex:
        logger.exception("Failed to create app")
        raise ex
```

Within `create_app()`, the following line of code defines what `current_app` refers to: 

```
app = SupersetApp(__name__)
```

The `current_app` variable acts as a global variable for different parts of your application to reference & use. The following line of code retrieves information from the `SUPERSET_CONFIG` environment variable (using `os.environ.get()`) and defaults to `superset.config` if not found:

```
config_module = os.environ.get("SUPERSET_CONFIG", "superset.config")
```

Then, the configuration information is loaded and attached to the `app` object (elsewhere in the application it would be referenced as `current_app`).

```
app.config.from_object(config_module)
```

All of the information so far suggests that the `SQLALCHEMY_EXAMPLES_URI` value is meant to be configured, which makes sense! 

- By default in a native Superset installation, the SQLite database in my home directory is used. 
- But within the Docker Compose image for Superset, the included Postgres database is used instead.

There's still SO much I don't understand about Flask, but I need to do a separate, multi-day deep dive into that web framework. I want to balance breadth with depth here and it may be time to move on with the cursory understanding I have.

> Note to self: Go through [Flask mega-tutorial](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xv-a-better-application-structure), which seems to be consistently recommended by people online!

### Examples Database

I want to come back for air, and circle back to how the World Health dashboard is loaded into the Superset metadata database. I want to understand this function better, which is called from the `load_world_bank_health_n_pop()` function in `world_bank.py`:

```
def get_example_database() -> "Database":
    db_uri = (
        current_app.config.get("SQLALCHEMY_EXAMPLES_URI")
        or current_app.config["SQLALCHEMY_DATABASE_URI"]
    )
    return get_or_create_db("examples", db_uri)
```

The first clause looks interesting:

```
db_uri = (
        current_app.config.get("SQLALCHEMY_EXAMPLES_URI")
        or current_app.config["SQLALCHEMY_DATABASE_URI"]
    )
```

This code is attempting to look up the database URI based on the app's configuration settings. We know that `current_app.config.get()` looks up values from `superset/superset/config.py`. At 1337 lines of code, the `config.py` file is massive. It contains code mostly assigning values to all-upper-case variable names. Here's an example:

```
SQLALCHEMY_EXAMPLES_URI = None
```

Here's a walkthrough of how `db_uri` is calculated:

- The first clause is attempting to find a truthy value, between `SQLALCHEMY_EXAMPLES_URI` and `SQLALCHEMY_DATABASE_URI`. 
- Because by default `SQLALCHEMY_EXAMPLES_URI` is set to `None`, the value for `SQLALCHEMY_DATABASE_URI` is then looked up.
- By default, `SQLALCHEMY_DATABASE_URI` is assigned to evaluate: `"sqlite:///" + os.path.join(DATA_DIR, "superset.db")`

Now we're getting somewhere! The `sqlite:///` and `"superset.db"` parts _smells_ a lot like the location of the sqlite metadata database that lives in my home directory that I dug up in [my Day 2 post](/apache-superset-from-scratch-day-2-metadata-database.html):

```
cat ~/.superset/superset.db
```

But what's this `DATA_DIR` value and how is it computed? I did a quick search within `superset/superset/config.py` and the first instance of `DATA_DIR` is referenced here:

```
if "SUPERSET_HOME" in os.environ:
    DATA_DIR = os.environ["SUPERSET_HOME"]
else:
    DATA_DIR = os.path.join(os.path.expanduser("~"), ".superset")
```

Because I didn't specifically set `SUPERSET_HOME` in my environment variables, then the second code path is being evaluated instead:

```
DATA_DIR = os.path.join(os.path.expanduser("~"), ".superset")
```

I quickly ran this in a new Python shell and the result mapped exactly to the `.superset/` folder within my home directory:

![Data Dir]({static}/images/data_dir.png)


This means that `SQLALCHEMY_DATABASE_URI` points to my metadata database, as expected. Progress!

Finally, this means that the `get_example_database()` function will return the location to my sqlite database or it will create it if it doesn't exist (as the name `get_or_create_db()` suggests):

```
    return get_or_create_db("examples", db_uri)
```

The return value of `utils.get_example_database()` is assigned to the `database` variable.

### Superset Shell

While reading function definitions is great, the only way to learn technical concepts is getting your hands dirty and actually running code yourself. 

What's the best way to actually accomplish this though, while having the application lifecycle state loaded for me to interact with?

Some searching online led me to this [page in the Flask docs](https://flask.palletsprojects.com/en/2.0.x/cli/#open-a-shell), which mentions the following:

> To explore the data in your application, you can start an interactive Python shell with the shell command. An application context will be active, and the app instance will be imported.

I also know that Superset extends many of the underlying Flask metaphors and I remember seeing `superset shell` listed when running the Superset CLI:

```
...
run                       Run a development server.
set-database-uri          Updates a database connection URI
shell                     Run a shell in the app context.
sync-tags                 Rebuilds special tags (owner, type, favorited
...
```

I'm going to try this out:

```
superset shell
```

Excellent! I now have a shell environment with the Superset App context loaded in:

![Superset Shell]({static}/images/superset_shell.png)

### Next Steps

I've run out of time for the day and will end here. Next, I want to step through all of the function calls in the World Health dashboard example using the Superset shell.