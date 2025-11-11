from django import forms
from datetime import date

EXPORT_CHOICES = [
    ('json', 'JSON'),
    ('xml', 'XML'),
    
]

EXPORT_CHOICES1= [
    ('Да', 'да'),
    ('Нет','нет')                     
]

class PhotoMetaForm(forms.Form):
    title = forms.CharField(
        label='Название (обязательное)',
        max_length=200,
        required=True,
        error_messages={'required': 'Введите название фотографии'}
    )
    photographer = forms.CharField(
        label='Фотограф',
        max_length=200,
        required=False
    )
    date_taken = forms.DateField(
        label='Дата съёмки',
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        error_messages={'invalid': 'Введите корректную дату'}
    )
    location = forms.CharField(
        label='Место',
        max_length=200,
        required=False
    )
    tags = forms.CharField(
        label='Теги (через запятую)',
        max_length=500,
        required=False
    )
    camera = forms.CharField(
        label='Камера',
        max_length=200,
        required=False
    )
    resolution = forms.CharField(
        label='Разрешение (например 4000x3000)',
        max_length=100,
        required=False
    )
    license = forms.CharField(
        label='Лицензия',
        max_length=200,
        required=False
    )
    apryov = forms.ChoiceField(
        label='Разрешение на публикацию в сети',
        choices = EXPORT_CHOICES1,
        required=True,
        error_messages={'required': 'даете ли вы согласие'}
    )
    export_format = forms.ChoiceField(
        label='Формат файла',
        choices=EXPORT_CHOICES,
        required=True,
        error_messages={'required': 'Выберите формат (JSON или XML)'}
    )

    def clean_date_taken(self):
        dt = self.cleaned_data.get('date_taken')
        if dt and dt > date.today():
            raise forms.ValidationError('Дата съёмки не может быть в будущем')
        return dt

    def clean_resolution(self):
        r = self.cleaned_data.get('resolution')
        if r:
            parts = r.lower().split('x')
            if len(parts) != 2:
                raise forms.ValidationError('Разрешение должно быть в формате WIDTHxHEIGHT')
            try:
                w = int(parts[0]); h = int(parts[1])
                if w <= 0 or h <= 0:
                    raise forms.ValidationError('Числа разрешения должны быть положительными')
            except ValueError:
                raise forms.ValidationError('Разрешение должно содержать числа')
        return r

    def clean_tags(self):
        t = self.cleaned_data.get('tags', '')
        if t:
            tags = [x.strip() for x in t.split(',') if x.strip()]
            if len(tags) > 20:
                raise forms.ValidationError('Можно указать не более 20 тегов')
        return t
