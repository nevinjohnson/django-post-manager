# views.py

import json
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import Post, PostHistory
from django.conf import settings
import requests
import hashlib
from django.http import Http404
from django.contrib.auth.decorators import login_required

API_URL = settings.API_URL
API_TOKEN = settings.API_TOKEN

VISIBLE_COUNT = 10   # Tracks how many posts to show

def generate_hash(title, content, timestamp = None):
    # if not timestamp:
    #     timestamp = timezone.now() # just commented it out
    return str(hashlib.sha256(f'{title}{content}{timestamp}'.encode()).hexdigest())



api_version_hash = generate_hash('title', 'content')
local_version_hash = generate_hash(Post.title, Post.content)

# @login_required
def sync_from_api():
    headers = {
        'Authorization': f'Bearer {API_TOKEN}',
        'Accept': 'application/json',
    }

    response = requests.get(API_URL, headers=headers)
    raw_posts = response.json()
    # print(response.json())

    # if isinstance(raw_posts, dict) and 'data' in raw_posts:
    #     raw_posts = raw_posts['data']
    # elif isinstance(raw_posts, list) and isinstance(raw_posts[0], str):
    #     raw_posts = [json.loads(item) for item in raw_posts]
    # elif isinstance(raw_posts, list):
    #     raw_posts = []
        
    for item in raw_posts:
        # raw_posts = []
        external_id = item.get('post_id')
        title = item.get('title')
        content = item.get('body')

        if not external_id or not title or not content:
            continue
        
        timestamp = timezone.now()

        incoming_api_hash = generate_hash(title, content)

        post, created = Post.objects.get_or_create(external_id=external_id)

        current_local_hash = generate_hash(post.title, post.content) if not created else incoming_api_hash

         # CASE 1: New post from API

        if created:
            
            post.title = title
            post.content = content
            post.last_edited_by = 'API'
            post.last_edited_at = timezone.now()
            post.api_hash = incoming_api_hash
            post.local_hash = incoming_api_hash
            post.version_hash = incoming_api_hash
            post.deleted = False
            post.save()

        # CASE 2: Local post is deleted and API has NOT changed → skip it

        elif post.deleted and incoming_api_hash == post.api_hash:
            # print(f"[SKIP] Post '{external_id}' is deleted and unchanged in API.")
            continue

        # CASE 3: Local post is deleted but API version has changed → restore it

        elif post.deleted and incoming_api_hash != post.api_hash:
           
            PostHistory.objects.create(
                post=post,
                title=post.title,
                content=post.content,
                editor= post.last_edited_by or 'API',
                timestamp=post.last_edited_at or post.updated_at,
                version_hash=post.version_hash
            )

            post.title = title
            post.content = content
            post.last_edited_by = 'API'
            post.last_edited_at = timestamp
            post.api_hash = incoming_api_hash
            post.local_hash = incoming_api_hash
            post.version_hash = incoming_api_hash
            post.deleted = False
            post.save()

        # CASE 4: Post is not deleted and API version has changed → update it

        elif incoming_api_hash != post.api_hash:
            PostHistory.objects.create(
                post=post,
                title=post.title,
                content=post.content,
                editor= post.last_edited_by or 'API',
                timestamp=post.last_edited_at or post.updated_at,
                version_hash=post.version_hash
            )

            post.title = title
            post.content = content
            post.last_edited_by = 'API'
            post.last_edited_at = timestamp
            post.api_hash = incoming_api_hash
            post.local_hash = incoming_api_hash
            post.version_hash = incoming_api_hash
            post.save()

        # CASE 5: Post is not changed in API but locally edited → skip

        elif incoming_api_hash == post.api_hash and current_local_hash != post.local_hash:
            continue
        
        else:
            continue

@login_required
def view_posts(request):
    count = request.session.get('visible_posts', VISIBLE_COUNT)
    if isinstance(count,str):
        count=int(count)   #just edited this three lines before it was only count = int(request.session.get('visible_posts', VISIBLE_COUNT))
    all_posts = Post.objects.order_by('-updated_at')
    posts = all_posts[:count] 
    #print(posts)
    posts= Post.objects.filter(deleted=False) 

    return render(request, 'posts/index.html', {
        'mode': 'list',
        'posts': posts,
        'count': count,
        'total_available': all_posts.count(),
    })

@login_required
def sync_more_posts(request):
    if request.method == 'POST':
        prev_count = request.session.get('visible_posts', VISIBLE_COUNT)
        request.session['visible_posts'] = prev_count + VISIBLE_COUNT

        sync_from_api()
        return redirect('view_posts')
    return redirect('view_posts')

def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == 'POST':
        new_title = request.POST.get('title')
        new_body  = request.POST.get('body')
        # previous_editor = request.user.username
        if not new_title or not new_body:
           return render(request, 'posts/index.html', {
               'mode': 'edit',
               'post': post,
               'error_message': 'Title and content cannot be empty.',
           })

        PostHistory.objects.create(
            post      = post,
            title     = post.title,
            content   = post.content,
            editor    = post.last_edited_by,
            timestamp = post.last_edited_at or post.updated_at,
            version_hash = post.version_hash
        )

        post.title = new_title
        post.content = new_body
        post.last_edited_by = request.user.username if request.user.is_authenticated else "UNKNOWN"
        post.last_edited_at = timezone.now()
        post.local_hash = generate_hash(new_title, new_body)
        post.version_hash = generate_hash(new_title, new_body)
        post.save()

        return redirect('view_posts')

    return render(request, 'posts/index.html', {'mode': 'edit', 'post': post})

def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        # print(post.deleted)
        post.deleted=True
        post.save()
        return redirect('view_posts')
    return render(request, 'posts/index.html', {'mode': 'delete', 'post': post})

def view_single_post(request, post_id):
    try:
        post = get_object_or_404(Post, id=post_id, deleted = False)
    except Post.DoesNotExist:
        raise Http404("Post not found or has been deleted.")

    history = post.posthistory_set.all().order_by('-timestamp')
    return render(request, 'posts/index.html', {
        'mode': 'detail',
        'post': post,
        'history': history
    })

@login_required
def post_list(request):
    # posts = Post.objects.all().prefetch_related('posthistory_set')
    posts = Post.objects.filter(deleted = False).order_by('post_id')
    return render(request, 'post/post_list.html', {'posts': posts})
