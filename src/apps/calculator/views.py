from django.shortcuts import render


def calculator_index(request):
    return render(request, "calculator/index.html")
