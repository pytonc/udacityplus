Errors
======
Errors are returned as either an empty dictionary if operation was successful or an dictionary
{error_key: "error string"}

Functions return two values:
Boolean, Dict
Boolean indicates whether the validation was successful, dict contains errors

User.valid_password

* error_password

User.valid_passwords

* error_password
* error_verify
* error_match

User.valid_username

* error_user_exists
* error_invalid_username

User.valid_date

* error_date

User.valid_email

* error_email