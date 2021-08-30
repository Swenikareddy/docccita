from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, ListView, UpdateView

from ..decorators import patient_required
from ..forms import patientInterestsForm, patientSignUpForm, TakeQuizForm
from ..models import Quiz, patient, TakenQuiz, User


class patientSignUpView(CreateView):
    model = User
    form_class = patientSignUpForm
    template_name = 'registration/signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'patient'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('students:quiz_list')


@method_decorator([login_required, patient_required], name='dispatch')
class patientInterestsView(UpdateView):
    model = patient
    form_class = patientInterestsForm
    template_name = 'ua/patient/interests_form.html'
    success_url = reverse_lazy('patient:quiz_list')

    def get_object(self):
        return self.request.user.patient

    def form_valid(self, form):
        messages.success(self.request, 'Interests updated with success!')
        return super().form_valid(form)


@method_decorator([login_required, patient_required], name='dispatch')
class QuizListView(ListView):
    model = Quiz
    ordering = ('name', )
    context_object_name = 'quizzes'
    template_name = 'classroom/patient/quiz_list.html'

    def get_queryset(self):
        patient = self.request.user.patient
        student_interests = patient.interests.values_list('pk', flat=True)
        taken_quizzes = patient.quizzes.values_list('pk', flat=True)
        queryset = Quiz.objects.filter(subject__in=patient_interests) \
            .exclude(pk__in=taken_quizzes) \
            .annotate(questions_count=Count('questions')) \
            .filter(questions_count__gt=0)
        return queryset


@method_decorator([login_required, patient_required], name='dispatch')
class TakenQuizListView(ListView):
    model = TakenQuiz
    context_object_name = 'taken_quizzes'
    template_name = 'ua/patient/taken_quiz_list.html'

    def get_queryset(self):
        queryset = self.request.user.patient.taken_quizzes \
            .select_related('quiz', 'quiz__patient') \
            .order_by('quiz__name')
        return queryset


@login_required
@patient_required
def take_quiz(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    patient = request.user.patient

    if patient.quizzes.filter(pk=pk).exists():
        return render(request, 'patient/taken_quiz.html')

    total_questions = quiz.questions.count()
    unanswered_questions = patient.get_unanswered_questions(quiz)
    total_unanswered_questions = unanswered_questions.count()
    progress = 100 - round(((total_unanswered_questions - 1) / total_questions) * 100)
    question = unanswered_questions.first()

    if request.method == 'POST':
        form = TakeQuizForm(question=question, data=request.POST)
        if form.is_valid():
            with transaction.atomic():
                patient_answer = form.save(commit=False)
                patient_answer.student = student
                patient_answer.save()
                if patient.get_unanswered_questions(quiz).exists():
                    return redirect('patient:take_quiz', pk)
                else:
                    correct_answers = patient.quiz_answers.filter(answer__question__quiz=quiz, answer__is_correct=True).count()
                    score = round((correct_answers / total_questions) * 100.0, 2)
                    TakenQuiz.objects.create(patient=patient, quiz=quiz, score=score)
                    if score < 50.0:
                        messages.warning(request, 'Better luck next time! Your score for the quiz %s was %s.' % (quiz.name, score))
                    else:
                        messages.success(request, 'Congratulations! You completed the quiz %s with success! You scored %s points.' % (quiz.name, score))
                    return redirect('patient:quiz_list')
    else:
        form = TakeQuizForm(question=question)

    return render(request, 'ua/patient/take_quiz_form.html', {
        'quiz': quiz,
        'question': question,
        'form': form,
        'progress': progress
    })
