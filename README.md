# SSMv2
Simple Service Monitor

-Staging code as I develop...


Step 1. Clone Repo using git clone

Step 2. Change name of _config to config

Step 3. Review config options and add new targets `config/targets/targets.ini`

Run With Python --> `pip install -r requirements.txt` --> `python sample_script.py`

Run With Docker --> `docker build -t ssmv2 .` --> `docker run`

### Notifiers

A table of the currently supported notifiers is shown below, please generate the appropriate API settings, and add them to the configuration file.

 | API      | API Settings                    | Supported |
|----------|---------------------------------|:---------:|
| Pushover | https://pushover.net/apps/build |     ✅     |
