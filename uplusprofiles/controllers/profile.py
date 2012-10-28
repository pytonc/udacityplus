import logging
from datetime import date, timedelta

from google.appengine.api import images
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

from BaseHandler import *
from jinja_custom.helpers import get_gravatar
from models.Course import Course
from models.User import User
from models.Project import Project


class ProfilePage(BaseHandler, blobstore_handlers.BlobstoreUploadHandler):
    MAX_IMG_SIZE = 1048576 # in bytes

    #@Authentication.do
    def get(self, username):
        """display profile of user with username, if None, display logged in user
        """
        mode = self.request.get('mode')
        upload_url = ""

        if mode == 'add_project':
            template = 'profile/add_project.html'
            upload_url = blobstore.create_upload_url('/' + username, max_bytes_per_blob=self.MAX_IMG_SIZE)
        elif mode == 'edit_project':
            template = 'profile/edit_project.html'
            upload_url = blobstore.create_upload_url('/' + username, max_bytes_per_blob=self.MAX_IMG_SIZE)
        else:
            template = 'profile/profile.html'


        user = User.get_user(username)
        if not user:
            user = User.save(username, '{}@someplace.com'.format(username), 'some long password')


        dob = user.created - 13 * timedelta(days=365)

        gravatar = user.avatar_url
        friends = []

        courses = Course.query()

        projects = Project.get_projects_by_ids(user.projects)

        if user:
            context = {'user': user, 'dob': dob,
                       'username': username,
                       'gravatar': gravatar,
                       'friends': friends,
                       'friend_btn': False,
                       'courses': courses,
                       'projects': projects,
                       'upload_url': upload_url}

            self.render(template, context)
        else:
            self.redirect('/logout')

    #@Authentication.do
    def post(self, username):
        mode = self.request.get('mode')
        if mode == 'add_project':
            screenshot_url = None
            errormsg = None

            title = self.request.get('title').strip()
            url = self.request.get('url').strip()
            description = self.request.get('description').strip()

            upload_files = self.get_uploads('screenshot')
            if upload_files:
                blob_info = upload_files[0]
                if 'image' in blob_info.content_type:
                    screenshot = blob_info.key()
                    screenshot_url = images.get_serving_url(screenshot)
                else:
                    # uploaded file wasn't an images, hence remove from the blobstore
                    blobstore.delete(blob_info.key())
                    errormsg = 'Invalid image type'
            
            if title and screenshot_url and url and description:
                project_id = Project.add_project(title=title, screenshot=screenshot, 
                    screenshot_url=screenshot_url, url=url, description=description)

                User.add_project(username, project_id)
            else:
                if upload_files and not errormsg:
                    # blob was okay but some other field was empty
                    # hence remove it to avoid orphaned entry
                    blobstore.delete(blob_info.key())

                if not errormsg:
                    errormsg = 'All fields are mandatory'

                user = User.get_user(username)
                template = 'profile/add_project.html'
                upload_url = blobstore.create_upload_url('/' + username, max_bytes_per_blob=self.MAX_IMG_SIZE)
                context = { 'user': user,
                            'username': username,
                            'title': title,
                            'url': url,
                            'description': description,
                            'upload_url': upload_url,
                            'errormsg': errormsg}
                self.render(template, context)
                return
        elif mode == 'edit_project':
            project_id = self.request.get('projects_dropdown')
            title = self.request.get('title').strip()
            url = self.request.get('url').strip()
            description = self.request.get('description').strip()

            screenshot = None
            screenshot_url = None
            errormsg = None

            upload_files = self.get_uploads('screenshot')
            if upload_files:
                blob_info = upload_files[0]
                if 'image' in blob_info.content_type:
                    screenshot = blob_info.key()
                    screenshot_url = images.get_serving_url(screenshot)
                else:
                    # uploaded file wasn't an images, hence remove from the blobstore
                    blobstore.delete(blob_info.key())
                    errormsg = 'Invalid image type'

            if title and url and description and not errormsg:
                # remove old screenshot from blobstore
                blob_key = Project.get_screenshot(project_id)
                Project.remove_screenshot_blob(blob_key)

                Project.update_project(project_id, title=title, screenshot=screenshot, 
                    screenshot_url=screenshot_url, url=url, description=description)
            else:
                if upload_files and not errormsg:
                    # same as above
                    blobstore.delete(blob_info.key())
                if not errormsg:
                    errormsg = 'All fields are mandatory (except for screenshot)'
                user = User.get_user(username)
                projects = Project.get_projects_by_ids(user.projects)
                upload_url = blobstore.create_upload_url('/' + username, max_bytes_per_blob=self.MAX_IMG_SIZE)
                template = 'profile/edit_project.html'
                context = { 'user': user,
                            'username': username,
                            'title': title,
                            'url': url,
                            'description': description,
                            'projects': projects,
                            'upload_url': upload_url,
                            'errormsg': errormsg }
                self.render(template, context)
                return
        elif mode == 'remove_project':
            project_id = self.request.get('project_id')
            Project.remove_project(project_id)
            User.remove_project(username, project_id)
            
        else:
            pass
        self.redirect('/'+username)


