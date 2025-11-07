from django import forms
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
import datetime

class PhotoMetaForm(forms.Form):
    title = forms.CharField(label='Название', max_length=200)
    photographer = forms.CharField(label='Фотограф', max_length=200, required=False)
    date_taken = forms.DateField(label='Дата съёмки', required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    location = forms.CharField(label='Место', max_length=200, required=False)
    tags = forms.CharField(label='Теги', max_length=500, required=False, help_text='Через запятую')
    camera = forms.CharField(label='Камера', max_length=200, required=False)
    resolution = forms.CharField(label='Разрешение', max_length=100, required=False, help_text='например: 4000x3000')
    license = forms.CharField(label='Лицензия', max_length=200, required=False)
    source_url = forms.URLField(label='Источник (URL)', required=False)
    export_format = forms.ChoiceField(label='Формат файла', choices=(('json','JSON'),('xml','XML')))

    def clean_date_taken(self):
        d = self.cleaned_data.get('date_taken')
        if d and d > datetime.date.today():
            raise ValidationError('Дата съёмки не может быть в будущем')
        return d

    def clean_resolution(self):
        r = self.cleaned_data.get('resolution')
        if r:
            parts = r.lower().split('x')
            if len(parts) != 2:
                raise ValidationError('Разрешение должно быть в формате WIDTHxHEIGHT')
            try:
                w = int(parts[0])
                h = int(parts[1])
                if w <= 0 or h <= 0:
                    raise ValidationError('Числа разрешения должны быть положительными')
            except ValueError:
                raise ValidationError('Разрешение должно содержать числа')
        return r

    def clean_tags(self):
        t = self.cleaned_data.get('tags', '')
        if t:
            tags = [x.strip() for x in t.split(',') if x.strip()]
            if len(tags) > 10:
                raise ValidationError('Можно указать не более 10 тегов')
        return t

    def clean_source_url(self):
        url = self.cleaned_data.get('source_url')
        if url:
            validator = URLValidator()
            validator(url)
        return url
