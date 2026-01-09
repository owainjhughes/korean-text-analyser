import requests
from django.conf import settings
from .models import WordGrade

def get_and_save_word_grade(word):
    api_key = settings.API_KEY
    url = (
        f"https://krdict.korean.go.kr/api/search"
        f"?key={api_key}&q={word}&part=word&type_search=search"
    )
    response = requests.get(url)
    if response.status_code == 200:
        from xml.etree import ElementTree as ET
        root = ET.fromstring(response.content)
        item = root.find('item')
        if item is not None:
            grade = item.findtext('word_grade')
            if grade:
                # Save to database (update if exists)
                obj, created = WordGrade.objects.update_or_create(
                    word=word,
                    defaults={'grade': grade}
                )
                return grade
    return None

def get_word_grade(word):
    try:
        obj = WordGrade.objects.get(word=word)
        return obj.grade
    except WordGrade.DoesNotExist:
        return get_and_save_word_grade(word)