import os
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import Http404
from .forms import PhotoMetaForm
from . import utils

def index(request):
    files = utils.list_all_files()
    has_any = bool(files['json'] or files['xml'])
    return render(request, 'photo_meta_app/index.html', {'files': files, 'has_any': has_any})

def add_metadata(request):
    if request.method == 'POST':
        form = PhotoMetaForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data.copy()

            # convert date -> ISO string
            if data.get('date_taken'):
                data['date_taken'] = data['date_taken'].isoformat()

            # tags -> list
            tags = data.get('tags')
            if tags:
                data['tags'] = [t.strip() for t in tags.split(',') if t.strip()]
            else:
                data['tags'] = []

            export_format = data.pop('export_format')

            try:
                if export_format == 'json':
                    path = utils.save_dict_as_json(data)
                else:
                    path = utils.save_dict_as_xml(data)
                messages.success(request, f'Файл сохранён: {os.path.basename(path)}')
                return redirect('photo_meta_app:index')
            except Exception as e:
                messages.error(request, 'Ошибка при сохранении: ' + str(e))
        else:
            messages.error(request, 'Проверьте правильность заполнения формы')
    else:
        form = PhotoMetaForm()
    return render(request, 'photo_meta_app/add_metadata.html', {'form': form})

def upload_file(request):
    if request.method == 'POST' and request.FILES.get('data_file'):
        uploaded = request.FILES['data_file']
        # Save to temp with safe name
        temp_name = utils.generate_safe_filename('upload')
        temp_path = os.path.join(utils.TMP_DIR, temp_name)
        try:
            with open(temp_path, 'wb') as f:
                for chunk in uploaded.chunks():
                    f.write(chunk)
        except Exception as e:
            messages.error(request, 'Ошибка при сохранении временного файла: ' + str(e))
            return redirect('photo_meta_app:upload_file')

        ok, kind, data, ext = utils.detect_and_validate_uploaded_file(temp_path)
        if not ok:
            try:
                os.remove(temp_path)
            except Exception:
                pass
            messages.error(request, 'Файл не валиден: ' + kind)
            return redirect('photo_meta_app:upload_file')

        final_name = utils.generate_safe_filename(ext)
        if ext == 'json':
            dest = os.path.join(utils.UPLOAD_DIR_JSON, final_name)
        else:
            dest = os.path.join(utils.UPLOAD_DIR_XML, final_name)
        try:
            os.replace(temp_path, dest)
        except Exception as e:
            messages.error(request, 'Ошибка при перемещении файла: ' + str(e))
            return redirect('photo_meta_app:upload_file')
        messages.success(request, 'Файл загружен как ' + final_name)
        return redirect('photo_meta_app:index')
    return render(request, 'photo_meta_app/upload.html')

def view_file(request, filename):
    for folder in (utils.UPLOAD_DIR_JSON, utils.UPLOAD_DIR_XML):
        path = os.path.join(folder, filename)
        if os.path.exists(path) and os.path.isfile(path):
            ok, kind, data = utils.read_file_content(path)
            if not ok:
                raise Http404('Файл не валиден')
            return render(request, 'photo_meta_app/file_view.html', {'data': data, 'filename': filename, 'kind': kind})
    raise Http404('Файл не найден')
