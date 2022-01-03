Title: Apache Superset from Scratch: Day 7 (Metadata for Examples)
Date: 2021-12-30 10:20
Category: Review

I ended Day 6 with a good understanding of the first half of the `load_world_bank_health_n_pop()` function, which loads the World Health dashboard example. Today, I'm hoping to understand the rest of the function if possible.

The next line of code is:

```
table = get_table_connector_registry()
```

The `get_table_connector_registry()` function seems to be defined in `superset/superset/examples/helpers.py`. The function definition is very simple:

```
def get_table_connector_registry() -> Any:
    return ConnectorRegistry.sources["table"]
```

### Helper Functions for Superset Examples

This function is so simple, I'm even wondering why this function needs to exist. 

> Why can't `ConnectorRegistry.sources["table"]` just be defined directly in the `load_world_bank_health_n_pop()` function within `world_bank.py`?

Let me take a peek at the rest of the functions in `superset/examples/helpers.py` to try to gain more context:

- `get_table_connector_registry()`: yet to be determined!
- `get_examples_folder()`: returns exact path to where example datasets, dashboards, etc are stored.
- `update_slice_ids(layout_dict: Dict[Any, Any], slices: List[Slice])`: does some type of sorting of slices
- `merge_slice(slc: Slice)`: deletes existing Slice and creates new one in its place
- `get_slice_json(defaults: Dict[Any, Any], **kwargs: Any)`: unclear! But something around JSON representation of Slice objects.
- `get_example_data(filepath: str, is_gzip: bool = True, make_bytes: bool = False)`: common utility function for fetching JSON dataset from a URL and reading in the bytes (we saw this earlier!)

These all smell like functions that any example-loading script can benefit from and re-use. So it makes sense that they're all defined here for common use.

### Why ConnectorRegistry?

ConnectorRegistry sounds interesting, as it sounds like some type of registry that maintains the available database connectors in the current Superset installation. This lead me to the following question:

> Why not store the available connectors in the metadata database?

My hunch is that this adds extra friction, slows down the development process, and doesn't add too much. 

You can imagine a Superset contributor having multiple local git branches and wanting to quickly switch between them. In my past life as a backend engineer, I've personally experienced the pains of database state causing issues between versions of the same software.

For connectors, the _state_ itself is likely defined entirely in the code itself. 

- The connector libraries are either defined in code that lives in the source tree, or they aren't!
- The `db_engine_spec` for a given database either exists in the source tree, or it doesn't!

Let's move on to the implementation for ConnectorRegistry.

### Connector Registry

Where is the ConnectorRegistry class defined? The comment at the top for the class definition is:

```
Central Registry for all available datasource engines
```

In `superset/superset/connectors/connector_registry.py`, the ConnectorRegistry class is defined with the following class methods.

- `register_sources()`
- `get_datasource()`
- `get_all_datasources()`
- `get_datasource_by_id()`
- `get_datasource_by_name()`
- `query_datasources_by_permissions()`
- `get_eager_datasource()`
- `query_datasources_by_name()`

Because the ConnectorRegistry class acts as a source of truth, it can just have class methods that other parts of the codebase can call to look up information. It won't ever be instantiated into individual objects.

The `register_sources()` class method piqued my interest, as it probably _registers_ new data sources. When is this actually called though? It's only called in `superset/superset/initialization/__init__.py`:

```
def configure_data_sources(self) -> None:
    # Registering sources
    module_datasource_map = self.config["DEFAULT_MODULE_DS_MAP"]
    module_datasource_map.update(self.config["ADDITIONAL_MODULE_DS_MAP"])
    ConnectorRegistry.register_sources(module_datasource_map)
```

This makes sense. The possible data source engines only need to be registered during the flask app initialization.


What is the default value set to `"DEFAULT_MODULE_DS_MAP`?

```
DEFAULT_MODULE_DS_MAP = OrderedDict(
    [
        ("superset.connectors.sqla.models", ["SqlaTable"]),
        ("superset.connectors.druid.models", ["DruidDatasource"]),
    ]
```

