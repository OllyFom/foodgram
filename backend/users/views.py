# from django.shortcuts import render, redirect
# from .forms import ProfileEditForm

# def profile(request):
#     if request.method == 'POST':
#         form = ProfileEditForm(request.POST, instance=request.user)
#         if form.is_valid():
#             form.save()
#             return redirect('users:profile')
#     else:
#         form = ProfileEditForm(instance=request.user)
#     return render(request, 'users/profile.html', {'form': form})