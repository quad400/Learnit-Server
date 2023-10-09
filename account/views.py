from urllib.parse import urlencode
from rest_framework import (generics,
                            status,mixins
                            )
from rest_framework import permissions as permission
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import serializers as serial
from django.dispatch import Signal
from django.contrib.auth import login
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.core.mail import EmailMessage

from . import serializers
from .models import UserAccount,Profile,Link,Skills
from core.utils import user_get_or_create
from core.permissions import IsOwnerOrReadOnlyAccount,IsAdminAndStaffOrReadOnly
from .serializers import (
                ProfileSerializer,
                UserCreateSerializer,
                ActivateSerializer,
                SendEmailResetSerializer,
                )
from .services import google_get_access_token,google_get_user_info,jwt_login,GoogleRawLoginFlowService

signal = Signal()
User = get_user_model()


# class GoogleLoginApi(APIView):
#     class InputSerializer(serial.Serializer):
#         code = serial.CharField(required=False)
#         error = serial.CharField(required=False)

#     def get(self, request, *args, **kwargs):
#         input_serializer = self.InputSerializer(data=request.GET)
#         input_serializer.is_valid(raise_exception=True)

#         validated_data = input_serializer.validated_data

#         code = validated_data.get('code')
#         error = validated_data.get('error')

#         login_url = f'{settings.BASE_FRONTEND_URL}/login'

#         if error or not code:
#             params = urlencode({'error': error})
#             return redirect(f'{login_url}?{params}')

#         domain = settings.BASE_BACKEND_URL
#         api_uri = reverse('login-with-google')
#         redirect_uri = f'{domain}/accounts/google/'

#         access_token = google_get_access_token(code=code, redirect_uri=redirect_uri)
#         print(access_token)
#         user_data = google_get_user_info(access_token=access_token)

#         profile_data = {
#             'email': user_data['email'],
#             'fullname': user_data.get('name', ''),
#         }
#         # print(user_data)

#         user= user_get_or_create(profile_data['email'], profile_data['fullname'])
#         print("user:", user)
#         response = redirect(settings.BASE_FRONTEND_URL)
#         # response = jwt_login(response=response, user=user)

#         return Response({"user": user}, status=status.HTTP_200_OK)



class PublicApi(APIView):
    authentication_classes = ()
    permission_classes = ()


class GoogleLoginRedirectApi(PublicApi):
    def get(self, request, *args, **kwargs):
        google_login_flow = GoogleRawLoginFlowService()

        authorization_url, state = google_login_flow.get_authorization_url()

        request.session["google_oauth2_state"] = state

        return redirect(authorization_url)


class GoogleLoginApi(PublicApi):
    class InputSerializer(serial.Serializer):
        code = serial.CharField(required=False)
        error = serial.CharField(required=False)
        state = serial.CharField(required=False)

    def get(self, request, *args, **kwargs):
        input_serializer = self.InputSerializer(data=request.GET)
        input_serializer.is_valid(raise_exception=True)

        validated_data = input_serializer.validated_data

        code = validated_data.get("code")
        error = validated_data.get("error")
        state = validated_data.get("state")

        if error is not None:
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)

        if code is None or state is None:
            return Response({"error": "Code and state are required."}, status=status.HTTP_400_BAD_REQUEST)

        session_state = request.session.get("google_oauth2_state")

        if session_state is None:
            return Response({"error": "CSRF check failed."}, status=status.HTTP_400_BAD_REQUEST)

        del request.session["google_oauth2_state"]

        if state != session_state:
            return Response({"error": "CSRF check failed."}, status=status.HTTP_400_BAD_REQUEST)

        google_login_flow = GoogleRawLoginFlowService()

        google_tokens = google_login_flow.get_tokens(code=code)

        id_token_decoded = google_tokens.decode_id_token()
        user_info = google_login_flow.get_user_info(google_tokens=google_tokens)

        user_email = id_token_decoded["email"]
        request_user_list = User.objects.filter(email=user_email)
        # request_user_list = user_list(filters={"email": user_email})
        user = request_user_list.get() if request_user_list else None

        if user is None:
            return Response({"error": f"User with email {user_email} is not found."}, status=status.HTTP_404_NOT_FOUND)

        login(request, user)

        result = {
            "id_token_decoded": id_token_decoded,
            "user_info": user_info,
        }

        return Response(result)


