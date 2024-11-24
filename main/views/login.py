from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from ..models.profile import Profile
from django.contrib.auth import authenticate, get_user_model
from django.http import JsonResponse
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

# Swagger 요청 스키마 정의
login_request_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'username': openapi.Schema(type=openapi.TYPE_STRING, description='사용자 아이디'),
        'password': openapi.Schema(type=openapi.TYPE_STRING, description='비밀번호'),
    },
    required=['username', 'password']
)

# Swagger 응답 스키마 정의
login_success_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'message': openapi.Schema(type=openapi.TYPE_STRING, description='성공 메시지'),
        'username': openapi.Schema(type=openapi.TYPE_STRING, description='사용자 아이디'),
        'profile_required': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='프로필 생성 필요 여부'),
        'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='JWT 리프레시 토큰'),
        'access': openapi.Schema(type=openapi.TYPE_STRING, description='JWT 액세스 토큰'),
    }
)

login_error_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'error': openapi.Schema(type=openapi.TYPE_STRING, description='오류 메시지'),
    }
)

class LoginView(APIView):
    @swagger_auto_schema(
        operation_summary="로그인",
        operation_description="사용자의 아이디와 비밀번호를 확인하여 JWT 토큰을 발급합니다.",
        request_body=login_request_schema,
        responses={
            200: openapi.Response(description="로그인 성공", schema=login_success_schema),
            401: openapi.Response(description="로그인 실패", schema=login_error_schema),
            500: openapi.Response(description="서버 오류", schema=login_error_schema),
        }
    )
    def post(self, request):
        """
        로그인 API
        사용자 인증 후 JWT 토큰과 프로필 생성 여부를 반환합니다.
        """
        try:
            data = request.data
            username = data.get('username')
            password = data.get('password')

            user = authenticate(request, username=username, password=password)
            if user is not None:
                # JWT 토큰 생성
                refresh = RefreshToken.for_user(user)

                # 프로필 존재 여부 확인
                profile_exists = Profile.objects.filter(user=user).exists()

                return JsonResponse({
                    'message': '로그인 성공!',
                    'username': user.username,
                    'profile_required': not profile_exists,
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }, status=200)
            else:
                return JsonResponse({'error': '로그인 실패. 아이디 또는 비밀번호를 확인하세요.'}, status=401)
        except Exception as e:
            return JsonResponse({'error': f'오류가 발생했습니다: {str(e)}'}, status=500)

