from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Course,Instructor, Syllabus, Category, Topic,Quiz,
    Skills,FAQ,Reviews,Discussion,Answer,Reply,
    Question,Requirement,Settings,
    )

from account.models import Profile
from quiz.serializers import QuizSerializer
from account.serializers import ProfileSerializer


User = get_user_model()

class SearchSerializer(serializers.Serializer):
    query = serializers.CharField()
    

class InstructorSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField(read_only=True) 

    class Meta:
        model = Instructor
        fields = [
            'instructor_id',
            'user',
            'isLead_instructor'
        ]

    def get_user(self, obj):
        return f"{obj.user.email}"

class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField(read_only=True) 
    review_course = serializers.SerializerMethodField(read_only=True)
    created = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Reviews
        fields = [
            'review_id','user','review_course',
            'rate','comment','created'
        ]
    
    def get_user(self, obj):
        return obj.user.email

    def get_review_course(self, obj):
        return obj.review_course.title
    
    def get_created(self, obj):
        return obj.created.strftime('%Y-%m-%d')


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = (
            "topic_id","title","topic_type","file",
            "locked", "created", "updated"
        )


class SyllabusSerializer(serializers.ModelSerializer):
    topics = TopicSerializer(many=True, read_only=True)
    syllabus_quiz=QuizSerializer(read_only=True,many=True)
    topic_count = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Syllabus
        fields = (
            "syllabus_id","title","topic_count",
            "topics","syllabus_quiz","created","updated",
        )

    def get_topic_count(self, obj):
        
        return obj.topics.count()

    def validate_title(self, attrs):
        qs = Syllabus.objects.filter(title__iexact=attrs)
        if qs.exists():
            raise serializers.ValidationError(f"{attrs} has already exist.")
        return attrs


class CategorySerializer(serializers.ModelSerializer):
    """  
        Serializer for lowest level category that has no children
    """
    class Meta:
        model = Category
        fields = ["category_id",'name']

    def __str__(self) -> str:
        return self.name

    def get_category(self, obj):
        return obj.name


class SkillSerializer(serializers.ModelSerializer):

    skill_course = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Skills
        fields = ['skill_id','content','skill_course']

    def get_skill_course(self, obj):
        return obj.skill_course.title

class RequirementSerializer(serializers.ModelSerializer):

    require_course = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Requirement
        fields = ['requirement_id','content','require_course']

    def get_require_course(self, obj):
        return obj.require_course.title

class QuizSerializer(serializers.ModelSerializer):

    class Meta:
        model = Quiz
        fields = [
            "quiz_id","question","option1",
            "option2","option3","option4","answer","created",
        ]


class FAQSerializer(serializers.ModelSerializer):

    faq_course = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = FAQ
        fields = ['faq_id','question','answer','faq_course',"created","updated"]

    def get_faq_course(self, obj):
        return obj.faq_course.title

class EnrollSerializer(serializers.Serializer):
    user = serializers.SerializerMethodField(read_only=True)

    def get_user(self, obj):
        return obj.email

class LikeSerializer(serializers.Serializer):
    user = serializers.SerializerMethodField(read_only=True)

    def get_user(self, obj):
        return obj.fullname


class ReplySerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField(read_only=True)
    answer_reply = serializers.SerializerMethodField(read_only=True)
    like_reply = LikeSerializer(read_only=True, many=True)
    likes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Reply
        fields = [
            "reply_id","user","answer_reply","likes_count",
            "content","like_reply","created","updated"
        ]
        
    def get_user(self, obj):
        return obj.user.fullname

    def get_answer_reply(self, obj):
        return obj.answer_reply.content

    def get_likes_count(self, obj):
        return obj.like_reply.count()

class AnswerSerializer(serializers.ModelSerializer):

    user = serializers.SerializerMethodField(read_only=True)
    question_answer = serializers.SerializerMethodField(read_only=True)
    like_answer = LikeSerializer(read_only=True, many=True)
    reply = ReplySerializer(read_only=True,many=True)
    likes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Answer
        fields = [
            "answer_id","user","question_answer","likes_count",
            "content","reply","like_answer","created","updated"
        ]

    def get_user(self, obj):
        return obj.user.fullname

    def get_question_answer(self, obj):
        return obj.question_answer.question

    def get_likes_count(self, obj):
        return obj.reply.count()

class QuestionSerializer(serializers.ModelSerializer):

    user = serializers.SerializerMethodField(read_only=True)
    answers = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = [
            "question_id","user",
            "question","detail","answers",
            "created","updated"
        ]
    
    def get_user(self, obj):
        return obj.user.fullname
    
    def validate_question(self, attrs):
        qs = Question.objects.filter(question__iexact=attrs)
        if qs.exists():
            raise serializers.ValidationError(f"{attrs} has already exist.")
        return attrs
    
    def create(self, validated_data):
        validated_data
        return super().create(validated_data)


