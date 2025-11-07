from django import forms
from .models import *  # Replace with your actual model


# class NewsAdminForm(forms.ModelForm):
#     class Meta:
#         model = News
#         fields = '__all__'  # You can specify the fields you want to include
#
#     news_content = forms.CharField(widget=CKEditorWidget())


# class FeedbackAdminForm(forms.ModelForm):
#     class Meta:
#         model = MainFeedback
#         fields = '__all__'  # You can specify the fields you want to include
#
#     feedback_1_content = forms.CharField(widget=CKEditorWidget())