What is the default value set to `"ADDITIONAL_MODULE_DS_MAP"`?

```
ADDITIONAL_MODULE_DS_MAP: Dict[str, List[str]] = {}
```

So this code path essentially returns an Ordered Dictionary of values. Interesting.

Let's circle back to `get_table_connector_registry()`, which essentially boils down to:

```
ConnectorRegistry.sources["table"]
```

This code references the following class variable:

```
class ConnectorRegistry:
    """Central Registry for all available datasource engines"""

    sources: Dict[str, Type["BaseDatasource"]] = {}
```

What does this value look like for our current Superset instance?

```
>>> ConnectorRegistry.sources
{'table': <class 'superset.connectors.sqla.models.SqlaTable'>, 'druid': <class 'superset.connectors.druid.models.DruidDatasource'>}
```

From Superset's stand point, databases are either:

- a Druid data source, connected using the legacy Druid connector, in which case the datasets are JSON (I think)
- a SQAlchemy data source, in which case the datasets are all tables

The returned dictionary matches the default value set to `"DEFAULT_MODULE_DS_MAP`:

```
DEFAULT_MODULE_DS_MAP = OrderedDict(
    [
        ("superset.connectors.sqla.models", ["SqlaTable"]),
        ("superset.connectors.druid.models", ["DruidDatasource"]),
    ]
```

This _seems_ like a LOT of steps and code just to return a tiny dictionary of values!

> ConnectorRegistry doesn't even seem to return the actual _database connectors_ that are registered. This is a bit weird!

Interestingly, the SqlaTable class does warrant further investigation. It seems to be an ORM model / wrapper for the SQLAlchemy table objects with some Superset-specific niceities.

### Searching for a Table

After returning the SQLAlchemy compatible module name and class using the ConnectorRegistry, here's the next line of code:

```
tbl = db.session.query(table).filter_by(table_name=tbl_name).first()
```

This code uses SQLAlchemy syntax to generate a SQL query that returns the "wb_health_population" table. It handles multiple results and focuses on just the ones from SQLAlchemy databases that Superset is aware of. Specifically, it returns a SqlaTable object and assigns to `tbl`.

The next code fragment creates the table if it doesn't exist:

```
if not tbl:
	tbl = table(table_name=tbl_name, schema=schema)
```

Next up, this code reads in "countries.md", which contains information on the World Health dataset. Then, it attaches this information to the description column for the SqlaTable object:

```
tbl.description = utils.readfile(
	os.path.join(get_examples_folder(), "countries.md")
)
```

The next three lines of code set values to three more columns within this SqlaTable object:

```
tbl.main_dttm_col = "year"
tbl.database = database
tbl.filter_select_enabled = True
```

### Defining Metrics for World Health Dashboard

The raw metrics that need to be created to power this Superset dashboard are represented as the following strings:

```
metrics = [
    "sum__SP_POP_TOTL",
    "sum__SH_DYN_AIDS",
    "sum__SH_DYN_AIDS",
    "sum__SP_RUR_TOTL_ZS",
    "sum__SP_DYN_LE00_IN",
    "sum__SP_RUR_TOTL",
]
```

The next block of code does the following for each metric-string:

- searches all of the `tbl` object's `metrics` to check if it already exists
- slices the metric-string to extract first 3 characters (e.g. "sum")
- uses SQLAlchemy to search for the column that will be aggregated
- appends the metric to `tbl.metrics`, using the `SqlMetric` class

```
for metric in metrics:
    if not any(col.metric_name == metric for col in tbl.metrics):
        aggr_func = metric[:3]
        col = str(column(metric[5:]).compile(db.engine))
        tbl.metrics.append(
            SqlMetric(metric_name=metric, expression=f"{aggr_func}({col})")
        )
```

The next three lines seem to commit these changes to the database and re-fetch the metadata:

```
db.session.merge(tbl)
db.session.commit()
tbl.fetch_metadata()
```

We're nearly done understanding the World Health dashboard example! But I've run out of time for today. I'll save this for Day 8!