
# Create your tests here.
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from course.models import Course
from django.contrib.auth import get_user_model

User = get_user_model()

class CourseUserCreateListAPIViewTests(APITestCase):
    def setUp(self):
        self.url = reverse('courses_user')
        self.user = User.objects.create_user(email='testuser',fullname="test",password='testpassword90')
        self.client.login(email='testuser', password='testpassword90')
        print(self.client.session.serializer)
        self.course_data = {
                            "category": "category_cV4qCXfuPkpQS5RTMdVaRr",
                            "description" : "wreje",
                            "detail" : "wwhw",
                            "level": "General",
                            "previous_price": "300",
                            "price": "200",
                            "title": "R9WW"
                            }

    def test_create_course(self):
        response = self.client.post(self.url, self.course_data)
        print(response)
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     self.assertEqual(Course.objects.count(), 1)
    #     self.assertEqual(Course.objects.get().title, 'Test Course')
    #     self.assertEqual(Course.objects.get().user, self.user)

    # def test_create_course_with_invalid_data(self):
    #     response = self.client.post(self.url, {})
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertEqual(Course.objects.count(), 0)

    # def test_list_courses(self):
    #     Course.objects.create(title='Course 1')
    #     Course.objects.create(title='Course 2')
    #     response = self.client.get(self.url)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(len(response.data), 2)
