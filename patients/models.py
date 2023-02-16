from django.db import models

# Create your models here.

class Patient(models.Model):
    name = models.CharField(max_length=100)
    symptoms = models.TextField()
    results = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']