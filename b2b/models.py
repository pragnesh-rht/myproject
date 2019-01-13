from datetime import timedelta

from PIL import Image
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify


class Post(models.Model):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=140, null=False)
    content = models.TextField()

    date_posted = models.DateTimeField(auto_now_add=True)
    date_end = models.DateTimeField(default=timezone.now() + timedelta(days=2), verbose_name='End Date')

    initial_price = models.IntegerField(default=100)
    current_price = models.IntegerField(default=0, verbose_name='Current Bid')

    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('bid-update', kwargs={'pk': self.pk})

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        Post.current_price = self.initial_price
        super().save(force_insert, force_update, using, update_fields)


def get_image_filename(instance, filename):
    title = instance.post.id
    slug = slugify(title)
    return "post_images/%s/%s" % (slug, filename)


class Images(models.Model):
    post = models.ForeignKey(Post, default=None, on_delete=models.CASCADE)
    post_image = models.ImageField(default='default_post_image.jpg', upload_to=get_image_filename,
                                   verbose_name='Select an Image')

    def make_square(self, min_size=256, fill_color=(0, 0, 0, 0)):
        x, y = self.size
        size = max(min_size, x, y)
        new_im = Image.new('RGB', (size, size), fill_color)
        new_im.paste(self, (int((size - x) / 2), int((size - y) / 2)))
        return new_im

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        img = Image.open(self.post_image.path)

        img = Images.make_square(img)

        if img.height > 600 or img.width > 600:
            output_size = (600, 600)
            img.thumbnail(output_size)
            img.save(self.post_image.path)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.post.title


class Bidder(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    prices = models.IntegerField(null=False)
    date_bid = models.DateTimeField(default=timezone.now)
    bid_author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.post.title

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        postObj = self.post
        postObj.current_price = self.prices
        postObj.save()
        super().save(force_insert, force_update, using, update_fields)
