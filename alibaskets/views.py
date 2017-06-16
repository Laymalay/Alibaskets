# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render_to_response, render, redirect
from django.http import HttpResponse, Http404
from django.views.generic import ListView, CreateView
from django.core.urlresolvers import reverse
from django.views import generic
from .models import Basket, Task
from django.shortcuts import render, get_object_or_404
from .forms import BasketForm, ValidationError, BasketEditForm, TaskForm
from alirem.alirm import Alirem
from alirem.basket_handler import BasketHandler
from notifications.signals import notify
from django.contrib import messages
import shutil
from alirem import getsize
from alirem.logger import DefaultLogger
from celery.task.control import inspect
from alibaskets.tasks import *
from celery.result import AsyncResult
import json
import pprint
from django.forms.models import model_to_dict


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


def basket_can_be_cleared(basket_pk):
    basket = get_object_or_404(Basket, pk=basket_pk)
    update_tasks()
    # print Task.objects.all()
    tasks_with_this_basket_progress = Task.objects.filter(basket_path=basket.path).filter(status='PROGRESS')
    tasks_with_this_basket_pending = Task.objects.filter(basket_path=basket.path).filter(status='PENDING')
    # print tasks_with_this_basket_progress, tasks_with_this_basket_pending
    if str(tasks_with_this_basket_progress) == '<QuerySet []>' \
         and str(tasks_with_this_basket_pending) == '<QuerySet []>':
        return True
    return False

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
                if taskform.cleaned_data['action'] == 'RM':
                    if  os.path.exists(taskform.cleaned_data['path_to_removing_file']):
                        task = taskform.save()
                        task.basket_path = basket.path
                        task.progress = 0
                        check_flags = BasketHandler(path=task.path_to_removing_file,
                                                    logger=DefaultLogger(),
                                                    basket_path=basket.path,
                                                    is_dir=(task.params == 'd'),
                                                    is_recursive=(task.params == 'r'))
                        try:
                            check_flags.check_flags()
                            job = remove.apply_async([task.path_to_removing_file,
                                                      basket.path,
                                                      (task.params == 'd'),
                                                      (task.params == 'r'),
                                                      task.is_force])
                            task.task_id = job.id
                            task.status = job.status
                            task.save()
                        except Exception as e:
                            messages.add_message(request, messages.ERROR, str(type(e)))
                            task.status = str(type(e))
                            task.save()
                    else:
                        messages.add_message(request, messages.ERROR, "This path is not exists")
                    return redirect('alibaskets:basket_detail', pk=basket.pk)
                elif taskform.cleaned_data['action'] == 'RS':
                    task = taskform.save()
                    is_merge = (task.params == 'm')
                    is_replace = (task.params == 'r')
                    if  os.path.exists(os.path.join(basket.path, task.restorename)):
                        restorer = Alirem()
                        for obj in restorer.get_basket_list(basket.path):
                            if obj.name == task.restorename:
                                restore_path = obj.rm_path
                        if os.path.exists(restore_path) and not is_merge and not is_replace:
                            messages.add_message(request, messages.ERROR,
                                                 "Name conflict, use merge or replace param")
                        else:
                            job = restore.apply_async([task.restorename,
                                                       basket.path,
                                                       is_merge,
                                                       is_replace,
                                                       task.is_force])
                            task.task_id = job.id
                            task.basket_path = basket.path
                            task.status = job.status
                            task.save()
                    else:
                        messages.add_message(request, messages.ERROR,
                                             "Could't find such file in basket")
                    return redirect('alibaskets:basket_detail', pk=basket.pk)
        if request.POST.get("update_button") is not None:
            if form_edit_basket.is_valid():
                basket.mode = form_edit_basket.cleaned_data['mode']
                basket.delta_time = form_edit_basket.cleaned_data['delta_time']
                basket.max_size = form_edit_basket.cleaned_data['max_size']
                basket.save()
                basket_handler = Alirem()
                if basket_can_be_cleared(pk):
                    print 'CAN'
                    basket_handler.check_basket_for_cleaning(mode=basket.get_mode_display(),
                                                             basket_path=basket.path,
                                                             time=iso8601(basket.delta_time),
                                                             size=basket.max_size)
                return redirect('alibaskets:basket_detail', pk=basket.pk)
    else:
        taskform = TaskForm()
        form_edit_basket = BasketEditForm(initial=
                                          {'mode':basket.mode,
                                           'delta_time':basket.delta_time,
                                           'max_size':basket.max_size})
        basket_handler = Alirem()
        if os.path.exists(basket.path):
            list_of_objects_in_basket = basket_handler.get_basket_list(basket.path)
            basket_size = getsize.get_size(basket.path) / 1000000.0
            basket_size_in_proc = (int)((basket_size*100.0)/basket.max_size)
            for obj in list_of_objects_in_basket:
                obj.disappearances_time = obj.time + basket.delta_time
        else:
            list_of_objects_in_basket = None
            basket_size_in_proc = 0
        return render(request, 'baskets/basket_detail.html',
                      {'basket': basket,
                       'form' : taskform,
                       'form_basket': form_edit_basket,
                       'list_of_objects': list_of_objects_in_basket,
                       'basket_size_in_proc': basket_size_in_proc})

