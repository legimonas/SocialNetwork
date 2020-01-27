from django import forms
from posts.models import *


class PostForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)

        for key in self.fields:
            self.fields[key].required = False

    class Meta:
        model = Post
        fields = [
            'title',
            'text',
            'likes'
        ]