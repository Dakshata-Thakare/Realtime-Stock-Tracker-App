from django.shortcuts import render

# Create your views here.
def stockPicker(request):
    return render(request,'mainapp/stockpicker.html')

def stockTracker(request):
    return render(request,'mainapp/stocktracker.html')