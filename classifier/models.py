from django.db import models

class WordGrade(models.Model):
    word = models.CharField(max_length=100, unique=True)
    grade = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.word} ({self.grade})"