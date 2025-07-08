# Example function to get word grade from krdict OpenAPI
import os
from dotenv import load_dotenv
import requests

load_dotenv()

def get_word_grade(word):
    api_key = os.getenv("api_key")
    url = (
        f"https://krdict.korean.go.kr/api/search"
        f"?key={api_key}&q={word}&part=word&type_search=search")
    response = requests.get(url)
    if response.status_code == 200:
        from xml.etree import ElementTree as ET
        root = ET.fromstring(response.content)
        # Find the first entry and get the grade
        item = root.find('item')
        if item is not None:
            grade = item.findtext('word_grade')
            print(f"Word: {word}, Grade: {grade}")
            return grade
    return None