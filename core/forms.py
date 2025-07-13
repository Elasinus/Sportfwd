from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from .models import Profile  # Make sure Profile model exists in core/models.py

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={
        'placeholder': 'Username or Email'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Password'
    }))


class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={
        'placeholder': 'Password'
    }))
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput(attrs={
        'placeholder': 'Confirm Password'
    }))
    role = forms.ChoiceField(choices=[('athlete', 'Athlete'), ('sponsor', 'Sponsor'), ('fan', 'Fan')])
    school = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'placeholder': 'Current School'
    }))
    grad_year = forms.IntegerField(
        label="Graduation Year",
        widget=forms.NumberInput(attrs={
            'placeholder': 'Graduation Year',
            'min': '1900',
            'max': '2099'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Username'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'Full Name'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

    def clean_grad_year(self):
        year = self.cleaned_data.get('grad_year')
        if year < 1900 or year > 2099:
            raise forms.ValidationError("Please enter a valid 4-digit graduation year.")
        return year

    def save(self, commit=True):
        user = super().save(commit=False)
        user.password = make_password(self.cleaned_data["password1"])
        if commit:
            user.save()
            Profile.objects.create(
                user=user,
                role=self.cleaned_data["role"],
                school=self.cleaned_data["school"],
                grad_year=self.cleaned_data["grad_year"]
            )
        return user
