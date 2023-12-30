from django import forms
from django.contrib.auth.forms import SetPasswordForm
from .models import CustomUser


class PasswordResetRequestForm(forms.Form):
    username = forms.CharField(
        max_length = 150,
        widget = forms.TextInput(
            attrs = {
                'class': 'form-control',
                'style': 'margin-top: 20px; width: 700px; display: initial;',
                'placeholder': 'Digite seu nome de usuário',
            }
        ),
        label='Usuario'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Adiciona classes ao form-group e ao campo username
        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['username'].widget.attrs['aria-label'] = 'Usuario'
        self.fields['username'].widget.attrs['aria-describedby'] = 'username-addon'
        self.fields['username'].widget.attrs['style'] = 'margin-top: 20px; width: 700px; display: initial;'

        # Adiciona a classe ao rótulo (label)
        self.fields['username'].label = 'Usuário'
        self.fields['username'].label_attrs = {'class': 'form-label mt-4'}  # Adiciona a classe ao rótulo

    def as_div(self):
        """Customize a renderização do formulário para adicionar a classe 'form-label' à label."""
        return self._html_output(
            normal_row='<div class="form-group">%(label)s %(field)s%(help_text)s</div>',
            error_row='<div class="form-group errorlist">%s</div>',
            row_ender='</div>',
            help_text_html=' <span class="helptext">%s</span>',
            errors_on_separate_row=True
        )
    

class CustomSetPasswordForm(SetPasswordForm):
    def as_custom_form(self):
        output = []
        for name, bound_field in self.fields.items():
            output.append('<div class="form-group">')
            output.append('<fieldset>')
            output.append('<label class="form-label mt-4" for="%s">%s:</label>' % (name, bound_field.label))

            widget_input_type = getattr(bound_field.widget, 'input_type', None)
            widget_attrs = ' '.join([f'{k}="{v}"' for k, v in bound_field.widget.attrs.items()])
            output.append('<input class="form-control" type="%s" name="%s" %s />' % (
                widget_input_type if widget_input_type else 'text',
                name,
                widget_attrs
            ))

            output.append('%s%s' % (bound_field, bound_field.help_text))
            output.append('</fieldset>')
            output.append('</div>')
        
        return ''.join(output)
    

class CustomPasswordResetRequestForm(PasswordResetRequestForm):
    def as_custom_form(self):
        output = []
        for name, bound_field in self.fields.items():
            output.append('<div class="form-group">')
            output.append('<fieldset>')
            output.append('<label class="form-label mt-4" for="%s">%s:</label>' % (name, bound_field.label))

            widget_input_type = getattr(bound_field.widget, 'input_type', None)
            widget_attrs = ' '.join([f'{k}="{v}"' for k, v in bound_field.widget.attrs.items()])
            output.append('<input class="form-control" type="%s" name="%s" %s />' % (
                widget_input_type if widget_input_type else 'text',
                name,
                widget_attrs
            ))

            output.append('%s%s' % (bound_field, bound_field.help_text))
            output.append('</fieldset>')
            output.append('</div>')
        
        return ''.join(output)