# models.py

from django.db import models
import hashlib
from django.utils import timezone

class Post(models.Model):
    external_id    = models.IntegerField(unique=False , null=True , blank = True)
    title          = models.CharField(max_length=255)
    content        = models.TextField()
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)
    last_edited_by = models.CharField(max_length=50, default='API')
    last_edited_at = models.DateTimeField(null=True, blank=True)
    local_hash      = models.CharField(max_length=64, editable=False, blank=True)
    api_hash = models.CharField(max_length=255, editable=False, blank=False)
    version_hash = models.CharField(max_length=64, blank=True, null=True)
    deleted= models.BooleanField(default=False)


    def save(self, *args, **kwargs):
            # Auto-generate external_id if not set
        if self.external_id is None:
            min_id = Post.objects.filter(external_id__lt=0).order_by('external_id').first()
            self.external_id = (min_id.external_id - 1) if min_id else -1

         # Update timestamp manually to ensure it's used in hash
        self.updated_at = timezone.now()

        hash_input = f"{self.title}{self.content}{self.updated_at}".encode('utf-8')
        generated_hash = hashlib.sha256(hash_input).hexdigest()

        self.local_hash = generated_hash
        self.version_hash = generated_hash

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class PostHistory(models.Model):
    post      = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='posthistory_set')
    title     = models.CharField(max_length=255)
    content   = models.TextField()
    editor    = models.CharField(max_length=50)
    timestamp = models.DateTimeField()
    version_hash = models.CharField(max_length=64, editable=False, blank=True)

    def save(self, *args, **kwargs):
        hash_input = f"{self.title}{self.content}{self.timestamp}".encode('utf-8')
        self.version_hash = hashlib.sha256(hash_input).hexdigest()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"History of '{self.post.title}' @ {self.timestamp}"

