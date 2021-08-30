from django.shortcuts import redirect, render
from django.views.generic import TemplateView


class SignUpView(TemplateView):
    template_name = 'registration/signup.html'


def home(request):
    if request.user.is_authenticated:
        if request.user.is_doctor:
            return redirect('doctor:quiz_change_list')
        else:
            return redirect('patient:quiz_list')
    return render(request, 'ua/home.html')
