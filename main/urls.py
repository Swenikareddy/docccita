from django.urls import include, path

from ua.views import ua, patient, doctor

urlpatterns = [
    path('', include('ua.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/signup/', ua.SignUpView.as_view(), name='signup'),
    path('accounts/signup/patient/', patient.patientSignUpView.as_view(), name='patient_signup'),
    path('accounts/signup/teacher/', doctor.doctorSignUpView.as_view(), name='doctor_signup'),
]
