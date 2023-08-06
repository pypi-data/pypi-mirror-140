# Download YouTube metadata for videos relating to a search query

This is a Python script that can download metadata (including comments and likes) for YouTube videos relating to a search query. Uses the [YouTube Data API v3](https://developers.google.com/youtube/v3/docs). Metadata is saved in an `sqlalchemy` compatible database, for instance, PostgreSQL or SQLite.

*Metatube* is pauses retrieval once your daily quota is used up (the default as of this writing is 10,000 requests per day) and waits until quota refill. If interrupted, *metatube* will, upon restart, first fill gaps in the download history, then continue downloading ‘into the future’. Once caught up to within ten minutes of the current time, *metatube* exits.

If you use *metatube* for scientific research, please cite it in your publication: <br />
Fink, C. (2020): *metatube: Python script to download YouTube metadata*. [doi:10.5281/zenodo.3773302](https://doi.org/10.5281/zenodo.3773302).


### Installation

```shell
pip install metatube
```

### Configuration

Copy the example configuration file [metatube.yml.example](https://gitlab.com/helics-lab/metatube/-/raw/master/metatube.yml.example) to a suitable location, depending on your operating system:

- on Linux systems:
    - system-wide configuration: `/etc/metatube.yml`
    - per-user configuration:
        - `~/.config/metatube.yml` OR
        - `${XDG_CONFIG_HOME}/metatube.yml`
- on MacOS systems:
    - per-user configuration:
        - `${XDG_CONFIG_HOME}/metatube.yml`
- on Microsoft Windows systems:
    - per-user configuration:
        `%APPDATA%\metatube.yml`

Adapt the configuration:

- Configure a database connection string (`connection_string`), pointing to an existing database (the format is described in the [sqlalchemy documentation](https://docs.sqlalchemy.org/en/14/core/engines.html#database-urls).
- Configure an API [access key](https://developers.google.com/youtube/registering_an_application) to the YouTube Data API v3 (`youtube_api_key`).
- Define search terms (`search_terms`)

All of these configuration options can alternatively be supplied as command line arguments to `metatube` (see [Usage](#command-line-executable)) or as a `config` `dict` directly to the constructor of `YouTubeVideoMetadataDownloader`. Command line options (see `metatube --help`) or `config` `dict` both override config file.

### Usage

#### Command line executable

```shell
metatube \
    --postgresql-connection-string "postgresql:///metatube" \
    --youtube-api-key "abcdefghijklmn" \
    "how to build a tallbike"

```

#### Python

Import the `metatube` module. Instantiate a `YouTubeVideoMetadataDownloader`, optionally supply a `config` dictionary. Then run the instance’s `download()` method.

```python
import metatube

# config from config file
downloader = YouTubeVideoMetadataDownloader()
downloader.download()

# config from config file,
# overriding `search_terms`
downloader = YouTubeVideoMetadataDownloader({
    "search_terms": "Critical Mass Vladivostok"
})
downloader.download()

# entire config from dictionary
downloader = YouTubeVideoMetadataDownloader({
    "youtube_api_key": "opqrstuvwxyz",
    "connection_string": "postgresql://server1/bicyclelover123:supersecretpassword@metatube",
    "search_terms": "dashcam bicycle commute albuquerque"
})
downloader.download()

```

### Data privacy

By default, metatube pseudonymises downloaded metadata, i.e. it replaces (direct) identifiers with randomised identifiers (generated using hashes, i.e. ‘one-way encryption’). This serves as one step of a responsible data processing workflow. However, the text and descriptions of videos and comments might nevertheless qualify as *indirect identifiers*, as they, combined or on their own, might allow re-identification of the commenter or uploader. If you want to use data downloaded using metatube in a GDPR-compliant fashion, you have to follow up the data collection stage with *data minimisation* and further pseudonymisation or anonymisation efforts.

Metatube can keep original identifiers (i.e. skip pseudonymisation). Set the according command line argument, configuration file or `config` `dict` (see the [sample config file](metatube.yml.example) and below). Ensure that you fulfil all legal and organisational requirements to handle personal information before you decide to collect non-pseudonyismed data.

```python
import metatube

downloader = YouTubeVideoMetadataDownloader({
    "search_terms": "Winter Cycling Congress",
    "pseudonymise": False  # get legal/ethics advice before doing this
})
downloader.download()
```
