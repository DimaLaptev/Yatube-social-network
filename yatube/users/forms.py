from django.contrib.auth.forms import UserCreationForm
#from django.contrib.auth import get_user_model
#from django import forms
from .models import CustomUser


#User = get_user_model()


class CreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'phone')

'''
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('phone',)'''
