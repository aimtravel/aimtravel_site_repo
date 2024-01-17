from django import forms


class YesNoRadioSelect(forms.widgets.RadioSelect):
    choices = (
        (True, 'Yes'),
        (False, 'No'),
    )

    def render(self, name, value, attrs=None, renderer=None):
        return super().render(name, value, attrs, renderer)