from django.shortcuts import render, get_object_or_404
from .models import Profile, Project, Task, Board, ProjectMembership
from .serializers import (ProfileSerializer, UserSerializer, ProjectListSerializer, 
                          ProjectSerializer, ProjectMembershipSerializer, BoardSerializer, TaskSerializer)
from rest_framework.response import Response
from rest_framework import status, generics
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated
from .permissions import CanViewProfile, CanEditProject, IsAdminOrMemberReadOnly
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination


class TrelloPaginationsView(PageNumberPagination):
    page_size = 10


class UserView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = TrelloPaginationsView


class ProfileView(generics.ListAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    pagination_class = TrelloPaginationsView


class ProfileDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [CanViewProfile]


class ProjectListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Project.objects.all()
    serializer_class = ProjectListSerializer
    pagination_class = TrelloPaginationsView


class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [CanEditProject, IsAuthenticated]
 

class ProjectMemberListView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = TrelloPaginationsView
    def get(self, request, pk):
        project = Project.objects.get(pk=pk)
        members = ProjectMembership.objects.filter(project=project)
        for member in members:
            if request.user.id == member.member_id:
                members_serializer = ProjectMembershipSerializer(instance=members, many=True)
                return Response(members_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
    
    def post(self, request, pk):
        project = Project.objects.get(pk=pk)
        members = ProjectMembership.objects.filter(project=project)
        member_deserializer = ProjectMembershipSerializer(data=request.data)
        pmem_admin = get_object_or_404(ProjectMembership, project_id=pk, access_level=2)
        if request.user.id == pmem_admin.member_id:
            for member in members:
                if (request.data['member'] == member.id) or (request.data['project'] != pk):
                    return Response(status=status.HTTP_400_BAD_REQUEST)
            else:
                if member_deserializer.is_valid():
                    member_deserializer.save()
                    return Response(member_deserializer.data, status=status.HTTP_200_OK)
                return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class ProjectMemberDetailView(APIView):
    permission_classes = [IsAdminOrMemberReadOnly]
    def get(self, request, proj_id, mem_id):
        pmem = get_object_or_404(ProjectMembership, pk=mem_id, project_id=proj_id)
        pmem_serializer = ProjectMembershipSerializer(instance=pmem, context={'request': request})
        pmem_admin = get_object_or_404(ProjectMembership, project_id=proj_id, access_level=2)
        if request.user.id == pmem_admin.member_id:
            return Response(pmem_serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    
    def delete(self, request, proj_id, mem_id):
        pmem = get_object_or_404(ProjectMembership, pk=mem_id, project_id=proj_id)
        pmem_admin = get_object_or_404(ProjectMembership, project_id=proj_id, access_level=2)
        if request.user.id == pmem_admin.member_id:
            pmem.delete()
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)



class BoardListView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = TrelloPaginationsView

    def get(self, request, proj_id):
        project = get_object_or_404(Project, pk=proj_id)
        pmem = ProjectMembership.objects.filter(project_id=project.id)
        board = Board.objects.filter(project_id=project.id)
        board_serializer = BoardSerializer(instance=board, many=True, context={'request': request})
        for member in pmem:
            if request.user.id == member.member_id:
                return Response(board_serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    def post(self, request, proj_id):
        project = get_object_or_404(Project, pk=proj_id)
        pmem = ProjectMembership.objects.filter(project_id=project.id)
        board_serializer = BoardSerializer(data=request.data)
        for member in pmem:
            if request.user.id == member.member_id and member.access_level == 2 and board_serializer.is_valid():
                board_serializer.save()
                return Response(board_serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)



class BoardDetailsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, proj_id, board_id):
        project = get_object_or_404(Project, pk=proj_id)
        pmem = ProjectMembership.objects.filter(project_id=project.id)
        board = get_object_or_404(Board, project_id=project.id, pk=board_id)
        board_serializer = BoardSerializer(instance=board)
        for member in pmem:
            if request.user.id == member.member_id:
                return Response(board_serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, proj_id, board_id):
        project = get_object_or_404(Project, pk=proj_id)
        pmem = ProjectMembership.objects.filter(project_id=project.id)
        board = get_object_or_404(Board, project_id=project.id, pk=board_id)
        board_serializer = BoardSerializer(instance=board, data=request.data)
        for member in pmem:
            if request.user.id == member.member_id and member.access_level == 2 and board_serializer.is_valid():
                board_serializer.save()
                return Response(board_serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, proj_id, board_id):
        project = get_object_or_404(Project, pk=proj_id)
        pmem = ProjectMembership.objects.filter(project_id=project.id)
        board = get_object_or_404(Board, project_id=project.id, pk=board_id)
        for member in pmem:
            if request.user.id == member.member_id and member.access_level == 2:
                board.delete()
                return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class TaskListView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = TrelloPaginationsView

    def get(self, request, proj_id, board_id):
        pmem = ProjectMembership.objects.filter(project_id=proj_id)
        tasks = Task.objects.filter(project_id=proj_id, board_id=board_id)
        task_serializer = TaskSerializer(instance=tasks, many=True, context={'request': request})
        for member in pmem:
            if request.user.id == member.member_id:
                return Response(task_serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    def post(self, request, proj_id, board_id):
        task_serializer = TaskSerializer(data=request.data)
        pmem_admin = get_object_or_404(ProjectMembership, project_id=proj_id, access_level=2)
        if request.user.id == pmem_admin.member_id and task_serializer.is_valid():
            task_serializer.save()
            return Response(task_serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class TaskEditView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, proj_id, board_id, task_id):
        pmem = ProjectMembership.objects.filter(project_id=proj_id)
        task = Task.objects.filter(project_id=proj_id, board_id=board_id, pk=task_id)
        task_serializer = TaskSerializer(instance=task, many=True, context={'request': request})
        for member in pmem:
            if request.user.id == member.member_id:
                return Response(task_serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, proj_id, board_id, task_id):
        pmem = ProjectMembership.objects.filter(project_id=proj_id)
        task = get_object_or_404(Task, project_id=proj_id, board_id=board_id, id=task_id)
        task_serializer = TaskSerializer(instance=task, data=request.data)
        if task.status_task == 'todo':
            for member in pmem:
                if request.user.id == member.member_id and task_serializer.is_valid():
                    task_serializer.save()
                    return Response(task_serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            if request.user.id == task.profile_id and task_serializer.is_valid():
                task_serializer.save()
                return Response(task_serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            
    def delete(self, request, proj_id, board_id, task_id):
        pmem = ProjectMembership.objects.filter(project_id=proj_id)
        task = get_object_or_404(Task, project_id=proj_id, board_id=board_id, id=task_id)

        for member in pmem:
            if request.user.id == member.member_id and member.access_level == 2:
                task.delete()
                return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)
        


        

