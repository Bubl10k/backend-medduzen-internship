from pydantic import BaseModel, condecimal


class QuizResult(BaseModel):
    average_score: condecimal(gt=-1, lt=10)
    percentage: condecimal(ge=0, lt=1)
    total_correct: int
    total_questions: int
