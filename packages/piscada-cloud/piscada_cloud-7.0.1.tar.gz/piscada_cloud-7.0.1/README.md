# Picada Cloud

Library for the Piscada Cloud including authentication and data access.

## Features

- Login to Piscada Cloud and retrieve credentials
- Persist credentialss locally
- Read historic values for multiple tags as a Pandas DataFrame
- Possible apply time-based linear interpolation to measurements
- Utils to add fractional representations of periods: day, week, year

## Install

Install from PyPI:

```shell
pip install piscada-cloud
```

or

```shell
poetry add piscada-cloud
```

Install from local source:

```shell
pip install --editable path/to/piscada_cloud
```

or

```shell
poetry add path/to/piscada_cloud
```

## Usage

### Authentication

To log-in interactively and persist the retrieved credentials on disk (under `$HOME/.piscada_credentials`) simply run:

```shell
python -m piscada_cloud.auth
```

or

```shell
poetry run python -m piscada_cloud.auth
```

Any future invocation, e.g. `credentials = piscada_cloud.auth.persisted_login()` will return the credentials on disk without user interaction.

`credentials = piscada_cloud.auth.login(username, password, host)` can be used to retrieve the credentials programmatically.

### Getting Data

The credentials retrieved through the login can be used to get the host and acccesss-token for the historical data API:

```python
from piscada_cloud import auth

credentials = auth.login_persisted()
host, token = auth.get_historian_credentials(credentials)
```

The host and token can be used to retrieve historic data as a Pandas DataFrame.
The `get_historic_values` method takes a row of parameters:

- `start`: Datetime object
- `end`: Datetime object
- `tags`: List of `Tag` objects
- `host` (optional): Endpoint to which we send the historian queries. e.g. `historian.piscada.online`.
- `token` (optional): Access token, associated with the endpoint, used for authentication.

The if the `host` or `token` arguments are not provided, the environment variables `HISTORIAN_HOST` and `HISTORIAN_TOKEN` are used in stead, respectively.

```python
from datetime import datetime, timedelta, timezone

from piscada_cloud.data import get_historic_values
from piscada_cloud.mappings import Tag


tags = [
    Tag(controller_id="fe7bd2c3-6c20-44d4-aecc-df5822457400", name="ServerCpuUsage"),
    Tag(controller_id="fe7bd2c3-6c20-44d4-aecc-df5822457400", name="ServerMemoryUsage"),
]

df = get_historic_values(
    start=datetime.now(timezone.utc) - timedelta(days=30),
    end=datetime.now(timezone.utc),
    tags=tags
)
```

## Write Data

In this example the column `oCU135001RT90_MV` is selected and the average value is calculated using the method `.mean()`.

To write the result back to the Piscada Cloud, the `data` module offers the `write_value` function. It takes these arguments:

- `tag`: A `Tag` object
- `value`: The float, string, or dict value to write to the tag. Float and string will be sent as is, dict will be serialised as JSON string.
- `timestamp` (optional): The timestamp in milliseconds since epoch at which to write the value, by default `int(time.time() * 1000)`.
- `host`: Endpoint to send post request. Overrides the default, which is `os.environ['WRITEAPI_HOST']`.
- `token`: Access token accosiated with the host. Overrides the default, which is `os.environ['WRITEAPI_TOKEN']`.

The `Tag.name` must use the prefix `py_` as this is the only namespace allowed for writing data via the API.

```python
from piscada_cloud.data import write_value
from piscada_cloud.mappings import Tag


mean = df["oCU135001RT90_MV"].mean()
response = write_value(Tag(controller_id="0798ac4a-4d4f-4648-95f0-12676b3411d5", name="py_oCU135001RT90_MV_1h_mean"), value=mean)
if response.ok:
    print("OK")
else:
    print(response.text)
```

The `response` returned by the `write_value` method allows to check if the writing of data was successful `response.ok == True`.

### Manipulations

In order to support analysis in the context of periodic patters, the `manipulations` allow you to add fractional representations of day, week, and year as additional columns in the DataFrame:

- 00:00:00 -> 0.0 --- 23:59:59 -> 1.0
- Monday 00:00:00 -> 0.0 --- Sunday 23:59:59 -> 1.0
- 1st Jan. 00:00:00 -> 0.0 --- 31st Dec. 23:59:59 -> 1.0

```python
from piscada_cloud import manipulations

manipulations.add_weekdays(data)
manipulations.add_day_fraction(data)
manipulations.add_week_fraction(data)
manipulations.add_year_fraction(data)
```

## Development

Enable the provided git pre commit hook: `ln -s ./qa.sh .git/hooks/pre-commit`

## Requirements

The package will support the two latest version of Python.

## Authors

- Tim Jagenberg [tim.jagenberg@piscada.com](mailto:tim.jagenberg@piscada.com)
- Filip Henrik Larsen [filip.larsen@piscada.com](mailto:filip.larsen@piscada.com)

## License

© Piscada AS 2019
