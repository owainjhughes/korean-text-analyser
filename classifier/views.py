from django.shortcuts import render, redirect
from .forms import RegisterForm
from konlpy.tag import Okt
from classifier.api_req import get_word_grade
import string

okt = Okt()

def index(request):
    result = []
    if request.method == 'POST':
        text = request.POST.get('text', '')

        # Tokenize and lemmatize with KoNLPy
        tokens = okt.pos(text, stem=True)

        seen = set()
        for word, tag in tokens:
            # Ignore punctuation and symbols
            if tag in ['Punctuation', 'Foreign', 'Number', 'Alpha', 'Symbol']:
                continue
            if word in string.punctuation:
                continue
            if word not in seen:
                seen.add(word)
                wordgrade = get_word_grade(word)
                result.append({'word': word, 'grade': wordgrade})

    return render(request, 'classifier/index.html', {'result': result})

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegisterForm()

    return render(request, 'classifier/register.html', {'form': form})

def about(request):
    return render(request, 'classifier/about.html')