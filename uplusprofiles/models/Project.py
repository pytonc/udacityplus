import re

from google.appengine.ext import  ndb
from google.appengine.ext import blobstore
from google.appengine.api import images


class Project(ndb.Model):
    title = ndb.StringProperty()
    screenshot = ndb.BlobKeyProperty()
    screenshot_url = ndb.StringProperty()
    url = ndb.StringProperty()
    short_description = ndb.StringProperty()
    author = ndb.KeyProperty()

    @classmethod
    def add_project(cls, **kwargs):
        """Adds project to datastore and returns id associated with that record
        """
        kwargs['short_description'] = cls.filter_whitespaces(kwargs['short_description'])
        p  = Project(**kwargs)
        p_key = p.put()
        return p_key.id()

    @classmethod
    def update_project(cls, project_id, **kwargs):
        """Updates project details.
        Screenshot is updated only if valid image is provided by the user 
        """
        p = Project.get_by_id(int(project_id))
        p.title = kwargs['title']
        if kwargs['screenshot'] and kwargs['screenshot_url']:
            cls.remove_screenshot_blob(p.screenshot)
            p.screenshot = kwargs['screenshot']
            p.screenshot_url = kwargs['screenshot_url']
        
        p.url = kwargs['url']
        p.short_description = cls.filter_whitespaces(kwargs['short_description'])
        p.put()

    @classmethod
    def remove_project(cls, project_id):
        """Removes project and corresponding blob and serving url
        """
        p = Project.get_by_id(int(project_id))
        blob_key = p.screenshot
        cls.remove_screenshot_blob(blob_key)
        p.key.delete()

    @classmethod
    def get_projects_by_ids(cls, project_ids):
        """Returns a list of Project objects
        """
        projects = []
        if project_ids:
            for project_id in project_ids:
                p = Project.get_by_id(project_id)
                if p:
                    projects.append(p)
        return projects

    @classmethod
    def get_screenshot(cls, project_id):
        """Returns blob_key associated with project_id
        """
        p = Project.get_by_id(int(project_id))
        return p.screenshot

    @classmethod
    def remove_screenshot_blob(cls, blob_key):
        """Removes screenshot from blobstore 
        and removes serving url associated with it
        """
        images.delete_serving_url(blob_key)
        blobstore.delete(blob_key)

    @classmethod
    def filter_whitespaces(cls, s):
        """Replaces whitespaces with single space
        (Necessary as newline characters break edit_project javascript)
        """
        return re.sub("\s+" , " ", s)
        
