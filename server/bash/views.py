from django.shortcuts import render
from django.views.generic import TemplateView
import subprocess
from angelweb.forms import BamForm
import time
from django.http import HttpResponseRedirect, HttpResponseBadRequest
import logging

import json

LOG = logging.getLogger(__name__)

def verify_command(value):
    value = str(value)
    
    bash_string = 'python verifier.py -url ' + value

    try:
        bash = subprocess.check_output([bash_string], shell=True)
        bash = bash.decode()
        print(bash)
    except subprocess.CalledProcessError as e:
        bash = e.output
        print(bash)

    return bash


def bash_view(request):
    template = "home.html"
    form =BamForm()
    context = {'form': form}
    if request.user.is_authenticated:
        current_email=request.user.email
        print(current_email)
        LOG.debug(current_email)
    else:
        current_email = ''
    if request.method == 'POST':
        form = BamForm(request.POST)
        
        if form.is_valid():

            bash_out = verify_command(form.cleaned_data['url_link'])
            one = bash_out.split('\n')
            count=0
            for onep in one:
                if 'errors' in onep:
                    count+=1
            if count ==0:
                success = 'CONGRATULATIONS! The review finished and your beacon has successfully passed the tests.'
            else:
                success = 'ERRORS FOUND! Your beacon has some errors, please review them and verify it back.'


   
            context = {
                'url_link': form.cleaned_data['url_link'],
                'bash_out': one,
                'success': success,
                'form': form

            }


            return render(request, 'base.html', context)

            
    
    return render(request, template, context)
