# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render_to_response, render, redirect
from django.http import HttpResponse, Http404
from alibaskets.models import Basket
from django.views.generic import ListView, CreateView
from django.core.urlresolvers import reverse
from django.views import generic
from .models import Basket, Task
from django.shortcuts import render, get_object_or_404
from .forms import BasketForm, ValidationError, BasketEditForm, TaskForm
from alirem.alirm import Alirem
from notifications.signals import notify
from django.contrib import messages
import shutil
from alirem import getsize


def basket_new(request):
    if request.method == "POST":
        form = BasketForm(request.POST)
        if form.is_valid():
            basket = form.save()
            new_basket = Alirem()
            new_basket.create_basket(basket.path)
            basket.save()
            return redirect('alibaskets:basket_list')

        else:
            messages.add_message(request, messages.ERROR, "This path is already exists")
            form = BasketForm()
            return render(request, 'baskets/basket_edit.html', {'form': form})

    else:
        form = BasketForm()
        return render(request, 'baskets/basket_edit.html', {'form': form})

def remove_basket(request, pk):
    basket = get_object_or_404(Basket, pk=pk)
    name = basket.name
    shutil.rmtree(basket.path)
    basket.delete()
    return render(request, 'baskets/remove_basket.html', {'name': name})

def basket_detail(request, pk):
    basket = get_object_or_404(Basket, pk=pk)
    if request.method == "POST":
        taskform = TaskForm(request.POST)
        form_edit_basket = BasketEditForm(request.POST,
                                          initial={'mode':basket.mode,
                                                   'delta_time':basket.delta_time,
                                                   'max_size':basket.max_size})
        if request.POST.get("create_task_button") is not None:
            if taskform.is_valid():
                task = taskform.save()
                if task.get_action_display() == 'remove':
                    remover = Alirem()
                    try:
                        task.is_alive = True
                        remover.remove(path=task.path_to_removing_file,
                                       basket_path=basket.path,
                                       is_dir=(task.params == 'd'),
                                       is_recursive=(task.params == 'r'))
                        task.is_alive = False
                    except Exception as e:
                        print e
                        messages.add_message(request, messages.ERROR, "Invalid form")
                    return redirect('alibaskets:basket_detail', pk=basket.pk)
                elif task.get_action_display() == 'restore':
                    restorer = Alirem()
                    if not restorer.restore(restorename=task.restorename, basket_path=basket.path,
                                            is_merge=(task.params == 'm'),
                                            is_replace=(task.params == 'r')):
                        messages.add_message(request, messages.ERROR, "This path is not exists")
                    return redirect('alibaskets:basket_detail', pk=basket.pk)
        if request.POST.get("update_button") is not None:
            if form_edit_basket.is_valid():
                basket.mode = form_edit_basket.cleaned_data['mode']
                basket.delta_time = form_edit_basket.cleaned_data['delta_time']
                basket.max_size = form_edit_basket.cleaned_data['max_size']
                basket.save()
                return redirect('alibaskets:basket_detail', pk=basket.pk)
    else:
        taskform = TaskForm()
        form_edit_basket = BasketEditForm(initial=
                                          {'mode':basket.mode,
                                           'delta_time':basket.delta_time,
                                           'max_size':basket.max_size})
        basket_handler = Alirem()
        basket_handler.check_basket_for_cleaning(mode=basket.get_mode_display(),
                                                 basket_path=basket.path,
                                                 time=iso8601(basket.delta_time),
                                                 size=basket.max_size)
        list_of_objects_in_basket = basket_handler.get_basket_list(basket.path)
        basket_size= getsize.get_size(basket.path) / 1000000.0
        basket_size_in_proc = (int)(basket_size/basket.max_size*100.0)
        for obj in list_of_objects_in_basket:
            print obj
            obj.disappearances_time = obj.time + basket.delta_time
        return render(request, 'baskets/basket_detail.html',
                      {'basket': basket,
                       'form' : taskform,
                       'form_basket': form_edit_basket,
                       'list_of_objects': list_of_objects_in_basket,
                       'basket_size_in_proc': basket_size_in_proc})


def basket_list(request):
    baskets = Basket.objects.all()
    tasks = Task.objects.all()
    return render(request, 'baskets/basket_list.html', {'baskets': baskets, 'tasks':tasks})

def iso8601(value):
    # split seconds to larger units
    seconds = value.total_seconds()
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    days, hours, minutes = map(int, (days, hours, minutes))
    seconds = round(seconds, 6)

    ## build date
    date = ''
    if days:
        date = '%sD' % days

    ## build time
    time = u'T'
    # hours
    bigger_exists = date or hours
    if bigger_exists:
        time += '{:02}H'.format(hours)
    # minutes
    bigger_exists = bigger_exists or minutes
    if bigger_exists:
      time += '{:02}M'.format(minutes)
    # seconds
    if seconds.is_integer():
        seconds = '{:02}'.format(int(seconds))
    else:
        # 9 chars long w/leading 0, 6 digits after decimal
        seconds = '%09.6f' % seconds
    # remove trailing zeros
    # seconds = seconds.rstrip('0')
    time += '{}S'.format(seconds)
    return u'P' + date + time
