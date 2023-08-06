# Watchtower Pipeline Tools

In order to generate data for Watchtower, follow these steps:

* `python -m venv .venv`
* `source .venv/bin/activate`
* `pip install watchtower-pipeline`
* Create a `.env.local` file as follows:

```
KITSU_DATA_SOURCE_URL=https://<your-kitsu-instance>/api
KITSU_DATA_SOURCE_USER_EMAIL=user@example.org
KITSU_DATA_SOURCE_USER_PASSWORD=password
```

* Run `python -m watchtower_pipeline.kitsu -b`
* Copy the content of the `watchtower` folder into your webserver
* Alternatively you can navigate to the folder and run `python -m http.server`
