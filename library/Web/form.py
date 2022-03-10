from django.forms import ModelForm, TextInput, PasswordInput,FileInput
from Core.models import User
from django import forms

class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password', ]  # 只显示 model 中指定的字段
        # 指定呈现样式字段、指定 CSS 样式
        widgets = {
            'username': TextInput(attrs={'class': 'login-input',
                                         'placeholder': '用户名',
                                         'name':'username'}),
            'password': PasswordInput(attrs={'class':'login-input',
                'placeholder': '用户密码',
                'name':'password',
                'autocomplete':'off' })
        
        }
                
class UploadFileForm(forms.Form):
    file = forms.FileField(widget = forms.FileInput(attrs={
                    'class':'form-control',
                    'id':'formFile',
                    'required':'required',
                    'accept':'image/jpeg,image/jpg,image/png',
                    })
                )


