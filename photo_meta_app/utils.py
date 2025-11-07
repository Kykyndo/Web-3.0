import os
import json
import uuid
from xml.etree import ElementTree as ET
from django.conf import settings

UPLOAD_DIR_JSON = os.path.join(settings.MEDIA_ROOT, 'json')
UPLOAD_DIR_XML = os.path.join(settings.MEDIA_ROOT, 'xml')
TMP_DIR = os.path.join(settings.MEDIA_ROOT, 'tmp_uploads')

os.makedirs(UPLOAD_DIR_JSON, exist_ok=True)
os.makedirs(UPLOAD_DIR_XML, exist_ok=True)
os.makedirs(TMP_DIR, exist_ok=True)

REQUIRED_KEYS = {'title'}

def generate_safe_filename(ext: str) -> str:
    return f"{uuid.uuid4().hex}.{ext}"

def save_dict_as_json(data: dict, filename: str = None) -> str:
    if filename is None:
        filename = generate_safe_filename('json')
    path = os.path.join(UPLOAD_DIR_JSON, filename)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return path

def dict_to_xml(data: dict) -> ET.Element:
    root = ET.Element('photo')
    for k, v in data.items():
        if isinstance(v, list):
            parent = ET.SubElement(root, k)
            for item in v:
                child = ET.SubElement(parent, 'item')
                child.text = str(item)
        else:
            child = ET.SubElement(root, k)
            child.text = '' if v is None else str(v)
    return root

def save_dict_as_xml(data: dict, filename: str = None) -> str:
    if filename is None:
        filename = generate_safe_filename('xml')
    path = os.path.join(UPLOAD_DIR_XML, filename)
    root = dict_to_xml(data)
    tree = ET.ElementTree(root)
    tree.write(path, encoding='utf-8', xml_declaration=True)
    return path

def validate_json_file(path: str):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        return False, f'Ошибка JSON: {e}', {}
    if not isinstance(data, dict):
        return False, 'Корневой элемент должен быть объект (словарь)', {}
    if not REQUIRED_KEYS.issubset(set(data.keys())):
        return False, f'Отсутствуют обязательные ключи: {REQUIRED_KEYS}', {}
    return True, 'OK', data

def validate_xml_file(path: str):
    try:
        tree = ET.parse(path)
        root = tree.getroot()
    except Exception as e:
        return False, f'Ошибка XML: {e}', {}
    if root.tag != 'photo':
        return False, 'Корневой элемент XML должен быть <photo>', {}
    data = {}
    for child in root:
        if list(child):
            data[child.tag] = [c.text for c in child.findall('item')]
        else:
            data[child.tag] = child.text
    if not REQUIRED_KEYS.issubset(set(data.keys())):
        return False, f'Отсутствуют обязательные ключи: {REQUIRED_KEYS}', {}
    return True, 'OK', data

def detect_and_validate_uploaded_file(temp_path: str):
    ok, msg, data = validate_json_file(temp_path)
    if ok:
        return True, 'json', data, 'json'
    ok2, msg2, data2 = validate_xml_file(temp_path)
    if ok2:
        return True, 'xml', data2, 'xml'
    return False, f'Не удалось распознать как валидный JSON или XML. JSON: {msg}. XML: {msg2}', {}, ''

def list_all_files():
    res = {'json': [], 'xml': []}
    for folder, key in ((UPLOAD_DIR_JSON, 'json'), (UPLOAD_DIR_XML, 'xml')):
        if not os.path.exists(folder):
            continue
        for fn in os.listdir(folder):
            if fn.startswith('.'):
                continue
            path = os.path.join(folder, fn)
            if os.path.isfile(path):
                res[key].append({'name': fn, 'path': path})
    return res

def read_file_content(path: str):
    ok, msg, data = validate_json_file(path)
    if ok:
        return True, 'json', data
    ok2, msg2, data2 = validate_xml_file(path)
    if ok2:
        return True, 'xml', data2
    return False, 'invalid', {}
