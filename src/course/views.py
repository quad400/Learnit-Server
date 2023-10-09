from datetime import timedelta
from django.utils import timezone
import json
from rest_framework.views import APIView
from rest_framework import (
                permissions,authentication,filters,
                generics,status,mixins,pagination
                )
from rest_framework.settings import api_settings
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.dispatch import Signal

from .models import (
                    Course,Category,FAQ,Reviews,
                    Syllabus,Topic,Instructor,Skills,
                    Question,Answer,Reply,Discussion,Quiz,Requirement,
                    Settings
                    )
from core.permissions import IsAdminAndStaffOrReadOnly,IsOwner
from .serializer import (
                CourseSerializer,CategorySerializer,SyllabusSerializer,TopicSerializer,
                InstructorRequestSerializer, InstructorRequestResponseSerializer,
                FAQSerializer,SkillSerializer,ReviewSerializer,DiscussionSerializer,
                QuestionSerializer, AnswerSerializer, ReplySerializer,QuizSerializer,
                RequirementSerializer,CourseProfileSerializer, SearchSerializer,SettingsSerializer
                )
from core.utils import get_email
from .email import InstructorRequestEmail
from account.models import Profile
from account.serializers import ProfileSerializer
from .search import perform_search

User = get_user_model()
signal = Signal()


class CourseUserCreateListAPIView(
                            mixins.ListModelMixin, 
                            generics.GenericAPIView):

    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    pagination_class = None

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request,*args,**kwargs):
        return self.list(request, *args, **kwargs)    


class CourseUserRetrieveUpdateDeleteAPIView(APIView):

    permission_classes = [IsOwner]

    def patch(self, request, *args, **kwargs):
        course_id = kwargs["course_id"]
        qs = Course.objects.filter(course_id=course_id)
        if qs.exists():
            serialize = CourseSerializer(instance=qs.first(), data=request.data)
            if serialize.is_valid():
                serialize.save(user=request.user)

                return Response(serialize.data, status=status.HTTP_200_OK)
            
            return Response(serialize.errors, status=status.HTTP_400_BAD_REQUEST)
        
        return Response("Course does not exist", status=status.HTTP_404_NOT_FOUND)

    def get(self, request, *args, **kwargs):
        course_id = kwargs["course_id"]
        qs = Course.objects.filter(course_id=course_id)
        if qs.exists():
            serialize = CourseSerializer(instance=qs.first())

            return Response(serialize.data, status=status.HTTP_200_OK)

        return Response("Course does not exist", status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, *args, **kwargs):
        course_id = kwargs["course_id"]
        qs = Course.objects.filter(course_id=course_id)
        if qs.exists():
            qs.delete()

            return Response("Course successfully deleted", status=status.HTTP_200_OK)
        return Response("Course does not exist", status=status.HTTP_404_NOT_FOUND)

class CourseFilterByUser(APIView):
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def get(self, request, *args, **kwargs):
        user_id = kwargs["user_id"]
        courses = Course.objects.filter(user__user_id=user_id)
        serialize = CourseSerializer(courses, many=True).data
        return Response(serialize, status=status.HTTP_200_OK)


class CourseListAPIView(generics.ListAPIView):
    serializer_class = CourseSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Course.objects.all()
    pagination_class = None

class CourseDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CourseSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'pk'
    queryset = Course.objects.all()

class CategoryListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    pagination_class = None
    permission_classes = [IsAdminAndStaffOrReadOnly]

class CategoryRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    permission_classes = [permissions.AllowAny]
    lookup_field = "pk"


