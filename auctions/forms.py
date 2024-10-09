from django import forms

class CreateListingForm(forms.Form):
    name = forms.CharField(label="Name:", required=True)
    description = forms.CharField(label="Description:", widget=forms.Textarea(), required=False)
    starting_bid = forms.DecimalField(label="Starting Bid:", required=True)
    photo = forms.ImageField(label="Photo:", required=False)

