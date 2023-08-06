# Watchtower Pipeline

## Requirements
* Python 3.9
* A working installation of Kitsu (optional)

In order to generate data for Watchtower, follow these steps:

* Create a new folder, step into it and perform:
* `python -m venv .venv`
* `source .venv/bin/activate`
* `pip install watchtower-pipeline`

## Create Example Data
To create an example project that will give you an idea of how the pipeline works:

* Run `python -m watchtower_pipeline.example -b`
* Copy the content of the `watchtower` folder into your webserver
* Alternatively you can navigate to the folder and run `python -m http.server`


## Create Kitsu-sourced Data
If you have a working Kitsu (and Zou) install and want to extract and visualize data from it:

* Create a `.env.local` file as follows:

```
KITSU_DATA_SOURCE_URL=https://<your-kitsu-instance>/api
KITSU_DATA_SOURCE_USER_EMAIL=user@example.org
KITSU_DATA_SOURCE_USER_PASSWORD=password
```

* Run `python -m watchtower_pipeline.kitsu -b`
* Copy the content of the `watchtower` folder into your webserver
* Alternatively you can navigate to the folder and run `python -m http.server`
