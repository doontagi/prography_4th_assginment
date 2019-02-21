from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from .forms import NewTopicForm,PostForm
from .models import Board, Topic, Post
from django.views.generic import UpdateView,DeleteView
from django.utils import timezone
from django.urls import reverse_lazy


def home(request):
    boards = Board.objects.all()
    return render(request, 'boardd/index.html', {'boards': boards})
def board_topics(request, pk):
    board = get_object_or_404(Board, pk=pk)
    return render(request, 'boardd/topics.html', {'board': board})
def new_topic(request, pk):
    board = get_object_or_404(Board, pk=pk)
    user = User.objects.first()  # TODO: get the currently logged in user
    if request.method == 'POST':
        form = NewTopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.board = board
            topic.starter = user
            topic.save()
            post = Post.objects.create(
                message=form.cleaned_data.get('message'),
                topic=topic,
            )
            return redirect('board_topics', pk=board.pk)  # TODO: redirect to the created topic page
    else:
        form = NewTopicForm()
    return render(request, 'boardd/new_topic.html', {'board': board, 'form': form})
def topic_posts(request, pk, topic_pk):
    topic = get_object_or_404(Topic, board__pk=pk, pk=topic_pk)
    return render(request, 'boardd/topic_posts.html', {'topic': topic})
def reply_topic(request, pk, topic_pk):
    topic = get_object_or_404(Topic, board__pk=pk, pk=topic_pk)
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.topic = topic
            post.save()
            return redirect('topic_posts', pk=pk, topic_pk=topic_pk)
    else:
        form = PostForm()
    return render(request, 'boardd/reply_topic.html', {'topic': topic, 'form': form})
class PostUpdateView(UpdateView):
    model = Post
    fields = ('message', )
    template_name = 'boardd/edit_post.html'
    pk_url_kwarg = 'post_pk'
    context_object_name = 'post'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.updated_at = timezone.now()
        post.save()
        return redirect('topic_posts', pk=post.topic.board.pk, topic_pk=post.topic.pk)
class PostDeleteView(DeleteView):
    model = Post
    pk_url_kwarg = 'post_pk'
    success_url = '/'