def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)
    task_dict = model_to_dict(task)
    task_dict['action'] = task.get_action_display()
    task_dict['params'] = task.get_params_display()
    return render(request, 'baskets/task_detail.html', {'task' : task_dict})

def basket_list(request):
    baskets = Basket.objects.all()
    tasks = Task.objects.all()
    for task in tasks:
        if task.task_id is not None:
            if task.action == 'RM':
                result = AsyncResult(task.task_id, app=remove)
                task.name = os.path.basename(task.path_to_removing_file)
            elif task.action == 'RS':
                result = AsyncResult(task.task_id, app=restore)
                task.name = task.restorename
            if  result.info is not None:
                task.progress = result.info['process_percent']
            else:
                task.progress = 100
            task.status = result.status
            task.save()
    return render(request, 'baskets/basket_list.html',
                  {'baskets': baskets, 'tasks': reversed(tasks)})


def update_tasks():
    tasks = Task.objects.all()
    for task in tasks:
        if task.task_id is not None:
            if task.action == 'RM':
                result = AsyncResult(task.task_id, app=remove)
                task.name = os.path.basename(task.path_to_removing_file)
            elif task.action == 'RS':
                result = AsyncResult(task.task_id, app=restore)
                task.name = task.restorename
            if  result.info is not None:
                task.progress = result.info['process_percent']
            else:
                task.progress = 100
            task.status = result.status
            task.save()

def task_status(request,pk):
    task = get_object_or_404(Task, pk=pk)
    tasks = Task.objects.all()

    # for taska in tasks:
    #     if taska.action == 'RM':
    #         res = AsyncResult(task.task_id, app=remove)
    #     elif taska.action == 'RS':
    #         res = AsyncResult(task.task_id, app=restore)
    #     if res.info is not None:
    #         taska.progress = res.info['process_percent']
    #     taska.status = res.status
    #     taska.save()
    if task.task_id is not None:
        if task.action == 'RM':
            result = AsyncResult(task.task_id, app=remove)
        elif task.action == 'RS':
            result = AsyncResult(task.task_id, app=restore)
        if result.info is None:
            data = 100
        else:
            data = result.info['process_percent']
    else:
        data = 0
    json_data = json.dumps(data)
    return HttpResponse(json_data)


def iso8601(value):
    seconds = value.total_seconds()
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    days, hours, minutes = map(int, (days, hours, minutes))
    seconds = round(seconds, 6)
    date = ''
    if days:
        date = '%sD' % days
    time = u'T'
    bigger_exists = date or hours
    if bigger_exists:
        time += '{:02}H'.format(hours)
    bigger_exists = bigger_exists or minutes
    if bigger_exists:
      time += '{:02}M'.format(minutes)
    if seconds.is_integer():
        seconds = '{:02}'.format(int(seconds))
    else:
        seconds = '%09.6f' % seconds
    # remove trailing zeros
    # seconds = seconds.rstrip('0')
    time += '{}S'.format(seconds)
    return u'P' + date + time
