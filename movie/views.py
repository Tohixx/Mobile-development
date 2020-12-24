from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, View
from django.contrib import messages
from django.core.files.storage import default_storage
from .form import MovieForm, CollageForm
from .models import Movie, Collage
import json
from itertools import islice
import matplotlib.pyplot as plt
import numpy as np
import urllib, base64
import io


# Create your views here.

def main(request):
    movies = Movie.objects.all()

    try:
        if request.GET['filter']:
            movies = Movie.objects.filter(title__icontains=request.GET['filter'])
    except:
        context = {'movies': movies}
        return render(request, 'base.html', context)

    context = {'movies': movies}
    return render(request, 'base.html', context)


def add_movie(request):
    form = MovieForm()
    if request.method == 'POST':
        form = MovieForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('main')

        return redirect('main')
    context = {'form': form}

    return render(request, 'movie/add_movie.html', context)


class MovieDetailView(DetailView):
    model = Movie
    template_name = 'movie/movie_card.html'
    slug_field = 'imdbID'


def delete_movie(request, pk):
    post = Movie.objects.get(id=pk)
    if request.method == 'GET':
        post.delete()
        return redirect('/')


def display_graph(request):
    x = np.arange(-2*np.pi, 2*np.pi, 0.1)
    y = list(np.sin(x))
    plt.title(f'y=sin(x)')
    plt.grid(True)
    plt.plot(x, y)

    fig = plt.gcf()
    fig.set_size_inches(3, 3)
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = urllib.parse.quote(string)

    context = {'data': uri}
    fig.clear()
    return render(request, 'movie/graph.html', context)


def display_diagram(request):
    x = 20
    y = 25
    z = 55
    try:
        if request.GET['x'] and request.GET['y'] and request.GET['z']:
            x = int(request.GET['x'])
            y = int(request.GET['y'])
            z = int(request.GET['z'])

    except:
        x = 25
        y = 20
        z = 55

    size_of_groups = [x, y, z]
    colors = ['yellow', 'green', 'blue']
    labels = [f'x = {x}', f'y= {y}', f'z = {z}']
    plt.pie(size_of_groups, colors=colors, labels=labels)
    my_circle = plt.Circle((0, 0), 0.7, color='white')
    p = plt.gcf()
    p.gca().add_artist(my_circle)
    fig = plt.gcf()
    fig.set_size_inches(3, 3)
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = urllib.parse.quote(string)

    context = {'data': uri, 'x':x, 'y':y, 'z':z }
    fig.clear()
    return render(request, 'movie/diagram.html', context)

def chunk(iterable, size):
    it = iter(iterable)
    item = list(islice(it, size))
    while item:
        yield item
        item = list(islice(it, size))


def collage(request):
    form = CollageForm()
    if request.method == 'POST':
        form = CollageForm(request.POST, request.FILES)
        obj = Collage.objects.first()
        if form.is_valid():
            file = request.FILES['image']
            file_name = default_storage.save(file.name, file)
            file_url = default_storage.url(file_name)
            obj.list_obj['image'].append(file_url)
            obj.save()

    obj = Collage.objects.first()
    list_default = obj.list_obj['image']
    if len(list_default) % 9 != 0:
        num = 9 - len(list_default) % 9
        for i in range(0, num):
            list_default.append('')

    out_image = list(chunk(list_default, 9))

    context = {'form': form, 'out_image': out_image}

    return render(request, 'movie/collage.html', context)

def clear_collage(request):
    obj = Collage.objects.first()
    obj.list_obj = {'image': []}
    obj.save()

    return redirect('collage')