from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import User

# 회원가입 테스트
class UserRegistrationTest(APITestCase):
    # 모든 테스트 시작 전 호출되는 함수
    def setUp(self):
        self.data = {"email": "test@mail.com", "password":"test"}
        self.user = User.objects.create_user("test@mail.com", "test")
        
    # 모든 테스트 마지막 호출 되는 함수
    def tearDown(self):
        pass
    
    # 중복된 아이디로 회원가입 시 (400)
    def test_registration_duplicate(self):
        url = reverse("join_view")
        user_data = {
            "email" : "test@mail.com",
            "username": "중복",
            "password": "test",
            "password_confirm": "test"
        }
        response = self.client.post(url, user_data)
        # print(response.data)
        self.assertEqual(response.status_code, 400)
        
    # 정상적인 회원가입 (201)
    def test_registration(self):
        url = reverse("join_view")
        user_data = {
            "email" : "newtest@mail.com",
            "username": "패스",
            "password": "newtest",
            "password_confirm": "newtest"
        }
        response = self.client.post(url, user_data)
        # print(response.data)
        self.assertEqual(response.status_code, 201)
        
# 로그인 테스트
class LoginUserTest(APITestCase):
    # 로그인 테스트할 계정
    def setUp(self):
        self.data = {"email": "test@mail.com", "password":"test"}
        self.data_none_pwd = {"email": "test@mail.com"}
        self.data_none_email = {"password":"test"}
        self.user = User.objects.create_user("test@mail.com", "test")
        
    # 정상 로그인
    def test_login(self):
        response = self.client.post(reverse("token_obtain_pair"), self.data)
        # print(response.data["access"])
        self.assertEqual(response.status_code, 200)
    
    # 패스워드 없을 경우
    def test_login_miss_pwd(self):
        response = self.client.post(reverse("token_obtain_pair"), self.data_none_pwd)
        self.assertEqual(response.status_code, 400)
        
    # 아이디 없을 경우
    def test_login_miss_email(self):
        response = self.client.post(reverse("token_obtain_pair"), self.data_none_email)
        self.assertEqual(response.status_code, 400)
        
    # 유저 정보 확인
    def test_get_user_data(self):
        # 액세스 토큰을 받아와서 HTTP_AUTHORIZATION에 주는 것이 중요!
        access_token = self.client.post(reverse("token_obtain_pair"), self.data).data['access']
        response = self.client.get(
            path=reverse("user_view"),
            HTTP_AUTHORIZATION = f"Bearer {access_token}"
        )
        print(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['email'], self.data['email'])