import logging
from datetime import date, timedelta

from google.appengine.api import images
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.ndb import Key, get_multi

from BaseHandler import *
from helpers.validators import *
from jinja_custom.helpers import get_gravatar
from models.Course import Course
from models.User import User
from models.Project import Project


class ProfilePage(BaseHandler, blobstore_handlers.BlobstoreUploadHandler):
    MAX_IMG_SIZE = 1048576 # in bytes

    def organize_courses_for(self, user):
        all =  user.get_all_courses()
        cc = get_multi([c.course for c in all if c.completed == True])
        ic = get_multi([c.course for c in all if c.completed == False])

        return all, ic, cc

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
        elif mode == 'edit':
            template = 'profile/edit.html'
        else:
            template = 'profile/profile.html'

           

        user = User.get_user(username)

        if not user:
            user = User.save(username, '{}@someplace.com'.format(username), 'some long password')


        gravatar = user.avatar_url
        friends = []

        

        if user:
            all, ic, cc = self.organize_courses_for(user)

            if user.dob:
                dob = user.dob.strftime('%m/%d/%Y')
            else:
                dob = None

            projects = Project.get_projects_by_ids(user.projects)

            context = {'user': user,
                       'dob': dob,
                       'username': username,
                       'gravatar': gravatar,
                       'friends': friends,
                       'friend_btn': False,
                       'courses_all': Course.courses_to_dict(),
                       'courses_completed': cc,
                       'courses_incomplete': ic,
                       'projects': projects,
                       'upload_url': upload_url,
                       'errors': {}}

            self.render(template, context)
        else:
            self.redirect('/logout')

    def clean_user_data(self, user, **kwargs):
        if not kwargs['password'] and not kwargs['password_confirm']:
            del kwargs['password']
            del kwargs['password_confirm']
            p = {}
        else:
            _, p = User.valid_passwords(kwargs['password'], kwargs['password_confirm'])
        _, e = User.valid_email(kwargs['email'], user)
        _, b = User.valid_date(kwargs['dob'])


        if user.email != kwargs['email']:
            valid, e = User.valid_email(kwargs['email'])

        #TODO: should probably rename this, it can add whatever 3 dictionaries
        errors = User.adduep(p, e, b)

        return errors

    #@Authentication.do
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

            url = self.request.get('url').strip()
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
                            'url': url,
                            'short_description': short_description,
                            'upload_url': upload_url,
                            'titleerror': titleerror,
                            'urlerror': urlerror,
                            'sderror': sderror,
                            'fileerror': fileerror}
                self.render(template, context)
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

            url = self.request.get('url').strip()
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
                            'url': url,
                            'short_description': short_description,
                            'projects': projects,
                            'upload_url': upload_url,
                            'titleerror': titleerror,
                            'urlerror': urlerror,
                            'sderror': sderror,
                            'fileerror': fileerror }
                self.render(template, context)
                return
            else:
                Project.update_project(project_id, title=title, screenshot=screenshot, 
                    screenshot_url=screenshot_url, url=url, short_description=short_description)
        elif mode == 'remove_project':
            project_id = self.request.get('project_id')
            Project.remove_project(project_id)
            User.remove_project(username, project_id)
            
        elif mode == 'edit':
            fields = self.get_params_dict((
                'real_name',
                'email',
                'short_about',
                'dob',
                'tools',
                'password',
                'password_confirm',
                'notify_on_msg'
                ))
            logging.error(fields)

            iclasses = self.request.get_all('classes_inprog')
            cclasses = self.request.get_all('classes_completed')
            fields['iclasses'] = iclasses
            fields['cclasses'] = cclasses
            fields['username'] = username

            user = Key(User, username).get()

            errors = self.clean_user_data(user, **fields)

            context = {
                'errors': errors,
                'user': user
            }

            if not errors:
                user.update(**fields)
                self.redirect('/{}'.format(username))
            else:

                if user.dob:
                    dob = user.dob.strftime('%m/%d/%Y')
                else:
                    dob = None
                all, ic, cc = self.organize_courses_for(user)
                context['courses_all'] = Course.courses_to_dict()
                context['courses_completed'] = cc
                context['courses_incomplete'] = ic
                context['dob'] = dob
                context['username'] = username
                context['gravatar'] = user.avatar_url
                context['friends'] = []
                context['friend_btn'] = False
                context['errors'] = errors
                self.render('profile/edit.html'.format(username), context)
                return
        self.redirect('/'+username)