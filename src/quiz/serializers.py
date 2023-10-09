from rest_framework import serializers

from .models import Option, Question, Quiz,QuizAttempter


class OptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Option
        fields = ["option_id",'option','correct']

        
class QuestionSerializer(serializers.ModelSerializer):

    option = OptionSerializer(source="opt",read_only=True,many=True)

    class Meta:
        model = Question
        fields = ['question_id','question','option']


class QuizSerializer(serializers.ModelSerializer):
    quizs = QuestionSerializer(many=True, read_only=True)
    class Meta:
        model = Quiz
        fields = ['quiz_id',"title","quizs"]

    def validate_title(self, attrs):
        qs = Quiz.objects.filter(title__iexact=attrs)
        if qs.exists():
            raise serializers.ValidationError(f"{attrs} has already exist.")
        return attrs
    
class QuizAttempterSerializer(serializers.ModelSerializer):

    score = serializers.SerializerMethodField(read_only=True)
    user_attempt = serializers.SerializerMethodField(read_only=True)
    quizz = serializers.SerializerMethodField(read_only=True)
    completed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = QuizAttempter
        fields = [
            "score","user_attempt","quizz","completed"
        ]

    def get_score(self, obj):
        return obj.score

    def get_user_attempt(self, obj):
        return obj.user_attempt.fullname

    def get_quizz(self, obj):
        return obj.quizz.title

    def get_completed(self, obj):
        return obj.completed