class UserCreateAPI(generics.CreateAPIView):
    serializer_class = UserCreateSerializer
    queryset = User.objects.all()
    permission_classes = [permission.AllowAny]

    def perform_create(self, serializer, *args, **kwargs):
        return serializer.save(*args, **kwargs)

class ActivationAPI(generics.GenericAPIView):
    serializer_class = ActivateSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.user
        user.is_active = True
        user.save()
        return Response(status=status.HTTP_200_OK)

        

class ProfileDetailUpdate(APIView):
    permission_classes = [permission.IsAuthenticated]

    def get(self, request, **kwargs):
        user = request.user
        qs = get_object_or_404(Profile,user=user)
        serializ = ProfileSerializer(instance=qs)
        return Response(serializ.data, status=status.HTTP_200_OK)

    def put(self, request, **kwargs):
        user = self.request.user
        qs = Profile.objects.get(user=user)
        serializer = ProfileSerializer(data=request.data, instance=qs)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, **kwargs):
        user = self.request.user
        qs = Profile.objects.get(user=user)
        serializer = ProfileSerializer(data=request.data, instance=qs)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Profile.objects.all()
    lookup_field = 'pk'
    serializer_class = ProfileSerializer
    permission_classes = [IsOwnerOrReadOnlyAccount]


class SendEmailAPIView(generics.GenericAPIView):
    serializer_class = SendEmailResetSerializer

    def post(self, request):
        email = request.data["email"]
        user = User.objects.filter(email=email)
        if user.exists() and user[0].is_active:
            url = f"reset_password/"
            subject = 'Request Password Reset'
            from_email = settings.FROM_EMAIL
            template_name = "email/password_reset.html"
            recipient_list = [email]
            message = render_to_string(template_name, 
                                       {"url": url, "site_name": settings.SITE_NAME, 
                                        "protocol": settings.PROTOCOL,
                                        "domain": settings.DOMAIN                                        
                                        })
            email = EmailMessage(subject, message, from_email, recipient_list)
            email.content_subtype = 'html'
            email.send()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response("This email is not valid", status=status.HTTP_400_BAD_REQUEST)
        

class UserListAPIView(generics.ListAPIView):
    serializer_class = serializers.UserListSerializer
    queryset = Profile.objects.all()
    permission_classes = [IsAdminAndStaffOrReadOnly,permission.IsAdminUser]
    pagination_class = None


