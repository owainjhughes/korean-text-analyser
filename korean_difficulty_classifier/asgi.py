<<<<<<< HEAD
=======
"""
ASGI config for korean_difficulty_classifier project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

>>>>>>> 225454725c60328a89aae8f7f61e4c0200fd66d3
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'korean_difficulty_classifier.settings')

application = get_asgi_application()
