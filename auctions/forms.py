from django import forms

from .models import AuctionListing, Comment, Bid


class CreateListingForm(forms.ModelForm):
    class Meta:
        model = AuctionListing
        fields = ['name', 'description', 'current_bid', 'photo', 'category']

    
class CreateCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'placeholder': 'Add a comment', 'rows': 3})
        }
        labels = {
            'content': '',
        }


class CreateBidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['value']
        labels = {
            'value': '',
        }