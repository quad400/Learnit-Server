from rest_framework.status import (
                    HTTP_200_OK,HTTP_201_CREATED,
                    HTTP_404_NOT_FOUND,HTTP_400_BAD_REQUEST,
                    HTTP_500_INTERNAL_SERVER_ERROR
                    )
from rest_framework.generics import GenericAPIView,ListCreateAPIView,RetrieveUpdateDestroyAPIView
from rest_framework.settings import api_settings
from rest_framework.response import Response
from rest_framework import mixins,status

from django.shortcuts import get_object_or_404

from course.models import Syllabus
from core.permissions import IsOwner,IsEnroll
from .models import Quiz,Question,Option,QuizAttempter,AttemtQuestion
from .serializers import (
                QuizSerializer,QuestionSerializer,
                OptionSerializer,QuizAttempterSerializer
                
                )

class OptionView(ListCreateAPIView):

    serializer_class = OptionSerializer
    queryset = Option.objects.all()
    # permission_classes = [IsOwner]

    def get_success_headers(self, data):
        try:
            return {'Location': str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            return {}

    def post(self, request, *args, **kwargs):
        question_id = kwargs["question_id"]
        
        quest = Question.objects.filter(question_id=question_id)
        if quest.exists():
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                opt = serializer.save(quest=quest[0])
                quest[0].opt.add(opt)
                headers = self.get_success_headers(serializer.data)
                return Response(serializer.data, status=HTTP_201_CREATED, headers=headers)
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

        return Response("Question does not exist", status=HTTP_404_NOT_FOUND)

class OptionDetailView(RetrieveUpdateDestroyAPIView):

    serializer_class = OptionSerializer
    queryset = Option.objects.all()
    lookup_field = "pk"

class QuestionView(ListCreateAPIView):

    serializer_class = QuestionSerializer
    queryset = Question.objects.all()
    # permission_classes = [IsOwner]

    def get_success_headers(self, data):
        try:
            return {'Location': str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            return {}

    def post(self, request, *args, **kwargs):
        quiz_id = kwargs["quiz_id"]
        
        quiz = Quiz.objects.filter(quiz_id=quiz_id)
        if quiz.exists():
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                qs = serializer.save(quiz=quiz[0])
                quiz[0].quizs.add(qs)
                headers = self.get_success_headers(serializer.data)
                return Response(serializer.data, status=HTTP_201_CREATED, headers=headers)
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

        return Response("Quiz does not exist", status=HTTP_404_NOT_FOUND)


class QuestionDetailView(RetrieveUpdateDestroyAPIView):

    serializer_class = QuestionSerializer
    queryset = Question.objects.all()
    lookup_field = "pk"

class QuizView(ListCreateAPIView):

    serializer_class = QuizSerializer
    queryset = Quiz.objects.all()
    permission_classes = [IsOwner]

    def get_success_headers(self, data):
        try:
            return {'Location': str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            return {}

    def post(self, request, *args, **kwargs):
        syllabus_id = kwargs["syllabus_id"]
        
        syllabus = Syllabus.objects.filter(syllabus_id=syllabus_id)
        if syllabus.exists():
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                cre = serializer.save(user=request.user)
                syllabus.first().syllabus_quiz.add(cre)
                headers = self.get_success_headers(serializer.data)
                return Response(serializer.data, status=HTTP_201_CREATED, headers=headers)
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

        return Response("Course does not exist", status=HTTP_404_NOT_FOUND)

    def get(self, request, *args, **kwargs):
        syllabus_id = kwargs["syllabus_id"]
        
        qs = Syllabus.objects.filter(syllabus_id=syllabus_id)
        if qs.exists():
            return self.list(request, *args, **kwargs)    
        return Response('Syllabus does not exist', status=HTTP_404_NOT_FOUND)


class QuizDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = QuizSerializer
    queryset = Quiz.objects.all()
    permission_classes = [IsOwner]
    lookup_field = "pk"


class QuizAttempterView(mixins.ListModelMixin,GenericAPIView):
    serializer_class = QuizAttempterSerializer
    queryset = QuizAttempter.objects.all()

    def post(self, request, *args, **kwargs):
        quiz_id = kwargs["quiz_id"]
        quiz = get_object_or_404(Quiz, quiz_id=quiz_id)
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            quizattempt = QuizAttempter.objects.filter(user_attempt=request.user)
            if quizattempt.exists():
                return Response("User can only attempt this quiz ones")
            else:
                serializer.save(user_attempt=request.user, quizz=quiz)
                return Response(serializer.data, status=HTTP_201_CREATED)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        quiz_id = kwargs["quiz_id"]
        get_object_or_404(Quiz, quiz_id=quiz_id)
        return self.list( request, *args, **kwargs)
    

class SubmitAttemptView(GenericAPIView):
    serializer_class = QuizAttempterSerializer
    queryset = QuizAttempter.objects.all()
    permission_classes = [IsEnroll]

    def post(self, request, *args, **kwargs):
        question_id = kwargs["question_id"]
        option_id = kwargs["option_id"]

        score = 0
        try:
            quiz = get_object_or_404(QuizAttempter, user_attempt=request.user)
            question = quiz.quizz.quizs.get(question_id=question_id)
            opt = Option.objects.filter(quest=question,option_id=option_id)
            get_attempt, create_attempt = AttemtQuestion.objects.get_or_create(quest=question,user=request.user)
            print(len(quiz.quizz.quizs.all()))
            qs = AttemtQuestion.objects.filter(user=request.user)

            if get_attempt.answered == False:
                if opt[0].correct == True:
                    score = 1
                    quiz.score += score
                    get_attempt.answered = True
                    get_attempt.save()
                    if len(quiz.quizz.quizs.all()) != len(qs)+1:
                        quiz.completed =True
                    quiz.save()
                    return Response("Correct Answer",status=HTTP_200_OK)

                quiz.score = score
                get_attempt.answered = True
                get_attempt.save()
                if len(quiz.quizz.quizs.all()) != len(qs):
                    quiz.completed =True
                quiz.save()
                return Response("Wrong Answer",status=HTTP_200_OK)
            return Response("This question has already been answerd by you", status=status.HTTP_403_FORBIDDEN)
        except IndexError:
            return Response("Error due to id mismatch", status=HTTP_500_INTERNAL_SERVER_ERROR)
        
        except QuizAttempter.DoesNotExist:
            return Response("User does not have access to this quiz", status=HTTP_400_BAD_REQUEST)
        