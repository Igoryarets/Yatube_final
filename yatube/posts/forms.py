from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post

        fields = ('text', 'group', 'image')
        labels = {'text': ('текст'), 'group': ('группа')}
        help_texts = {'group': ('Выберите подходящую группу для поста')}


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment

        fields = ['text']
