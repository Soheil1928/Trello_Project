from django.test import TestCase
from boards.models import User, Profile, Project, ProjectMembership, Task, Board


class UserModelTestCase(TestCase):
    def test_create_user(self):
        username = 'test_user'
        password = 'testpassword'
        user = User.objects.create(username=username)
        user.set_password(password)

        self.assertEqual(user.username, username)
        self.assertTrue(user.is_active)
        self.assertTrue(user.check_password(password))
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)


class ProfileModelTestCase(TestCase):
    def test_edit_profile(self):
        user = User.objects.create(username='test_user')
        user.set_password('testpassword')

        profile_name = 'testprofile'
        bio = 'this is a bio test'
        Profile.objects.update(user=user.id, profile_name=profile_name, bio=bio)
        user_edit = Profile.objects.get(profile_name=profile_name)

        self.assertEqual(user_edit.id, user.id)
        self.assertEqual(user_edit.profile_name, 'testprofile')
        self.assertEqual(user_edit.bio, 'this is a bio test')


class ProjectModelTestCase(TestCase):
    def test_create_project(self):
        user = User.objects.create(username='test_user')
        user.set_password('testpassword')
        profile = Profile.objects.get(id=user.id)
        project = Project.objects.create(title='test_project', description='test description', owner=profile)

        self.assertEqual(project.title, 'test_project')
        self.assertEqual(project.description, 'test description')
        self.assertEqual(project.owner, profile)



class ProjectMembershipModelTestCase(TestCase):
    def test_create_member(self):
        user1 = User.objects.create(username='test_user1')
        user1.set_password('testpassword1')
        profile1 = Profile.objects.get(id=user1.id)
        user2 = User.objects.create(username='test_user2')
        user2.set_password('testpassword2')
        profile2 = Profile.objects.get(id=user2.id)
        project = Project.objects.create(title='test_project', description='test description', owner=profile1)
        member1 = ProjectMembership.objects.get(project=project, member=profile1)
        member2 = ProjectMembership.objects.create(project=project, member=profile2)

        self.assertEqual(member1.access_level, 2)
        self.assertEqual(member2.access_level, 1)
        self.assertNotEqual(member1.access_level, 1)
        self.assertNotEqual(member2.access_level, 2)
        self.assertEqual(member2.project.title, 'test_project')
        self.assertNotEqual(member2.project.title, 'test_project_test')
        

class TaskModelTestCase(TestCase):
    def test_create_task(self):
        user = User.objects.create(username='test_user')
        user.set_password('testpassword')
        profile = Profile.objects.get(id=user.id)
        project = Project.objects.create(title='test_project', description='test description project', owner=profile)
        board = Board.objects.create(title='test_board', description='test description board', project=project)
        task = Task.objects.create(title='test_task', description='test description task', board=board, project=project)

        self.assertEqual(task.title, 'test_task')
        self.assertEqual(task.description, 'test description task')
        self.assertEqual(task.board, board)
        self.assertEqual(task.project, project)
        self.assertEqual(task.status_task, 'todo')
        self.assertNotEqual(task.status_task, 'doing')
        self.assertNotEqual(task.status_task, 'suspend')
        self.assertNotEqual(task.status_task, 'done')