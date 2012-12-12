Downloading to csv
------------------
appcfg.py download_data --config_file=bulkloader.yaml --filename=<file>.csv --kind=<kind: Course|Source> --url=http://<app_id>.appspot.com/_ah/remote_api

Uploading to dev server
-----------------------
login: admin
password: <blank>
appcfg.py --config_file=bulkloader.yaml upload_data --filename=data/<file>.csv --kind=<kind: Course|Source> --application="dev~uplusprofiles" --url=http://localhost:8080/_ah/remote_api <path_to_app>

Uploading to app engine
-----------------------
appcfg.py --config_file=bulkloader.yaml upload_data --filename=data/<file>.csv --kind=<kind: Course|Source> --url=http://localhost:8080/_ah/remote_api

Examples:

python2x appcfg.py --config_file=bulkloader.yaml upload_data --filename=data/courses.csv --kind=Course --url=http://devn-uplusprofiles.appspot.com/_ah/remote_api

python2x appcfg.py --config_file=bulkloader.yaml upload_data --filename=data/sources.csv --kind=Source --url=http://devn-uplusprofiles.appspot.com/_ah/remote_api