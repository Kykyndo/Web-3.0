from django.db import models

# No persistent models required — files are used as storage.
class Dummy(models.Model):
    created = models.DateTimeField(auto_now_add=True)
