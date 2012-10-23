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
        elif mode == 'edit_project':
            template = 'profile/edit_project.html'
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
                       'projects': projects}

            self.render(template, context)
        else:
            self.redirect('/logout')

    #@Authentication.do
    def post(self, username):
        mode = self.request.get('mode')
        if mode == 'add_project':
            title = self.request.get('title').strip()
            screenshot = self.request.get('screenshot').strip()
            url = self.request.get('url').strip()
            description = self.request.get('description').strip()
            
            if title and screenshot and url and description:
                project_id = Project.add_project(title=title, screenshot=screenshot, 
                                url=url, description=description)

                User.add_project(username, project_id)
            else:
                user = User.get_user(username)
                template = 'profile/add_project.html'
                context = { 'user': user,
                            'username': username,
                            'title': title,
                            'screenshot': screenshot,
                            'url': url,
                            'description': description,
                            'errormsg': 'All fields are manadatory'}
                self.render(template, context)
                return
        elif mode == 'edit_project':
            project_id = self.request.get('projects_dropdown')
            title = self.request.get('title').strip()
            screenshot = self.request.get('screenshot').strip()
            url = self.request.get('url').strip()
            description = self.request.get('description').strip()
            if title and screenshot and url and description:
                Project.update_project(project_id, title=title, screenshot=screenshot, 
                                url=url, description=description)
            else:
                user = User.get_user(username)
                projects = Project.get_projects_by_ids(user.projects)
                template = 'profile/edit_project.html'
                context = { 'user': user,
                            'username': username,
                            'title': title,
                            'screenshot': screenshot,
                            'url': url,
                            'description': description,
                            'projects': projects,
                            'errormsg': 'All fields are manadatory'}
                self.render(template, context)
                return
        elif mode == 'remove_project':
            project_id = self.request.get('project_id')
            Project.remove_project(project_id)
            User.remove_project(username, project_id)
        else:
            pass
        self.redirect('/'+username)
