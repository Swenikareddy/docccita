from django.urls import include, path

from .views import ua, doctor, patient

urlpatterns = [
    path('', ua.home, name='home'),

    path('patient/', include(([
        path('', patient.QuizListView.as_view(), name='quiz_list'),
        path('interests/', patient.patientInterestsView.as_view(), name='patient_interests'),
        path('taken/', patient.TakenQuizListView.as_view(), name='taken_quiz_list'),
        path('quiz/<int:pk>/', patient.take_quiz, name='take_quiz'),
    ], 'classroom'), namespace='patient')),

    path('doctor/', include(([
        path('', doctor.QuizListView.as_view(), name='quiz_change_list'),
        path('quiz/add/', doctor.QuizCreateView.as_view(), name='quiz_add'),
        path('quiz/<int:pk>/', doctor.QuizUpdateView.as_view(), name='quiz_change'),
        path('quiz/<int:pk>/delete/', doctor.QuizDeleteView.as_view(), name='quiz_delete'),
        path('quiz/<int:pk>/results/', doctor.QuizResultsView.as_view(), name='quiz_results'),
        path('quiz/<int:pk>/question/add/', doctor.question_add, name='question_add'),
        path('quiz/<int:quiz_pk>/question/<int:question_pk>/', doctor.question_change, name='question_change'),
        path('quiz/<int:quiz_pk>/question/<int:question_pk>/delete/', doctor.QuestionDeleteView.as_view(), name='question_delete'),
    ], 'ua'), namespace='doctor')),
]
