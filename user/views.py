from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Skills
from .models import User as UserModel
from .models import UserProfile as UserProfileModel
from .serializers import UserSerializer, UserJoinSerializer, UserProfileDetailSerializer
from .serializers import SkillsSerializer

from project.models import Project as ProjectModel
from project.serializers import ProjectViewSerializer
# S3 업로드 관련
import boto3
import my_settings


# user/upload/
class UploadS3(APIView):
    # S3에 이미지 업로드 후 URL 리턴
    def post(self, request):
        file = request.data["file"]
        print(file)
        
        s3 = boto3.client('s3',
                          aws_access_key_id = my_settings.AWS_ACCESS_KEY,
                          aws_secret_access_key = my_settings.AWS_SECRET_KEY,
                          region_name = my_settings.REGION_NAME,
                          )
        
        file_name = str(file).split('.')[0]
        file_extension = str(file).split('.')[1]
        
        s3.put_object(
            ACL="public-read",
            Bucket="toastuitestbucket",
            Body=file,
            Key=file_name,
            ContentType=file.content_type
            )
        url =  "https://toastuitestbucket.s3.ap-northeast-2.amazonaws.com/"+ file_name + '.' + file_extension
        return Response({"success":"업로드 성공!", "url": url})


# user/join/
class JoinView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        join_serializer = UserJoinSerializer(data=request.data)
        if join_serializer.is_valid():
            join_serializer.save()
            return Response({"user" : join_serializer.data, "msg" : "회원가입 완료"}, status=status.HTTP_201_CREATED)
        return Response(join_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# user/profile/
class UserAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    # 로그인한 유저 정보 출력
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    # 로그인한 유저프로필 수정
    def put(self, request):
        user = UserProfileModel.objects.get(user_id=request.user.id)
        serializer = UserProfileDetailSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    # 유저 탈퇴
    def delete(self, request):
        UserModel.objects.get(id=request.user.pk).delete()
        return Response({"success": "탈퇴되었습니다!"}, status=status.HTTP_200_OK)



# user/profile/<user_id>
class AnotherUserAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    # 다른 유저 정보 보기
    def get(self, request, user_id):
        user = UserModel.objects.get(id=user_id)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    


# user/profile/project/
class MyProjectView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    # 나의 프로젝트 출력
    def get(self, request):
        project = ProjectModel.objects.filter(user_id=request.user.pk)
        project_serializer = ProjectViewSerializer(project, many=True)
        return Response(project_serializer.data, status=status.HTTP_200_OK)
    
    
# user/profile/project/bookmark
class MyBookmarkProjectView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    # 내가 북마크한 프로젝트 출력
    def get(self, request):
        project = ProjectModel.objects.filter(bookmark=request.user.pk)
        project_serializer = ProjectViewSerializer(project, many=True)
        return Response(project_serializer.data, status=status.HTTP_200_OK)


# utils - QueryDebugger
from _utils.query_utils import query_debugger # Query Debugger

# project/user/
class GetBaseInfoView(APIView):
    @query_debugger
    def get(self, request):
        skills = Skills.objects.all()
        skills_data = SkillsSerializer(skills, many=True).data
        # user.username과
        # 
        # request.user
        # login_user_id = request.query_params.get('user_id')
        return Response({"login_username": request.user.username, "skills":skills_data}, status=status.HTTP_200_OK)

