from django.db import models
from django.utils import timezone

# Create your models here.


class Images(models.Model):
    imagename = models.CharField('Image name', max_length=500)
    tag = models.CharField('Image tag', max_length=200)
    hash = models.CharField('Hash of image', max_length=100,
                            default='', blank=True, null=False)
    size = models.BigIntegerField('Size of image', default=0)
    changed = models.DateTimeField(
        'Date pushed', default=timezone.now)

    class Meta:
        verbose_name = 'Image'
        verbose_name_plural = 'Images'
        constraints = [
            models.UniqueConstraint(fields=['hash'], name='unique_hash_value')
        ]

    def __str__(self):
        return self.hash

    def to_json(self):
        return {
            "name": self.imagename,
            "hash": self.hash
        }
