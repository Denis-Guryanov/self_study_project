from django.contrib import admin

from .models import Answer, Question, Test, TestResult

admin.site.register(Test)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(TestResult)