class SyllabusListCreateAPIView(
                    mixins.ListModelMixin,
                    generics.GenericAPIView):
    
    serializer_class = SyllabusSerializer
    queryset = Syllabus.objects.all()
    permission_classes = [IsOwner]
    pagination_class = None

    def get_success_headers(self, data):
        try:
            return {'Location': str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            return {}

    def post(self, request, *args, **kwargs):
        course_id = kwargs["course_id"]
        
        course = Course.objects.filter(course_id=course_id)
        course_single = course[0]
        if course.exists():
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                cre = serializer.save(course_syllabus=course_single,user=request.user)
                course.first().syllabus.add(cre)
                headers = self.get_success_headers(serializer.data)
                return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
            return Response(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response("Course does not exist", status=status.HTTP_404_NOT_FOUND)

    def get(self, request, *args, **kwargs):
        course_id = kwargs["course_id"]
        
        qs = Course.objects.filter(course_id=course_id)
        if qs.exists():
            return self.list(request, *args, **kwargs)    
        return Response('Course does not exist', status=status.HTTP_404_NOT_FOUND)

    
class SyllabusRetrieveUpdateDestroyAPIView(APIView):

    def get(self, request, *args, **kwargs):
        syllabus_id = kwargs["syllabus_id"]
        course_id = kwargs["course_id"]
        
        qs = Course.objects.filter(course_id=course_id)
        if qs.exists():
            syllabus_qs = Syllabus.objects.filter(syllabus_id=syllabus_id)
            if syllabus_qs.exists():
                serialize = SyllabusSerializer(instance=syllabus_qs[0])
                return Response(serialize.data, status=status.HTTP_200_OK)
            return Response('Syllabus does not exist', status=status.HTTP_404_NOT_FOUND)
        return Response('Course does not exist', status=status.HTTP_404_NOT_FOUND)

    def put(self, request, *args, **kwargs):
        syllabus_id = kwargs["syllabus_id"]
        course_id = kwargs["course_id"]
        
        qs = Course.objects.filter(course_id=course_id)
        if qs.exists():
            syllabus_qs = Syllabus.objects.filter(syllabus_id=syllabus_id)
            if syllabus_qs.exists():
                serialize = SyllabusSerializer(instance=syllabus_qs[0],data=request.data)
                if serialize.is_valid():
                    serialize.save()
                    return Response(serialize.data, status=status.HTTP_200_OK)
                return Response(serialize.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return Response('Syllabus does not exist', status=status.HTTP_404_NOT_FOUND)
        return Response('Course does not exist', status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, *args, **kwargs):
        syllabus_id = kwargs["syllabus_id"]
        course_id = kwargs["course_id"]
        
        qs = Course.objects.filter(course_id=course_id)
        if qs.exists():
            syllabus_qs = Syllabus.objects.filter(syllabus_id=syllabus_id)
            if syllabus_qs.exists():
                syllabus_qs.delete()

                return Response('Syllabus is successfully deleted', status=status.HTTP_200_OK)

            return Response('Syllabus does not exist', status=status.HTTP_404_NOT_FOUND)
        return Response('Course does not exist', status=status.HTTP_404_NOT_FOUND)


class TopicListCreateAPIView(
                    mixins.ListModelMixin,
                    generics.GenericAPIView):

    serializer_class = TopicSerializer
    queryset = Topic.objects.all()
    permission_classes = [IsOwner]
    pagination_class = None

    def post(self, request, *args, **kwargs):
        syllabus_id = kwargs["syllabus_id"]
        course_id = kwargs["course_id"]
        
        qs = Course.objects.filter(course_id=course_id)
        if qs.exists():
            syllabus_qs = Syllabus.objects.filter(syllabus_id=syllabus_id)
            if syllabus_qs.exists():
                topic_serialize = self.get_serializer(data=request.data)
                if topic_serialize.is_valid():
                    topic = topic_serialize.save(user=qs[0].user)
                    syllabus_qs.first().topics.add(topic)
                    return Response(topic_serialize.data, status=status.HTTP_201_CREATED)
                return Response(topic_serialize.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return Response("Syllabus does not exist", status=status.HTTP_404_NOT_FOUND)
        return Response("Course does not exist", status=status.HTTP_404_NOT_FOUND)

    def get(self, request, *args, **kwargs):
        syllabus_id = kwargs["syllabus_id"]
        course_id = kwargs["course_id"]
        
        qs = Course.objects.filter(course_id=course_id)
        if qs.exists():
            syllabus_qs = Syllabus.objects.filter(syllabus_id=syllabus_id)
            if syllabus_qs.exists():
                topic_serialize = TopicSerializer(instance=syllabus_qs.first().topics, many=True)
                return Response(topic_serialize.data, status=status.HTTP_200_OK)
            return Response("Syllabus does not exist", status=status.HTTP_404_NOT_FOUND)
        return Response("Course does not exist", status=status.HTTP_404_NOT_FOUND)


class TopicRetrieveUpdateDestroyAPIView(APIView):

    def get(self, request, *args, **kwargs):
        syllabus_id = kwargs["syllabus_id"]
        course_id = kwargs["course_id"]
        topic_id = kwargs["topic_id"]
        
        qs = Course.objects.filter(course_id=course_id)
        if qs.exists():
            syllabus_qs = Syllabus.objects.filter(syllabus_id=syllabus_id)
            if syllabus_qs.exists():
                topic_qs = Topic.objects.filter(topic_id=topic_id)
                if topic_qs.exists():
                    serialize = TopicSerializer(instance=topic_qs[0])
                    return Response(serialize.data, status=status.HTTP_200_OK)
                return Response('Topic does not exist', status=status.HTTP_404_NOT_FOUND)
            return Response('Syllabus does not exist', status=status.HTTP_404_NOT_FOUND)
        return Response('Course does not exist', status=status.HTTP_404_NOT_FOUND)

    def put(self, request, *args, **kwargs):
        syllabus_id = kwargs["syllabus_id"]
        course_id = kwargs["course_id"]
        topic_id = kwargs["topic_id"]
        
        qs = Course.objects.filter(course_id=course_id)
        if qs.exists():
            syllabus_qs = Syllabus.objects.filter(syllabus_id=syllabus_id)
            if syllabus_qs.exists():
                topic_qs = Topic.objects.filter(topic_id=topic_id)
                if topic_qs.exists():
                    serialize = TopicSerializer(instance=topic_qs[0],data=request.data)
                    if serialize.is_valid():
                        serialize.save()
                        return Response(serialize.data, status=status.HTTP_200_OK)
                    return Response(serialize.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                return Response('Topic does not exist', status=status.HTTP_404_NOT_FOUND)
            return Response('Syllabus does not exist', status=status.HTTP_404_NOT_FOUND)
        return Response('Course does not exist', status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, *args, **kwargs):
        syllabus_id = kwargs["syllabus_id"]
        course_id = kwargs["course_id"]
        topic_id = kwargs["topic_id"]
        
        qs = Course.objects.filter(course_id=course_id)
        if qs.exists():
            syllabus_qs = Syllabus.objects.filter(syllabus_id=syllabus_id)
            if syllabus_qs.exists():
                topic_qs = Topic.objects.filter(topic_id=topic_id)
                if topic_qs.exists():
                    topic_qs.delete()
                    return Response('Syllabus is successfully deleted', status=status.HTTP_200_OK)
                return Response('Topic does not exist', status=status.HTTP_404_NOT_FOUND)
            return Response('Syllabus does not exist', status=status.HTTP_404_NOT_FOUND)
        return Response('Course does not exist', status=status.HTTP_404_NOT_FOUND)


class InstructorRequestAPIView(APIView):

    permission_classes = [IsOwner]

    def post(self, request, *args, **kwargs):
        course_id = kwargs["course_id"]
        course_qs = Course.objects.filter(course_id=course_id)
        qs = course_qs[0]
        if course_qs.exists():
            instructor_request_serialize = InstructorRequestSerializer(data=request.data)
            if instructor_request_serialize.is_valid():
                email = instructor_request_serialize.validated_data.get("email")
                user = User.objects.filter(email=email)
                if user.exists():
                    user = user.first()
                    if request.user.is_instructor:
                        signal.send(sender=user, user=user, request=request)
                        context = {"user": user, "title": qs.title, "course_id": course_id}
                        to = [get_email(user)]
                        InstructorRequestEmail(request, context=context).send(to)
                        return Response("Request Succefully sent", status=status.HTTP_200_OK)
                    return Response("User Account is not an instructor", status=status.HTTP_400_BAD_REQUEST)
                return Response("User Account does not exist", status=status.HTTP_400_BAD_REQUEST)
            return Response(instructor_request_serialize.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response("Course does not exist", status=status.HTTP_400_BAD_REQUEST)


class InstructorCreateAPIView(APIView):

    def post(self, request, *args, **kwargs):
        course_id = kwargs["course_id"]
        course_qs = Course.objects.filter(course_id=course_id)
        if course_qs.exists():
            reply_serialize = InstructorRequestResponseSerializer(data=request.data)
            if reply_serialize.is_valid():
                reply = reply_serialize.validated_data.get("reply")
                if reply == 'yes' or reply == 'Yes' or reply == 'YES':
                    if course_qs.first().instructors.filter(user=request.user).exists():
                        return Response("Instructor is already added", status=status.HTTP_403_FORBIDDEN)
                    else:
                        if course_qs[0].user == request.user:
                            instructor_create = Instructor.objects.create(user=request.user, isLead_instructor=True)
                        
                            course_qs.first().instructors.add(instructor_create)
                        else:
                            instructor_create = Instructor.objects.create(user=request.user)
                            course_qs.first().instructors.add(instructor_create)
                        return Response("accepted", status=status.HTTP_201_CREATED)
                elif reply == 'no':
                    return Response("rejected", status=status.HTTP_200_OK)
                else:
                    return Response(f"{reply} not a valid input", status=status.HTTP_200_OK)
            return Response(reply_serialize.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response('course does not exist', status=status.HTTP_404_NOT_FOUND)


class InstructorDestroyAPIView(APIView):
    permission_classes = [IsOwner]
    def delete(self, request, *args, **kwargs):
        course_id = kwargs["course_id"]
        instructor_id = kwargs["instructor_id"]
        course_qs = Course.objects.filter(course_id=course_id)
        if course_qs.exists():
            instructor_qs = course_qs.first().instructors.filter(instructor_id=instructor_id)
            if instructor_qs.exists():
                instructor_qs.delete()
                return Response('Instructor is successfully deleted', status=status.HTTP_200_OK)
            return Response('Instructor does not exist', status=status.HTTP_404_NOT_FOUND)
        return Response('Course does not exist', status=status.HTTP_404_NOT_FOUND)


class SkillListCreateAPIView(
                    mixins.ListModelMixin,
                    generics.GenericAPIView):
    serializer_class = SkillSerializer
    queryset = Skills.objects.all()
    # permission_classes = [IsOwner]

    def get_success_headers(self, data):
        try:
            return {'Location': str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            return {}

    def get(self, request, *args, **kwargs):
        course_id = kwargs["course_id"]

        qs = Course.objects.filter(course_id=course_id)
        if qs.exists():
            return self.list(request, *args, **kwargs)    
        return Response('Course does not exist', status=status.HTTP_404_NOT_FOUND)

    def post(self, request, *args, **kwargs):
        course_id = kwargs["course_id"]
        qs = Course.objects.filter(course_id=course_id)
        if qs.exists():
        
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                cre = serializer.save(skill_course=qs[0])
                qs.first().skills.add(cre)
                headers = self.get_success_headers(serializer.data)
                return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response("Course does not exist",status=status.HTTP_404_NOT_FOUND)


class SkillRetrieveDestroyAPIView(APIView):
    def get(self, request, *args, **kwargs):
        course_id = kwargs["course_id"]
        id = kwargs["skill_id"]
        qs = Course.objects.filter(course_id=course_id)
        if qs.exists():
            qs = qs.first().skills.filter(skill_id=id)
            if qs.exists():

                serialize = SkillSerializer(instance=qs.first())
                return Response(serialize.data, status=status.HTTP_200_OK)
            return Response("skill does not exist",status=status.HTTP_404_NOT_FOUND)
        
        return Response("Course does not exist",status=status.HTTP_404_NOT_FOUND)


    def delete(self, request, *args, **kwargs):
        course_id = kwargs["course_id"]
        id = kwargs["skill_id"]
        qs = Course.objects.filter(course_id=course_id)
        if qs.exists():
            skill = Skills.objects.filter(skill_id=id)
            if skill.exists():
                skill.delete()
                return Response("Successfully deleted", status=status.HTTP_200_OK)

            return Response("skill does not exist",status=status.HTTP_404_NOT_FOUND)
        
        return Response("Course does not exist",status=status.HTTP_404_NOT_FOUND)

class RequirementListCreateAPIView(
                    mixins.ListModelMixin,
                    generics.GenericAPIView):
    serializer_class = RequirementSerializer
    queryset = Requirement.objects.all()
    # permission_classes = [IsOwner]

    def get_success_headers(self, data):
        try:
            return {'Location': str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            return {}

    def get(self, request, *args, **kwargs):
        course_id = kwargs["course_id"]

        qs = Course.objects.filter(course_id=course_id)
        if qs.exists():
            return self.list(request, *args, **kwargs)    
        return Response('Course does not exist', status=status.HTTP_404_NOT_FOUND)

    def post(self, request, *args, **kwargs):
        course_id = kwargs["course_id"]
        qs = Course.objects.filter(course_id=course_id)
        if qs.exists():
        
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                cre = serializer.save(require_course=qs[0])
                qs.first().requirement.add(cre)
                headers = self.get_success_headers(serializer.data)
                return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response("Course does not exist",status=status.HTTP_404_NOT_FOUND)


class RequirementRetrieveDestroyAPIView(APIView):
    def get(self, request, *args, **kwargs):
        course_id = kwargs["course_id"]
        id = kwargs["requirement_id"]
        qs = Course.objects.filter(course_id=course_id)
        if qs.exists():
            qs = qs.first().requirement.filter(requirement_id=id)
            if qs.exists():

                serialize = RequirementSerializer(instance=qs.first())
                return Response(serialize.data, status=status.HTTP_200_OK)
            return Response("skill does not exist",status=status.HTTP_404_NOT_FOUND)
        
        return Response("Course does not exist",status=status.HTTP_404_NOT_FOUND)


    def delete(self, request, *args, **kwargs):
        course_id = kwargs["course_id"]
        id = kwargs["requirement_id"]
        qs = Course.objects.filter(course_id=course_id)
        if qs.exists():
            require = Requirement.objects.filter(requirement_id=id)
            if require.exists():
                require.delete()
                return Response("Successfully deleted", status=status.HTTP_200_OK)

            return Response("Requirement does not exist",status=status.HTTP_404_NOT_FOUND)
        
        return Response("Course does not exist",status=status.HTTP_404_NOT_FOUND)

class FAQListCreateAPIView(APIView):
    permission_classes = []

    def get(self, request, *args, **kwargs):
        course_id = kwargs["course_id"]

        qs = Course.objects.filter(course_id=course_id)
        if qs.exists():
            qs = qs.first().faqs.all()
            serialize = FAQSerializer(instance=qs, many=True)
            return Response(serialize.data, status=status.HTTP_200_OK)

        return Response('Course does not exist', status=status.HTTP_404_NOT_FOUND)

    def post(self, request, *args, **kwargs):
        course_id = kwargs["course_id"]
        qs = Course.objects.filter(course_id=course_id)
        if qs.exists():
            serialize = FAQSerializer(data=request.data)
            if serialize.is_valid():
                question = serialize.validated_data.get("question")
                answer = serialize.validated_data.get("answer")
                serialize.save(faq_course=qs[0])
                faq_create = FAQ.objects.create(faq_course=qs[0],question=question,answer=answer)
                qs = qs.first()
                qs = qs.faqs.add(faq_create)
                return Response(serialize.data, status=status.HTTP_201_CREATED)
            
            return Response(serialize.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response("Course does not exist",status=status.HTTP_404_NOT_FOUND)


class FAQRetrieveUpdateDestroyAPIView(APIView):
    def get(self, request, *args, **kwargs):
        course_id = kwargs["course_id"]
        id = kwargs["faq_id"]
        qs = Course.objects.filter(course_id=course_id)
        if qs.exists():
            qs = qs.first().faqs.filter(faq_id=id)
            if qs.exists():

                serialize = FAQSerializer(instance=qs.first())
                return Response(serialize.data, status=status.HTTP_200_OK)
            return Response("Faq does not exist",status=status.HTTP_404_NOT_FOUND)
        
        return Response("Course does not exist",status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, *args, **kwargs):
        course_id = kwargs["course_id"]
        id = kwargs["faq_id"]
        qs = Course.objects.filter(course_id=course_id)
        if qs.exists():
            faq = FAQ.objects.filter(faq_id=id)
            if faq.exists():
                faq.delete()
                return Response("Successfully deleted", status=status.HTTP_200_OK)

            return Response("faq does not exist",status=status.HTTP_404_NOT_FOUND)
        
        return Response("Course does not exist",status=status.HTTP_404_NOT_FOUND)

    def put(self, request, *args, **kwargs):
        course_id = kwargs["course_id"]
        id = kwargs["faq_id"]
        qs = Course.objects.filter(course_id=course_id)
        if qs.exists():
            faq_qs = qs.first().faqs.filter(faq_id=id)
            if faq_qs.exists():
                serialize = FAQSerializer(instance=faq_qs.first(), data=request.data)
                if serialize.is_valid():
                    serialize.save(faq_course=qs[0])
                    return Response(serialize.data, status=status.HTTP_200_OK)

                return Response(serialize.errors, status=status.HTTP_400_BAD_REQUEST)

            return Response("Faq does not exist", status=status.HTTP_404_NOT_FOUND)

        return Response("Course does not exist", status=status.HTTP_404_NOT_FOUND)

class ReviewListCreateAPIView(
                    mixins.ListModelMixin,
                    generics.GenericAPIView):

    serializer_class = ReviewSerializer
    queryset = Reviews.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_success_headers(self, data):
        try:
            return {'Location': str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            return {}

    def post(self, request, *args, **kwargs):
        course_id = kwargs["course_id"]
        qs = Course.objects.filter(course_id=course_id)
        serialize = ReviewSerializer(data=request.data)
        if qs.exists():
            if qs[0].user != request.user:
                serializer = self.get_serializer(data=request.data)
                if serialize.is_valid():
                    if serializer.is_valid():
                        cre = serializer.save(review_course=qs[0],user=request.user)
                        qs.first().reviews.add(cre)
                        headers = self.get_success_headers(serializer.data)
                        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
                    return Response(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return Response('Course owner cannot give a review', status=status.HTTP_403_FORBIDDEN)
        return Response("Course does not exist", status=status.HTTP_404_NOT_FOUND)

    def get(self, request, *args, **kwargs):
        course_id = kwargs["course_id"]
        qs = Course.objects.filter(course_id=course_id)
        if qs.exists():
            qs_review = qs.first().reviews
            serialize = ReviewSerializer(instance=qs_review, many=True)
            return Response(serialize.data, status=status.HTTP_200_OK)
        return Response("Course does not exist", status=status.HTTP_404_NOT_FOUND)


class DiscussionCreateAPIView(
                    mixins.ListModelMixin,
                    generics.GenericAPIView):

    serializer_class = DiscussionSerializer
    queryset = Discussion.objects.all()
    permission_classes = []

    def get_success_headers(self, data):
        try:
            return {'Location': str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            return {}

    def post(self, request, *args, **kwargs):
        course_id = kwargs["course_id"]
        qs = Course.objects.filter(course_id=course_id)
        if qs.exists():
            serialize = DiscussionSerializer(data=request.data)
            if serialize.is_valid():
                serialize.save(course_discuss=qs[0])
                return Response(serialize.data, status=status.HTTP_201_CREATED)
            return Response(serialize.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response("Course does not exist", status=status.HTTP_404_NOT_FOUND)
    
    def get(self, request, *args, **kwargs):
        course_id = kwargs["course_id"]
        qs = Course.objects.filter(course_id=course_id)
        if qs.exists():
            discuss = Discussion.objects.all()
            serialize = DiscussionSerializer(instance=discuss, many=True)
            return Response(serialize.data, status=status.HTTP_200_OK)
        return Response("Course does not exist", status=status.HTTP_404_NOT_FOUND)


class QuestionCreateListAPIView(APIView):

    def post(self, request, *args, **kwargs):
        discussion_id = kwargs["discussion_id"]
        qs = Discussion.objects.filter(discussion_id=discussion_id)
        if qs.exists():
            if request.user.is_authenticated:
                serialize = QuestionSerializer(data=request.data)
                if serialize.is_valid():
                    question = serialize.validated_data.get('question')
                    quest = Question.objects.create(user=request.user, discuss=qs[0],question=question)
                    qs[0].questions.add(quest)
                    # quest.delete()
                    serialize.save(discuss=qs[0],user=request.user,commit=False)
                    return Response(serialize.data, status=status.HTTP_201_CREATED)
                return Response(serialize.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return Response("User must be authenticated", status=status.HTTP_401_UNAUTHORIZED)
        return Response("Discussion not created or does not exist", status=status.HTTP_404_NOT_FOUND)

    def get(self, request,**kwargs):
        discussion_id = kwargs["discussion_id"]
        qs = Discussion.objects.filter(discussion_id=discussion_id)

        if qs.exists():
            serialize = QuestionSerializer(instance=qs[0].questions, many=True)
            return Response(serialize.data, status=status.HTTP_200_OK)
        return Response("Discussion not created or does not exist", status=status.HTTP_404_NOT_FOUND)


class QuestionRetrieveUpdateDestroy(APIView):
    def get(self, request,**kwargs):
        question_id = kwargs["question_id"]
        qs = Question.objects.filter(question_id=question_id)

        if qs.exists():
            serialize = QuestionSerializer(instance=qs[0])
            return Response(serialize.data, status=status.HTTP_200_OK)
        return Response("Discussion not created or does not exist", status=status.HTTP_404_NOT_FOUND)

    def put(self, request, **kwargs):
        question_id = kwargs["question_id"]
        qs = Question.objects.filter(question_id=question_id)

        if qs.exists():
            serialize = QuestionSerializer(instance=qs[0], data=request.data)
            if serialize.is_valid():
                serialize.save(user=request.user)
                return Response(serialize.data, status=status.HTTP_200_OK)
            return Response(serialize.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response("Question not created or does not exist", status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, **kwargs):
        question_id = kwargs["question_id"]
        qs = Question.objects.filter(question_id=question_id)

        if qs.exists():
            qs.delete()
            return Response("Question is successfully deleted", status=status.HTTP_200_OK)
        return Response("Question does not exist", status=status.HTTP_404_NOT_FOUND)


class QuestionUserListAPIView(APIView):

    def get(self, request,**kwargs):
        if request.user.is_authenticated:
            qs = Question.objects.filter(user=request.user)
            if qs.exists():
                serialize = QuestionSerializer(instance=qs, many=True)
                return Response(serialize.data, status=status.HTTP_200_OK)
            return Response("User have no question", status=status.HTTP_404_NOT_FOUND)
        return Response("User must be logged in", status=status.HTTP_401_UNAUTHORIZED)


class AnswerCreateListAPIView(APIView):
    
    def post(self, request, **kwargs):
        question_id = kwargs["question_id"]
        qs = Question.objects.filter(question_id=question_id)

        if qs.exists():
            serialize = AnswerSerializer(data=request.data)
            if serialize.is_valid():
                content = serialize.validated_data.get('content')
                ans = Answer.objects.create(user=request.user,question_answer=qs[0],content=content)
                serialize.save(user=request.user,question_answer=qs[0])
                qs[0].answers.add(ans)
                return Response(serialize.data, status=status.HTTP_201_CREATED)
            return Response(serialize.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response("Question does not exist", status=status.HTTP_404_NOT_FOUND)

    def get(self, request, **kwargs):
        question_id = kwargs["question_id"]
        qs = Question.objects.filter(question_id=question_id)

        if qs.exists():
            serialize = AnswerSerializer(instance=qs[0].answers, many=True)
            return Response(serialize.data, status=status.HTTP_200_OK)
        return Response("Question does not exist", status=status.HTTP_404_NOT_FOUND)


class AnswerRetrieveUpdateDestroyAPIView(APIView):

    def get(self, request, **kwargs):

        answer_id = kwargs["answer_id"]
        qs = Answer.objects.filter(answer_id=answer_id)

        if qs.exists():
            serialize = AnswerSerializer(instance=qs[0])

            return Response(serialize.data, status=status.HTTP_200_OK)
        return Response("Answer does not exist", status=status.HTTP_404_NOT_FOUND)

    def put(self, request, **kwargs):
        answer_id = kwargs["answer_id"]
        qs = Answer.objects.filter(answer_id=answer_id)

        if qs.exists():
            serialize = AnswerSerializer(instance=qs[0], data=request.data)
            if serialize.is_valid():
                serialize.save(user=request.user)
                return Response(serialize.data, status=status.HTTP_200_OK)
            return Response(serialize.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response("Answer does not exist", status=status.HTTP_404_NOT_FOUND)

    def delete(self,request,**kwargs):
        answer_id = kwargs["answer_id"]
        qs = Answer.objects.filter(answer_id=answer_id)

        if qs.exists():
            qs.delete()

            return Response("Answer successfully deleted", status=status.HTTP_200_OK)
        return Response("Answer does not exist", status=status.HTTP_404_NOT_FOUND)


class ReplyCreateListAPIView(APIView):
    def post(self, request, **kwargs):
        answer_id = kwargs["answer_id"]
        qs = Answer.objects.filter(answer_id=answer_id)
        serialize = ReplySerializer(data=request.data)
        if qs.exists():
            if serialize.is_valid():
                content = serialize.validated_data.get('content')
                reply = Reply.objects.create(user=request.user,answer_reply=qs[0],content=content)
                qs[0].reply.add(reply)
                serialize.save(user=request.user,answer_reply=qs[0])
                return Response(serialize.data, status=status.HTTP_201_CREATED)
            return Response(serialize.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response("Answer does not exist", status=status.HTTP_404_NOT_FOUND)

    def get(self, request, **kwargs):
        answer_id = kwargs["answer_id"]
        qs = Answer.objects.filter(answer_id=answer_id)
        if qs.exists():
            reply = qs[0].reply
            serialize = ReplySerializer(instance=reply, many=True)
            return Response(serialize.data, status=status.HTTP_200_OK)
        return Response("Answer does not exist", status=status.HTTP_404_NOT_FOUND)


class ReplyRetrieveAPIView(APIView):

    def get(self, request, **kwargs):
        reply_id = kwargs["reply_id"]
        qs = Reply.objects.filter(reply_id=reply_id)
        if qs.exists():
            serialize = ReplySerializer(instance=qs[0])
            return Response(serialize.data, status=status.HTTP_200_OK)
        return Response("Answer does not exist", status=status.HTTP_404_NOT_FOUND)


class LikeUnlikeAnswerCreateAPIView(APIView):

    def post(self, request, **kwargs):
        answer_id = kwargs["answer_id"]
        user = request.user

        qs = Answer.objects.filter(answer_id=answer_id)
        obj = qs.first()
        if qs.exists():
            if not user in obj.like_answer.all():
                obj.like_answer.add(user)
                return Response(f"{request.user} successfully like this Answer", status=status.HTTP_200_OK)
            obj.like_answer.remove(user)
            return Response(f"{request.user} successfully unlike this Answer", status=status.HTTP_200_OK)
        return Response("Answer does not exist", status=status.HTTP_404_NOT_FOUND)

class LikeUnlikeReplyCreateAPIView(APIView):

    def post(self, request, **kwargs):
        reply_id = kwargs["reply_id"]
        user = request.user

        qs = Reply.objects.filter(reply_id=reply_id)
        obj = qs.first()
        if qs.exists():
            if not user in obj.like_reply.all():
                obj.like_reply.add(user)
                return Response(f"{request.user} successfully like this Reply", status=status.HTTP_200_OK)
            obj.like_reply.remove(user)
            return Response(f"{request.user} successfully unlike this Reply", status=status.HTTP_200_OK)
        return Response("Reply does not exist", status=status.HTTP_404_NOT_FOUND)


class CourseEnrollAPIView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, **kwargs):
        course_id = kwargs["course_id"]
        user = request.user

        qs = Course.objects.filter(course_id=course_id)
        obj = qs.first()
        if qs.exists():
            if not user in obj.enrolled.all():
                obj.enrolled.add(user)
                return Response(f"{request.user} successfully enroll on {obj.title}", status=status.HTTP_200_OK)
            return Response("User is already enrolled on this course", status=status.HTTP_200_OK)
        return Response("Course does not exist", status=status.HTTP_404_NOT_FOUND)


class QuizUploadAPIView(APIView):

    def post(self, request, **kwargs):
        syllabus_id = kwargs["syllabus_id"]
        qs = Syllabus.objects.filter(syllabus_id=syllabus_id)
        if qs.exists():
            serialize = QuizSerializer(data=request.data)
            if serialize.is_valid():
                quiz = Quiz.objects.create(**serialize.validated_data)
                
                qs[0].syllabus_quiz.add(quiz)
                serialize.save()
                return Response(serialize.data, status=status.HTTP_201_CREATED)

            return Response(serialize.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response("Syllabus does not exist", status=status.HTTP_404_NOT_FOUND)

    def get(self, request, **kwargs):
        syllabus_id = kwargs["syllabus_id"]
        qs = Syllabus.objects.filter(syllabus_id=syllabus_id)
        if qs.exists():
            quiz = qs[0].syllabus_quiz
            serialize = QuizSerializer(instance=quiz, many=True)
            return Response(serialize.data, status=status.HTTP_201_CREATED)
        return Response("Syllabus does not exist", status=status.HTTP_404_NOT_FOUND)


class FilterByCategoryAPIView(generics.ListAPIView):
    serializer_class = CourseSerializer
    queryset = Course.objects.all()


    def get(self, request, *args, **kwargs):
        category_id = kwargs['category_id']

        category = Category.objects.get(category_id=category_id)
        course = Course.objects.filter(category__category_id=category_id)

        data = {
        "category_name": category.name,
        "total_category": course.count(),
        }
        return Response(data, status=status.HTTP_200_OK)



class FilterByCategoryWithFiterTypeAPIView(generics.ListAPIView):
    serializer_class = CourseSerializer
    queryset = Course.objects.all()
    pagination_class = pagination.PageNumberPagination


    def list(self, request, *args, **kwargs):
        category_id = kwargs['category_id']
        filter_type = kwargs["sort_by"]
        
        valid_filters = ['most_popular', 'latest', 'trending']

        if filter_type in valid_filters:
            if filter_type == 'most_popular':
                queryset = Course.objects.filter(category__category_id=category_id).order_by('-enrolled_counter')
            elif filter_type == 'latest':
                queryset = Course.objects.filter(category__category_id=category_id).order_by('-created')
            elif filter_type == 'trending':
                trending_duration = timedelta(days=7)  # Trending duration of 7 days
                end_date = timezone.now()
                start_date = end_date - trending_duration
                # Filter products based on sales, views, or any other relevant metric
                queryset = Course.objects.filter(category__category_id=category_id).filter(created__range=(start_date, end_date)).order_by("-enrolled")
        elif filter_type is not None:
            return Response('Invalid filter parameter.',
                status=status.HTTP_400_BAD_REQUEST
            )
        else:
            queryset = Course.objects.filter(category__category_id=category_id)
            
        serialize = CourseSerializer(instance=queryset, many=True).data

        return self.get_paginated_response(self.paginate_queryset(serialize))


class InstructorDetail(APIView):

    def get(self, request, **kwargs):
        user_id = kwargs["user_id"]
        courses = Course.objects.filter(user__user_id=user_id)
        profile = Profile.objects.get(user__user_id=user_id)
        if courses.exists():
            total_rate_count = 0
            total_average_rate = 0
            total_enrolled_student = 0
            serializer = CourseSerializer(instance=courses, many=True)
            profile_serializer = ProfileSerializer(instance=profile)
            for course in  courses:
                total_rate_count += course.count_rate()
                try:

                    total_average_rate += course.average_rate() / total_rate_count
                
                except ZeroDivisionError:
                    total_average_rate = 0
                total_enrolled_student += course.enrolled_count()
            data = {
                    "profile": profile_serializer.data,
                    "total_rate_count": total_rate_count,
                    "total_average_rate": round(total_average_rate,1),
                    "total_enrolled_student": total_enrolled_student,
                    "total_course": courses.count(),
                    "courses": serializer.data
                    }
            proj = json.loads(json.dumps(data))
            return Response(proj)
        


class ProfileDetail(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, **kwargs):
        try:
            courses = Course.objects.filter(user__user_id=request.user.user_id)
            profile = Profile.objects.get(user__user_id=request.user.user_id)
            if courses.exists():
                total_rate_count = 0
                total_average_rate = 0
                total_enrolled_student = 0
                serializer = CourseProfileSerializer(instance=courses, many=True)
                profile_serializer = ProfileSerializer(instance=profile)
                for course in  courses:
                    total_rate_count += course.count_rate()
                    try:

                        total_average_rate += course.average_rate() / total_rate_count
                    
                    except ZeroDivisionError:
                        total_average_rate = 0
                    total_enrolled_student += course.enrolled_count()
                data = {
                        "profile": profile_serializer.data,
                        "total_rate_count": total_rate_count,
                        "total_average_rate": round(total_average_rate,1),
                        "total_enrolled_student": total_enrolled_student,
                        "total_course": courses.count(),
                        "courses": serializer.data
                        }
                return Response(data, status=status.HTTP_200_OK)
            else:
                return Response("User has no course", status=status.HTTP_404_NOT_FOUND)
                # print("data", data)
                # proj = json.loads(json.dumps(data))
                # print(proj)
                # return Response(proj)
        except:
            return Response("Not a valid user", status=status.HTTP_400_BAD_REQUEST)
        
    def put(self, request, **kwargs):
        user = request.user
        profile = get_object_or_404(Profile, user=user)
        serializer = ProfileSerializer(instance=profile, data=request.data)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class CourseSearchAPIView(generics.ListAPIView):
    serializer_class = CourseSerializer
    filter_backends = [filters.SearchFilter]
    pagination_class = None
    search_fields = ['title', 'description', 'category']  # Define searchable fields

    def get_queryset(self):
        queryset = Course.objects.all()
        search_query = self.request.query_params.get('q', None)
        if search_query is not None:
            queryset = queryset.filter(title__icontains=search_query)
        return queryset


class SearchListView(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '')
        if not query:
            return Response('Result not found', status=status.HTTP_400_BAD_REQUEST)
        results = perform_search(query)
        return Response(results)


class SettingsAPIView(generics.ListCreateAPIView):
    queryset = Settings.objects.all()
    serializer_class = SettingsSerializer
    pagination_class = None
    # permission_classes = IsAdminAndStaffOrReadOnly

class SettingsDetailDeleteAPIView(
                                generics.RetrieveDestroyAPIView,
                                generics.GenericAPIView):
    queryset = Settings.objects.all()
    serializer_class = SettingsSerializer
    lookup_field = 'pk'

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

class SettingsUpdateAPIView(mixins.UpdateModelMixin,generics.GenericAPIView):
    queryset = Settings.objects.all()
    serializer_class = SettingsSerializer
    lookup_field = 'pk'
