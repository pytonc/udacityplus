import re

P_TITLE = re.compile(r'^[a-zA-Z0-9_\s-]{5,50}$')
# P_SHORT_DESC = re.compile(r'^[a-zA-Z0-9_!&()^\s-]{10,350}$')


def validate_project_title(title):
    if P_TITLE.match(title):
        return ''
    else:
        return 'min 5 characters required. only alphabets, numbers, -, _ and spaces are allowed'


def validate_project_url(url):
    if len(url) > 10:
        return ''
    else:
        return 'URL should be atleast 10 characters long'


def validate_project_short_description(desc):
    if 10 < len(desc) < 351:
        return ''
    else:
        return 'Description should be atleast 10 characters long'