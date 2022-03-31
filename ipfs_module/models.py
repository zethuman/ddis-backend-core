from django.db import models
from django.utils import timezone

# Create your models here.


class ImagesManager(models.Manager):
    use_in_migrations = True

    def find_image_by_file_hash(self, file_hash):
        return self.filter(file_hash=file_hash)

    def find_image_by_imagename_tag(self, imagename, tag):
        return self.filter(imagename=imagename, tag=tag, pin=True)

    def get_image_by_imagename_tag(self, imagename, tag):
        return self.get(imagename=imagename, tag=tag, pin=True)

    def get_ipfs_hash_by_imagename_tag(self, imagename, tag):
        return self.get(imagename=imagename, tag=tag, pin=True).ipfs_hash

    def delete_image_id(self, id):
        image = self.filter(id=id)
        image.delete()
        return image

    def create_image(self, name, tag, ipfs_hash, file_hash, pin, size):
        image = self.create(
            imagename=name, tag=tag, ipfs_hash=ipfs_hash, file_hash=file_hash, pin=pin, size=size)
        image.save()


class Images(models.Model):
    imagename = models.CharField('Image name', max_length=500)
    tag = models.CharField('Image tag', max_length=200)
    ipfs_hash = models.CharField('Hash of image in ipfs', max_length=100,
                                 default='', blank=True, null=False)
    file_hash = models.CharField('Hash of image local', max_length=100,
                                 default='', blank=True, null=False)
    size = models.BigIntegerField('Size of image', default=0)
    changed = models.DateTimeField(
        'Date pushed', default=timezone.now)
    pin = models.BooleanField('Image pin status', default=False)

    objects = ImagesManager()

    class Meta:
        verbose_name = 'Image'
        verbose_name_plural = 'Images'
        constraints = [
            models.UniqueConstraint(
                fields=['ipfs_hash'], name='unique_hash_value')
        ]

    def __str__(self):
        return self.ipfs_hash

    def to_json(self):
        return {
            "id": self.id,
            "name": self.imagename,
            "hash": self.ipfs_hash
        }
