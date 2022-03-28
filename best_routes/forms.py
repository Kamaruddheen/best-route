from django import forms


class AddDocumentCSVForm(forms.Form):
    input_file = forms.FileField(widget=forms.FileInput(
        attrs={'accept': '.csv'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['input_file'].label = "Upload .csv file"

    # def clean(self):
    #     value = self.cleaned_data.get('file')
    #     if not value.name.endswith('.csv'):
    #         raise forms.ValidationError(u'Unsupported File')
    #     return value
