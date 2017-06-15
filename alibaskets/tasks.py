# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task, task
import time
from alirem.alirm import Alirem
import os
from alirem.getsize import get_size
import threading
from celery.signals import worker_process_init
from multiprocessing import current_process

def update_progress(file_name_in_basket, total_size):
    percent = int((get_size(file_name_in_basket)*100.0)/(total_size+1))
    return percent




# @worker_process_init.connect
# def fix_multiprocessing(**kwargs):
#     try:
#         current_process()._authkey
#         current_process()._daemonic
#         current_process()._tempdir
        
#     except AttributeError:
#         current_process()._authkey = {'fix': '/mp'}
#         current_process()._daemonic = {'fix': '/mp'}
#         current_process()._tempdir = {'fix': '/mp'}


@shared_task(bind=True)
def remove(self, path_to_removing_file, basket_path, is_dir, is_recursive):
    total_size = get_size(path_to_removing_file)

    def update(path_to_removing_file, basket_path, is_dir, is_recursive):
        remover = Alirem()
        remover.remove(path=path_to_removing_file,
                       basket_path=basket_path,
                       is_dir=is_dir,
                       is_recursive=is_recursive)
    t = threading.Thread(target=update, args=(path_to_removing_file, basket_path,
                                              is_dir, is_recursive))
    t.start()
    progress = 0
    file_name_in_basket = os.path.join(basket_path, os.path.basename(path_to_removing_file))
    while t.is_alive():
        time.sleep(0.1)
        if os.path.exists(file_name_in_basket):
            progress = update_progress(file_name_in_basket=file_name_in_basket,
                                       total_size=total_size)
        self.update_state(state='PROGRESS',
                          meta={'process_percent': progress})



@shared_task(bind=True)
def restore(self, restorename, basket_path, is_merge, is_replace):
    total_size = get_size(os.path.join(basket_path, restorename))
    restorer = Alirem()
    restore_path = None
    for obj in restorer.get_basket_list(basket_path):
        if obj.name == restorename:
            restore_path = obj.rm_path

    def update(restorename, basket_path, is_merge, is_replace):
        restorer = Alirem()
        restorer.restore(restorename=restorename,
                         basket_path=basket_path,
                         is_merge=is_merge,
                         is_replace=is_replace)
    t = threading.Thread(target=update, args=(restorename, basket_path, is_merge, is_replace))
    t.start()
    progress = 0
    while t.is_alive():
        time.sleep(0.1)
        if os.path.exists(restore_path):
            progress = update_progress(file_name_in_basket=restore_path,
                                       total_size=total_size)
        self.update_state(state='PROGRESS',
                          meta={'process_percent': progress})

