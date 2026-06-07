from django import forms


class BootstrapModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            classes = widget.attrs.get('class', '')
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs['class'] = f'{classes} form-check-input'.strip()
            elif isinstance(widget, forms.Select):
                widget.attrs['class'] = f'{classes} form-select'.strip()
            elif isinstance(widget, (forms.FileInput, forms.ClearableFileInput)):
                widget.attrs['class'] = f'{classes} form-control'.strip()
            else:
                widget.attrs['class'] = f'{classes} form-control'.strip()
