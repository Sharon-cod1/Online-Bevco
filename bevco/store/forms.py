from django import forms

class PhoneForm(forms.Form):
    phone = forms.CharField(label='Phone Number', max_length=15)

class OTPForm(forms.Form):
    otp = forms.CharField(label='Enter OTP', max_length=6)
