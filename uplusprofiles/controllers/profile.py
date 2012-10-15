from BaseHandler import *
from jinja_custom.helpers import get_gravatar
from models.Course import Course
from models.User import User
from models.Project import Project
from datetime import date, timedelta
import logging


class ProfilePage(BaseHandler):
    #@Authentication.do
    def get(self, username):
        """display profile of user with username, if None, display logged in user
        """
        mode = self.request.get('mode')

        if mode == 'add_project':
            template = 'profile/add_project.html'
        else:
            template = 'profile/profile.html'


        user = User.get_user(username)
        if not user:
            user = User.save(username, '{}@someplace.com'.format(username), 'some long password')


        dob = user.created - 13 * timedelta(days=365)

        gravatar = user.avatar_url
        friends = []

        courses = Course.query()

        project_ids = user.projects
        projects = []
        if project_ids:
            for project_id in project_ids:
                projects.append(Project.get_by_id(project_id))

        if user:
            context = {'user': user, 'dob': dob,
                       'username': username,
                       'gravatar': gravatar,
                       'friends': friends,
                       'friend_btn': False,
                       'courses': courses,
                       'projects': projects}

            self.render(template, context)
        else:
            self.redirect('/logout')

    #@Authentication.do
    def post(self, username):
        mode = self.request.get('mode')
        if mode == 'add_project':
            title = self.request.get('title')
            screenshot = self.request.get('screenshot')
            url = self.request.get('url')
            description = self.request.get('description')
            # TODO: validation

            project_id = Project.add_project(title=title, screenshot=screenshot, 
                                url=url, description=description)
            user = User.get_user(username)
            projects = user.projects
            if projects:
                projects.append(project_id)
            else:
                projects = [project_id]
            user.projects = projects
            user.put()
        else:
            pass
        self.redirect('/'+username)
