from rest_framework.test import APITestCase, APIClient, APIRequestFactory
from django.test import TestCase, Client
from rest_framework import status
from django.urls import reverse
from boards.models import User, Profile, Project, ProjectMembership, Task, Board
from boards.serializers import UserSerializer, ProfileSerializer, ProjectListSerializer, ProjectSerializer, ProjectMembershipSerializer
from boards.permissions import CanViewProfile, CanEditProject
from boards.views import ProfileDetailView


class RegisterViewTestCase(APITestCase):
    def test_register(self):
        url = reverse('users')
        data = {'username': 'test_user',
                'password' : 'testpassword',
                'password2' : 'testpassword'}
        response = self.client.post(path=url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['username'], 'test_user')
        # Duplicate username
        data = {'username': 'test_user',
                'password' : 'testpassword222',
                'password2' : 'testpassword222'}
        response = self.client.post(path=url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('users')
        self.user_data = {'username': 'testuser', 'password': 'testpassword', 'password2': 'testpassword'}

    def test_create_user(self):
        response = self.client.post(self.url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, 'testuser')

    def test_list_users(self):
        # Create a user to list
        User.objects.create(username='testuser2', password='testpassword2')
        
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # به خاطر صفحه بندی 4 شده، اگر صفحه بندی را کامنت کنید همان 1 نتیجه حاصل میشه
        self.assertEqual(len(response.data), 4)
        self.assertEqual(response.data['results'][0]['username'], 'testuser2')


class ProfileViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('profiles')
        self.user_data = {'username': 'testuser', 'password': 'testpassword', 'password2': 'testpassword'}

    def test_list_users(self):
        # Create a user to list
        user2 = User.objects.create(username='testuser2', password='testpassword2')
        Profile.objects.update(user=user2, profile_name='testprofile', bio='test_profile_bio')

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)
        self.assertEqual(response.data['results'][0]['profile_name'], 'testprofile')
        self.assertEqual(response.data['results'][0]['bio'], 'test_profile_bio')


class ProfileDetailViewTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(username='testuser', password='testpassword')
        Profile.objects.update(profile_name='TestProfile', bio='Test Bio')
        self.profile = Profile.objects.get(user=self.user)
        self.url = reverse('profile_detail', kwargs={'pk': self.profile.pk})
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serializer = ProfileSerializer(instance=self.profile)
        self.assertEqual(response.data, serializer.data)

    def test_update_profile(self):
        updated_data = {'profile_name': 'UpdatedProfile', 'bio': 'Updated Bio'}
        response = self.client.put(self.url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.profile_name, 'UpdatedProfile')
        self.assertEqual(self.profile.bio, 'Updated Bio')


    def test_delete_profile(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(Profile.DoesNotExist):
            self.profile.refresh_from_db()

    def test_user_can_view_own_profile(self):
        another_user = User.objects.create(username='anotheruser', password='anotherpassword')
        Profile.objects.update(profile_name='AnotherProfile', bio='Another Bio')
        another_profile = Profile.objects.get(user=another_user)
        url_another_profile = reverse('profile_detail', kwargs={'pk': another_profile.pk})
        
        response = self.client.get(url_another_profile)
        self.assertEqual(response.status_code, status.HTTP_200_OK)



class ProjectListViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(username='testuser', password='testpassword')
        self.profile = Profile.objects.get(user=self.user)
        self.client.force_authenticate(user=self.user)

    def create_project(self, title, description):
        return Project.objects.create(title=title, description=description, owner=self.profile)

    def test_list_projects(self):
        # Create two projects for testing pagination
        project1 = self.create_project(title='Project1', description='Description1')
        project2 = self.create_project(title='Project2', description='Description2')

        response = self.client.get(reverse('project_list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serializer = ProjectListSerializer(instance=[project1, project2], many=True)
        self.assertEqual(response.data['results'], serializer.data)

    def test_create_project(self):
        data = {'title': 'New Project', 'description': 'Project Description', 'owner': self.profile.pk}
        response = self.client.post(reverse('project_list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Project.objects.count(), 1)
        self.assertEqual(Project.objects.get().title, 'New Project')


class ProjectDetailViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.profile = Profile.objects.get(user=self.user)
        self.project = Project.objects.create(title='Test Project', description='Project Description', owner=self.profile)
        self.url = reverse('project_detail', kwargs={'pk': self.project.pk})
        self.client.force_authenticate(user=self.user)

    def test_retrieve_project(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serializer = ProjectSerializer(instance=self.project)
        self.assertEqual(response.data, serializer.data)

    def test_update_project(self):
        updated_data = {'title': 'Updated Project', 'description': 'Updated Description'}
        response = self.client.put(self.url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, 'Updated Project')
        self.assertEqual(self.project.description, 'Updated Description')

    def test_delete_project(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(Project.DoesNotExist):
            self.project.refresh_from_db()

    def test_unauthenticated_user_cannot_access(self):
        unauthenticated_client = APIClient()
        response = unauthenticated_client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_cannot_edit_project_they_do_not_own(self):
        another_user = User.objects.create_user(username='anotheruser', password='anotherpassword')
        another_profile = Profile.objects.get(user=another_user)
        another_project = Project.objects.create(title='Another Project', description='Another Description', owner=another_profile)
        url_another_project = reverse('project_detail', kwargs={'pk': another_project.pk})
        
        response = self.client.put(url_another_project, {'title': 'Changed Title'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_can_edit_own_project(self):
        response = self.client.put(self.url, {'title': 'Changed Title'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, 'Changed Title')


class ProjectMemberListViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.profile = Profile.objects.get(user=self.user)
        self.project = Project.objects.create(title='Test Project', description='Project Description', owner=self.profile)
        self.url = reverse('members_list', kwargs={'pk': self.project.pk})
        self.client.force_authenticate(user=self.user)

    def create_project_membership(self, access_level=ProjectMembership.Access.MEMBER):
        self.user2 = User.objects.create_user(username='testuser2', password='testpassword2')
        self.profile2 = Profile.objects.get(user=self.user2)
        return ProjectMembership.objects.create(project=self.project, member=self.profile2, access_level=access_level)

    def test_list_project_members(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_project_members_invalid_project_id(self):
        invalid_url = reverse('project_detail', kwargs={'pk': 999})  # Assuming project ID 999 does not exist
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_add_project_member(self):
        self.user2 = User.objects.create_user(username='testuser2', password='testpassword2')
        self.profile2 = Profile.objects.get(user=self.user2)
        data = {'project': self.project.pk, 'member': self.profile2.pk, 'access_level': ProjectMembership.Access.MEMBER}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ProjectMembership.objects.count(), 2)
        self.assertEqual(str(ProjectMembership.objects.get(access_level=1)), f'{self.profile2} | {self.project.title}')


