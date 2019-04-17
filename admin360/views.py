from django.shortcuts import render

# Create your views here.

# def loginCheck(request):
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         password = request.POST.get('password')
#         user = authenticate(request, username=username, password=password)
#         if user and user.is_staff is False:
#             login(request, user)
#             return redirect('home')
#         elif user and user.is_staff is True:
#             login(request, user)
#             return redirect('admin')
#         else:
#             messages.add_message(request, messages.INFO, 'Wrong User Name Or Password')
#             return redirect('loginView')
#     messages.add_message(request, messages.INFO, 'You Have To Login First')
#     return redirect('loginView')