class DiscussionSerializer(serializers.ModelSerializer):

    course_discuss = serializers.SerializerMethodField(read_only=True)
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Discussion
        fields = [
            "discussion_id","course_discuss",
            "questions",
        ]
    
    def get_course_discuss(self, obj):
        return obj.course_discuss.title

    def create(self, validated_data):
        return super().create(validated_data)

class CourseProfileSerializer(serializers.ModelSerializer): 
    syllabus = SyllabusSerializer(many=True, read_only=True)
    skills = SkillSerializer(many=True, read_only=True)
    requirement = RequirementSerializer(many=True, read_only=True)
    title = serializers.CharField(required=True)
    price = serializers.DecimalField(required=True, decimal_places=2, max_digits=7)
    instructors = InstructorSerializer(read_only=True, many=True)
    faqs = FAQSerializer(read_only=True, many=True)
    reviews = ReviewSerializer(read_only=True, many=True)
    enrolled = EnrollSerializer(read_only=True,many=True)
    updated = serializers.SerializerMethodField(read_only=True)
    syllabus_count = serializers.SerializerMethodField(read_only=True)
    total_topic_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Course
        fields = (
                    "course_id","thumbnail","average_rate","count_rate","detail",
                    "title","category","price","faqs","previous_price","requirement",
                    "about","instructors","syllabus","skills","level",
                    "enrolled","enrolled_count","reviews","created","updated",
                    "syllabus_count","total_topic_count","description",
                )

    def get_profile(self, obj):
        profile = Profile.objects.get(user=obj.user)
        return ProfileSerializer(instance=profile).data

    def validate_title(self, attrs):
        qs = Course.objects.filter(title__iexact=attrs)
        if qs.exists():
            raise serializers.ValidationError(f"{attrs} has already exist.")
        return attrs

    def get_updated(self, obj):
        return obj.updated.strftime('%Y-%m-%d')

    def get_syllabus_count(self, obj):
        
        return obj.syllabus.count()

    def get_total_topic_count(self,obj):
        add = 0
        for syllabus in obj.syllabus.all():
            add += syllabus.topics.count()
            # print(syllabus)
        return add  

class CourseSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField(read_only=True)
    syllabus = SyllabusSerializer(many=True, read_only=True)
    skills = SkillSerializer(many=True, read_only=True)
    requirement = RequirementSerializer(many=True, read_only=True)
    title = serializers.CharField(required=True)
    price = serializers.DecimalField(required=True, decimal_places=2, max_digits=7)
    instructors = InstructorSerializer(read_only=True, many=True)
    faqs = FAQSerializer(read_only=True, many=True)
    reviews = ReviewSerializer(read_only=True, many=True)
    enrolled = EnrollSerializer(read_only=True,many=True)
    updated = serializers.SerializerMethodField(read_only=True)
    syllabus_count = serializers.SerializerMethodField(read_only=True)
    total_topic_count = serializers.SerializerMethodField(read_only=True)
    category_name = serializers.SerializerMethodField(read_only=True)    
    class Meta:
        model = Course
        fields = (
                    "course_id","profile","intro","thumbnail","category_name","average_rate","count_rate","detail",
                    "title","category","price","faqs","previous_price","requirement",
                    "about","instructors","syllabus","skills","level",
                    "enrolled","enrolled_count","reviews","created","updated",
                    "syllabus_count","total_topic_count","description",
                )

    def get_profile(self, obj):
        courses = Course.objects.filter(title=obj)
        for course in courses:
            profile = Profile.objects.get(user__user_id=course.user.user_id)
            return ProfileSerializer(instance=profile).data
    
    def get_category_name(self,obj):
        cat = CategorySerializer(instance=obj.category).data
        return cat

    def validate_title(self, attrs):
        qs = Course.objects.filter(title__iexact=attrs)
        if qs.exists():
            raise serializers.ValidationError(f"{attrs} has already exist.")
        return attrs

    def get_updated(self, obj):
        return obj.updated.strftime('%Y-%m-%d')

    def get_syllabus_count(self, obj):
        
        return obj.syllabus.count()

    def get_total_topic_count(self,obj):
        add = 0
        for syllabus in obj.syllabus.all():
            add += syllabus.topics.count()
            # print(syllabus)
        return add

    def create(self, validated_data):

        return super().create(validated_data)


class InstructorRequestSerializer(serializers.Serializer):

    email = serializers.EmailField()


class QuizAnswerSerializer(serializers.Serializer):

    answer = serializers.CharField(write_only=True)


class InstructorRequestResponseSerializer(serializers.Serializer):

    reply = serializers.CharField()


class InstructorDetailSerializer(serializers.Serializer):

    rate_count = serializers.IntegerField(read_only=True)



class SettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Settings
        fields = '__all__'


{
"question" : "",
"option1": "",
"option2": "",
"option3": "",
"option4": ""
}

{
    "question": "Gender of quadri",
    "option1": "Male",
    "option2": "Female",
    "option3": "Trans",
    "option4": "None of the above",
    "answer": "Male"
}