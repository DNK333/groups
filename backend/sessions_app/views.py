from django.shortcuts import render, redirect

def home(request):
    if request.method == "POST":
        name = request.POST.get('name')
        
        request.session['username'] = name
        
        return redirect('home')
    
    username = request.session.get('username')
    
    return render(request, 'sessions_app/home.html', {'username' : username})

def forget(request):
    request.session.pop('username', None)
    
    return redirect('home')

