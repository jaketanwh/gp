from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render
import time

def hello(request):
    return HttpResponse("Hello world！ This is my first trial. [jaketanwhh的笔记]")

def current_time(request):
    if request.method == "POST":
        print('POST 请求')
        a = request.POST['a']
        b = request.POST.get('b')
        name_dict = {'twz': 'Love python and Django', 'zqxt': 'I am teaching Django'}
        response = JsonResponse(name_dict)
        response["Access-Control-Allow-Headers"] = "Origin,Content-Type,Cookie,Accept,Token"
        return response
        #return HttpResponse("Current time is: " + time.strftime('%Y-%m-%d %H:%M:%S'))
    else:
        print("GET 请求")
        a = request.GET.get('a')
        b = request.GET.get('b')
        name_dict = {'twz': 'Love python and Django', 'zqxt': 'I am teaching Django'}
        response = JsonResponse(name_dict)
        #response["Access-Control-Allow-Headers"] = "Origin,Content-Type,Cookie,Accept,Token"
        return response
        #return HttpResponse("Current time is: "+time.strftime('%Y-%m-%d %H:%M:%S'))