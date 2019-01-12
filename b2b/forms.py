from django import forms
from django.forms import inlineformset_factory
from django.utils import timezone

from .models import Post, Images


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'description', 'initial_price', 'content', 'date_end')


class PostUpdateForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'description', 'initial_price', 'content', 'date_end')


class ImageForm(forms.ModelForm):
    class Meta:
        model = Images
        fields = {'post_image'}


ImageFormSet = inlineformset_factory(Post, Images, fields=('post_image',), extra=5)


class BidForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = {'current_price'}

    def clean_current_price(self):
        form_current_price = self.cleaned_data.get('current_price')
        if self.instance.date_end >= timezone.now():
            if self.instance.initial_price <= form_current_price > self.instance.current_price:
                return form_current_price
            else:
                raise forms.ValidationError('values must be higher than the current bid and minimum price')
        raise forms.ValidationError('Sorry, the bidding time is over :(')
