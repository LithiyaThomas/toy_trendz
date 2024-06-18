from django.db import models


class Brand(models.Model):
    name = models.CharField(max_length=100)
    is_deleted = models.BooleanField(default=False)

    def soft_delete(self, *args, **kwargs):
        self.is_deleted = True
        self.save()

    def restore(self):
        self.is_deleted = False
        self.save()

    def permanent_delete(self):
        super(Brand, self).delete()

    def __str__(self):
        return self.name
