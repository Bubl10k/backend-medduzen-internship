from rest_framework import status
from rest_framework.test import APITestCase

from backend.apps.company.models import Company
from backend.apps.quiz.models import Answer, Question, Quiz, Result
from backend.apps.users.models import CustomUser


class QuizTest(APITestCase):
    def setUp(self):
        self.owner = CustomUser.objects.create_user(
            username="testuser", password="testpassword", email="testuser@example.com"
        )
        self.user = CustomUser.objects.create_user(
            username="testuser2", password="testpassword", email="testuser2@example.com"
        )
        self.company = Company.objects.create(name="Test Company", owner=self.owner)
        self.company.members.add(self.owner)
        self.company.members.add(self.user)
        self.client.force_authenticate(user=self.owner)
        self.quiz = Quiz.objects.create(
            title="Sample Quiz", frequency=0, company=self.company
        )
        self.question = Question.objects.create(
            text="What is 2 + 2?", quiz=self.quiz
        )
        self.answer = Answer.objects.create(
            text="4", is_correct=True, question=self.question
        )
    
    def test_quiz_create(self):
        quiz_data = {
            "title": "Test",
            "frequency": 0,
            "company": self.company.id,
            "questions": [
                {
                    "text": "What is 2 + 2?",
                    "answers": [
                        {"text": "4", "is_correct": True},
                        {"text": "5", "is_correct": False},
                    ],
                },
                {
                    "text": "What is 3 + 3?",
                    "answers": [
                        {"text": "6", "is_correct": True},
                        {"text": "7", "is_correct": False},
                    ],
                },
            ],
        }
        response = self.client.post("/api/quiz/quizzes/", data=quiz_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Quiz.objects.count(), 2)
        self.assertEqual(Question.objects.count(), 3)
        self.assertEqual(Answer.objects.count(), 5)
    
    def test_quiz_update(self):
        update_data = {"title": "Updated Quiz"}
        response = self.client.patch(f"/api/quiz/quizzes/{self.quiz.id}/", data=update_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.quiz.refresh_from_db()
        self.assertEqual(self.quiz.title, "Updated Quiz")
    
    def test_quiz_delete(self):
        response = self.client.delete(f"/api/quiz/quizzes/{self.quiz.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Quiz.objects.count(), 0)
            
    def test_add_question(self):
        question_data = {
            "text": "Test",
            "answers": [
                {"text": "test", "is_correct": True},
                {"text": "test2", "is_correct": False},
            ],
        } 
        response = self.client.patch(
            f"/api/quiz/quizzes/{self.quiz.id}/add_question/", data=question_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    
    def test_remove_question(self):
        question_to_remove = {"question": self.question.id}
        response = self.client.patch(
            f"/api/quiz/quizzes/{self.quiz.id}/remove_question/", data=question_to_remove, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.quiz.refresh_from_db()
        
        self.assertNotIn(self.question, self.quiz.questions.all())
        self.assertEqual(response.data["detail"], "Question removed successfully.")
    
    def test_start_quiz(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(f"/api/quiz/quizzes/{self.quiz.id}/start_quiz/", format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        result = Result.objects.filter(user=self.user, quiz=self.quiz).first()
        self.assertIsNotNone(result)
        self.assertEqual(result.status, Result.QuizStatus.STARTED)
    
    def test_complete_quiz(self):
        self.client.force_authenticate(user=self.user)
        self.client.post(f"/api/quiz/quizzes/{self.quiz.id}/start_quiz/", format="json")

        answers_data = [
            {"question": self.question.id, "answer": self.answer.id},
        ]
        
        response = self.client.post(
            f"/api/quiz/quizzes/{self.quiz.id}/complete_quiz/", 
            data={"answers": answers_data}, 
            format="json"
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["detail"], "Quiz completed successfully.")
        result = Result.objects.get(user=self.user, quiz=self.quiz)
        self.assertEqual(result.status, Result.QuizStatus.COMPLETED)
        self.assertEqual(result.score, 1)
        self.assertEqual(result.total_question, 1)
    
    def test_average_scores(self):
        self.client.force_authenticate(user=self.user)
        self.client.force_authenticate(user=self.owner)
        
        self.client.post(f"/api/quiz/quizzes/{self.quiz.id}/start_quiz/", format="json")
        answers_data = [{"question": self.question.id, "answer": self.answer.id}]
        self.client.post(
            f"/api/quiz/quizzes/{self.quiz.id}/complete_quiz/",
            data={"answers": answers_data},
            format="json",
        )

        quiz2 = Quiz.objects.create(title="Second Quiz", company=self.company, frequency=0)
        question2 = Question.objects.create(text="What is 3 + 5?", quiz=quiz2)
        answer2 = Answer.objects.create(text="8", is_correct=True, question=question2)
        self.client.post(f"/api/quiz/quizzes/{quiz2.id}/start_quiz/", format="json")
        answers_data2 = [{"question": question2.id, "answer": None}]
        self.client.post(
            f"/api/quiz/quizzes/{quiz2.id}/complete_quiz/",
            data={"answers": answers_data2},
            format="json",
        )

        other_company = Company.objects.create(name="Other Company", owner=self.owner)
        other_company.members.add(self.owner)
        other_company.members.add(self.user)
        quiz3 = Quiz.objects.create(title="Third Quiz", company=other_company, frequency=0)
        question3 = Question.objects.create(text="What is 2 + 2?", quiz=quiz3)
        answer3 = Answer.objects.create(text="4", is_correct=True, question=question3)
        self.client.post(f"/api/quiz/quizzes/{quiz3.id}/start_quiz/", format="json")
        answers_data3 = [{"question": question3.id, "answer": answer3.id}]
        self.client.post(
            f"/api/quiz/quizzes/{quiz3.id}/complete_quiz/",
            data={"answers": answers_data3},
            format="json",
        )

        response = self.client.get(f"/api/quiz/quizzes/{self.quiz.id}/results/", format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        company_results = data["company_results"]
        self.assertEqual(company_results["total_correct"], 1)
        self.assertEqual(company_results["total_question"], 2)
        self.assertAlmostEqual(company_results["average_score"], 5.00, places=2)  # (1/2)*10

        global_results = data["global_results"]
        self.assertEqual(global_results["total_correct"], 2)
        self.assertEqual(global_results["total_question"], 3)
        self.assertAlmostEqual(global_results["average_score"], 6.67, places=2)  # (2/3)*10
    
    def test_list_average_scores(self):
        Result.objects.create(user=self.user, quiz=self.quiz, company=self.company, score=8, total_question=10, status=Result.QuizStatus.COMPLETED)
        quiz2 = Quiz.objects.create(title="Second Quiz", frequency=0, company=self.company)
        Result.objects.create(user=self.user, quiz=quiz2, company=self.company, score=7, total_question=10, status=Result.QuizStatus.COMPLETED)

        response = self.client.get("/api/quiz/quizzes/list_average_scores/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["quiz_id"], self.quiz.id)
        self.assertEqual(data[1]["quiz_id"], quiz2.id)
        self.assertAlmostEqual(data[0]["average_score"], 0.8, places=1)
        self.assertAlmostEqual(data[1]["average_score"], 0.7, places=1)
        
    def test_list_user_scores(self):
        Result.objects.create(user=self.user, quiz=self.quiz, company=self.company, score=9, total_question=10, status=Result.QuizStatus.COMPLETED)
        quiz2 = Quiz.objects.create(title="Second Quiz", frequency=0, company=self.company)
        Result.objects.create(user=self.user, quiz=quiz2, company=self.company, score=5, total_question=10, status=Result.QuizStatus.COMPLETED)
        
        response = self.client.get(f"/api/quiz/quizzes/list_average_user_scores/?user={self.user.id}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["quiz_id"], self.quiz.id)
        self.assertAlmostEqual(data[0]["average_score"], 0.9, places=1)
        self.assertEqual(data[1]["quiz_id"], quiz2.id)
        self.assertAlmostEqual(data[1]["average_score"], 0.5, places=1)
    