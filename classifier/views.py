
from django.shortcuts import render, redirect
from .forms import RegisterForm
from konlpy.tag import Okt
from .dictionary_utils import load_cleaned_kengdic, WORD_GLOSS, WORD_LEVEL
from classifier.api_req import get_word_grade

okt = Okt()

def index(request):
    result = {}
    if request.method == 'POST':
        text = request.POST.get('text', '')

        # Tokenize and lemmatize with KoNLPy
        # e.g. [('정치', 'Noun'), ('는', 'Josa'), ...]
        tokens = okt.pos(text, stem=True)

        seen = set()

        for word in tokens:
            get_word_grade(word[0])

    return render(request, 'classifier/index.html', {'result': result})

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})