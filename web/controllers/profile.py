from google.appengine.ext.ndb import Key, get_multi
import logging

from google.appengine.api import images
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from boilerplate.lib.basehandler import user_required
#from boilerplate.lib.basehandler import BaseHandler
from web.controllers.BaseHandler import BaseHandler
from web.controllers.helpers.validators import *
from web.models.Project import Project
from web.models.User import User
from web.models.Course import Course
import webapp2
from web.util import forms

class ProfilePage(BaseHandler, blobstore_handlers.BlobstoreUploadHandler):
    MAX_IMG_SIZE = 1048576 # in bytes
    
    def organize_courses_for(self, user):
        all =  user.get_all_courses()
        cc = get_multi([c.course for c in all if c.completed == True])
        ic = get_multi([c.course for c in all if c.completed == False])

        return all, ic, cc

    def organize_courses_for(self, user):
        all =  user.get_all_courses()
        cc = get_multi([c.course for c in all if c.completed == True])
        ic = get_multi([c.course for c in all if c.completed == False])

        return all, ic, cc

    @webapp2.cached_property
    def form(self):
        if self.is_mobile:
            return forms.EditProfileForm(self)
        else:
            return forms.EditProfileForm(self)

    @user_required
    def get(self, username):
        """display profile of user with username, if None, display logged in user
        """
        mode = self.request.get('mode')
        upload_url = ""

        if not mode:
            template = 'profile/profile.html'
        elif mode == 'edit':
            template = 'profile/edit.html'
        elif mode == 'add_project':
            template = 'profile/add_project.html'
            upload_url = blobstore.create_upload_url('/' + username, max_bytes_per_blob=self.MAX_IMG_SIZE)
        elif mode == 'edit_project':
            template = 'profile/edit_project.html'
            upload_url = blobstore.create_upload_url('/' + username, max_bytes_per_blob=self.MAX_IMG_SIZE)
        else:
            template = 'profile/profile.html'

        if self.user:
            user = User.get_by_id(long(self.user_id))
        else:
            user = User.get_user(username)

        self.form.process(obj=user)

        friends = []

        if user:
            all, ic, cc = self.organize_courses_for(user)

            projects = Project.get_projects_by_ids(user.projects)

            context = {
                        'user': user,
                       'gravatar': user.gravatar,
                       'friends': friends,
                       'friend_btn': False,
                       'courses_all': Course.courses_to_dict(),
                       'courses_completed': cc,
                       'courses_incomplete': ic,
                       'projects': projects,
                       'upload_url': upload_url,
            }

            self.render_template(template, **context)
        else:
            self.redirect('/logout')

    @user_required
    def post(self, username):
        mode = self.request.get('mode')
        if mode == 'add_project':
            blob_info = None
            fileerror = 'Screenshot is mandatory'
            upload_files = self.get_uploads('screenshot')
            if upload_files:
                blob_info = upload_files[0]
                if 'image' in blob_info.content_type:
                    screenshot = blob_info.key()
                    screenshot_url = images.get_serving_url(screenshot)
                    fileerror = ''
                else:
                    # uploaded file wasn't an images, hence remove from the blobstore
                    blobstore.delete(blob_info.key())
                    fileerror = 'Invalid image type'
            else:
                fileerror = 'Please provide a screenshot of your project (max size: 1MB)'

            title = self.request.get('title').strip()
            titleerror = validate_project_title(title)

            url = self.request.get('proj_url').strip()
            urlerror = validate_project_url(url)

            short_description = self.request.get('short_description').strip()
            sderror = validate_project_short_description(short_description)

            if titleerror or urlerror or sderror or fileerror:
                if blob_info and not fileerror:
                    # blob was okay but validation of some other field failed
                    # hence remove it to avoid orphaned entry
                    # also remove the serving url
                    Project.remove_screenshot_blob(blob_info.key())

                user = User.get_user(username)
                template = 'profile/add_project.html'
                upload_url = blobstore.create_upload_url('/' + username, max_bytes_per_blob=self.MAX_IMG_SIZE)
                context = { 'user': user,
                            'username': username,
                            'title': title,
                            'proj_url': url,
                            'short_description': short_description,
                            'upload_url': upload_url,
                            'titleerror': titleerror,
                            'urlerror': urlerror,
                            'sderror': sderror,
                            'fileerror': fileerror}
                self.render_template(template, context)
                return
            else:
                user = User.get_user(username)
                project_id = Project.add_project(title=title, screenshot=screenshot,
                    screenshot_url=screenshot_url, url=url, short_description=short_description,
                    author=user.key)

                User.add_project(username, project_id)

        elif mode == 'edit_project':
            blob_info = None
            screenshot = None
            screenshot_url = None
            fileerror = ''

            upload_files = self.get_uploads('screenshot')
            if upload_files:
                blob_info = upload_files[0]
                if 'image' in blob_info.content_type:
                    screenshot = blob_info.key()
                    screenshot_url = images.get_serving_url(screenshot)
                else:
                    # uploaded file wasn't an images, hence remove from the blobstore
                    blobstore.delete(blob_info.key())
                    fileerror = 'Invalid image type'

            project_id = self.request.get('projects_dropdown')

            title = self.request.get('title').strip()
            titleerror = validate_project_title(title)

            url = self.request.get('proj_url').strip()
            urlerror = validate_project_url(url)

            short_description = self.request.get('short_description').strip()
            sderror = validate_project_short_description(short_description)

            if titleerror or urlerror or sderror or fileerror:
                if blob_info and not fileerror:
                    # same as above
                    Project.remove_screenshot_blob(blob_info.key())

                user = User.get_user(username)
                projects = Project.get_projects_by_ids(user.projects)
                upload_url = blobstore.create_upload_url('/' + username, max_bytes_per_blob=self.MAX_IMG_SIZE)
                template = 'profile/edit_project.html'
                context = { 'user': user,
                            'username': username,
                            'title': title,
                            'proj_url': url,
                            'short_description': short_description,
                            'projects': projects,
                            'upload_url': upload_url,
                            'titleerror': titleerror,
                            'urlerror': urlerror,
                            'sderror': sderror,
                            'fileerror': fileerror }
                self.render_template(template, context)
                return
            else:
                Project.update_project(project_id, title=title, screenshot=screenshot,
                    screenshot_url=screenshot_url, url=url, short_description=short_description)
        elif mode == 'remove_project':
            project_id = self.request.get('project_id')
            Project.remove_project(project_id)
            User.remove_project(username, project_id)

        elif mode == 'edit':
            if not self.form.validate():
                return self.get(username)
#                self.redirect('/'+username)

            fields = self.get_params_dict((
                'short_about',
                'tools',
                ))

            iclasses = self.request.get_all('classes_inprog')
            cclasses = self.request.get_all('classes_completed')
            fields['iclasses'] = iclasses
            fields['cclasses'] = cclasses
            fields['username'] = username

            user = User.get_user(username)

            user.update(self.form, **fields)
            self.redirect('/{}'.format(username))

        self.redirect('/{}'.format(username))

