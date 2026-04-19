from django.db import models
from django.contrib.auth.models import User


class Department(models.Model):
    name           = models.CharField(max_length=100, unique=True)
    description    = models.TextField(blank=True, null=True)
    specialisation = models.TextField(blank=True, null=True)
    head_user      = models.ForeignKey(
                         User,
                         on_delete=models.SET_NULL,
                         null=True,
                         blank=True,
                         related_name='headed_departments'
                     )
    is_active      = models.BooleanField(default=True)
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'department'

    def __str__(self):
        return self.name