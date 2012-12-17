General
-------
Application is in `web` directory. Top level directories take precedence over ones in `boilerplate`, hence some are duplicated. Please don't alter anything in `boilerplate` directory.

Some files are unused, I just didn't get around to cleanup. Some code may crash and be insecure against unauthorized requests.

~~Users don't get automatically added to search index due to processing required to do that being executed only after user edits their profile. Registration triggers boilerplate User class (in boilerplate/models), profile triggers app specific User (in web/models).~~done, so new users get auto-put in search

Bulk data
---------
Course data is in `data/` directory. For remote deployment, upload the application before uploading data. Instructions for uploading data are in `bulkuploader.md`, some convenience code in `bulkup.sh` (for local) and `bulkup_remote.sh` (for remote).

update gae-boilerplate with:
----------------------------

```
git pull bootstrap master
```

OpenID
------
Not configured