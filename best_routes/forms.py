from django import forms


class AddDocumentCSVForm(forms.Form):
    input_file = forms.FileField(widget=forms.FileInput(
        attrs={'accept': '.csv'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['input_file'].label = "Upload .csv file"