class LinkAPIView(APIView):
    '''
        Create, List, Update, Retrieve, Destroy
    '''
    permission_classes = [permission.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        profile_id = kwargs["profile_id"]
        qs = Profile.objects.filter(profile_id=profile_id)
        if qs.exists():
            qs = qs.first().links.all()
            serialize = serializers.LinkSerializer(instance=qs)
            return Response(serialize.data, status=status.HTTP_200_OK)

        return Response(serialize.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def post(self, request, *args, **kwargs):
        user = request.user
        profile_id = kwargs["profile_id"]
        qs = Profile.objects.filter(profile_id=profile_id)
        if qs.exists():
            serialize = serializers.LinkSerializer(data=request.data)
            if serialize.is_valid():
                link = serialize.validated_data.get("link")
                name = serialize.validated_data.get("name")
                serialize.save(user=request.user)
                if user.is_authenticated:
                    link_create = Link.objects.create(user_id=request.user.id,name=name,link=link)
                    qs = qs.first()
                    qs = qs.links.add(link_create)
                    return Response(serialize.data, status=status.HTTP_201_CREATED)
            
            return Response(serialize.errors, status=status.HTTP_400_BAD_REQUEST)
                
        else:
            return Response("User does not exist",status=status.HTTP_404_NOT_FOUND)


class LinkRetrieveUpdateDestroyAPIView(APIView):
    def get(self, request, *args, **kwargs):
        profile_id = kwargs["profile_id"]
        id = kwargs["link_id"]
        qs = Profile.objects.filter(profile_id=profile_id)
        if qs.exists():
            qs = qs.first().links.filter(link_id=id)
            if qs.exists():

                serialize = serializers.LinkSerializer(instance=qs.first())
                return Response(serialize.data, status=status.HTTP_200_OK)

            return Response()
        
        return Response(serialize.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        profile_id = kwargs["profile_id"]
        id = kwargs["link_id"]
        qs = Profile.objects.filter(profile_id=profile_id)
        if qs.exists():
            link = Link.objects.filter(link_id=id)
            if link.exists():
                link.delete()
                return Response("Successfully deleted", status=status.HTTP_200_OK)

            return Response("Link does not exist",status=status.HTTP_404_NOT_FOUND)
        
        return Response("User does not exist",status=status.HTTP_404_NOT_FOUND)

    def put(self, request, *args, **kwargs):
        profile_id = kwargs["profile_id"]
        id = kwargs["link_id"]
        qs = Profile.objects.filter(profile_id=profile_id)
        if qs.exists():
            qs = qs.first().links.filter(link_id=id)
            if qs.exists():
                serialize = serializers.LinkSerializer(instance=qs.first(), data=request.data)
                if serialize.is_valid():
                    serialize.save(user=request.user)
                    return Response(serialize.data, status=status.HTTP_200_OK)

                return Response(serialize.errors, status=status.HTTP_400_BAD_REQUEST)

            return Response("Link does not exist", status=status.HTTP_404_NOT_FOUND)

        return Response("Object does not exist", status=status.HTTP_404_NOT_FOUND)


class SkillAPIView(mixins.ListModelMixin,generics.GenericAPIView):
    queryset = Profile.objects.all()
    serializer_class = serializers.SkillSerializer
    permission_classes = [permission.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        profile_id = kwargs["profile_id"]

        qs = Profile.objects.filter(profile_id=profile_id)
        if qs.exists():
            qs = qs.first().skills.all()
            serialize = serializers.SkillSerializer(instance=qs, many=True)
            return Response(serialize.data, status=status.HTTP_200_OK)
        return Response("Profile does not exist", status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, *args, **kwargs):
        user = request.user
        profile_id = kwargs["profile_id"]
        qs = Profile.objects.filter(profile_id=profile_id)
        if qs.exists():
            serialize = self.get_serializer(data=request.data)
            if serialize.is_valid():
                if user.is_authenticated:
                    skill_create = serialize.save(user=request.user)
                    qs = qs[0].skills.add(skill_create)
                    return Response(serialize.data, status=status.HTTP_201_CREATED)
            
            return Response(serialize.errors, status=status.HTTP_400_BAD_REQUEST)
                
        else:
            return Response("User does not exist",status=status.HTTP_404_NOT_FOUND)


class SkillRetrieveUpdateDestroyAPIView(APIView):
    def get(self, request, *args, **kwargs):
        profile_id = kwargs["profile_id"]
        id = kwargs["skill_id"]
        qs = Profile.objects.filter(profile_id=profile_id)
        if qs.exists():
            qs = qs.first().skills.filter(skill_id=id)
            if qs.exists():

                serialize = serializers.SkillSerializer(instance=qs.first())
                return Response(serialize.data, status=status.HTTP_200_OK)

            return Response()

        return Response(serialize.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        profile_id = kwargs["profile_id"]
        id = kwargs["skill_id"]
        qs = Profile.objects.filter(profile_id=profile_id)
        if qs.exists():
            skill = Skills.objects.filter(skill_id=id)
            if skill.exists():
                skill.delete()
                return Response("Successfully deleted", status=status.HTTP_200_OK)

            return Response("skill does not exist",status=status.HTTP_404_NOT_FOUND)
        
        return Response("User does not exist",status=status.HTTP_404_NOT_FOUND)

    def put(self, request, *args, **kwargs):
        profile_id = kwargs["profile_id"]
        id = kwargs["skill_id"]
        qs = Profile.objects.filter(profile_id=profile_id)
        if qs.exists():
            qs = qs.first().skills.filter(skill_id=id)
            if qs.exists():
                serialize = serializers.SkillSerializer(instance=qs.first(), data=request.data)
                if serialize.is_valid():
                    serialize.save(user=request.user)
                    return Response(serialize.data, status=status.HTTP_200_OK)

                return Response(serialize.errors, status=status.HTTP_400_BAD_REQUEST)

            return Response("skill does not exist", status=status.HTTP_404_NOT_FOUND)

        return Response("Object does not exist", status=status.HTTP_404_NOT_FOUND)

