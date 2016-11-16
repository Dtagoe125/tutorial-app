from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from models import Page, Category
from forms import CategoryForm, PageForm, UserForm, UserProfileForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from datetime import datetime

# Create your views here.

def index(request):
	request.session.set_test_cookie()
	if request.session.test_cookie_worked():
		print ">>>> TEST COOKIE WORKED!"
		request.session.delete_test_cookie()

	# Query the database for a list of ALL categories currently stored.
	# Order the categories by no. likes in descending order.
	# Retrieve the top 5 only - or all if less than 5.
	# Place the list in our context_dict dictionary which will be passed to the template engine.
	category_list = Category.objects.order_by('-likes')[:5]
	context_dict = {'categories': category_list}
	page_list = Page.objects.order_by('-views')[:5]
	context_dict = {'categories' : category_list,
					'pages' : page_list 
					}
	# Render the response nd send it back!
	return render(request, 'index.html', context_dict)

def about(request):
	return render(request, 'about.html', ())

def category(request, category_name_slug):

	context_dict = {}

	try:
		# Can we find acategory nme slug with the given name
		# If we can't, the .get() method raises a DoesNotExist exception
		# So the .get() method returns one model instance or raises an exception
		category = Category.objects.get(slug=category_name_slug)
		context_dict['category_name'] = category.name

		# Retrieve all of the associated pages
		# Note that filter returns >= 1 model instance.
		pages = Page.objects.filter(category=category)

		# Adds our results list to the template context under name pages.
		context_dict['pages'] = pages
		#We also add the category object from the database to the context dictionary
		# We'll use this in the template to verify that the category exists
		context_dict['category'] = category
	
	except Category.DoesNotExist:
		# We get here if we didnt find the specified category
		# Don't do anything - the template display the "no category" message for us.
		pass

	# Go render the response and return it to the cllient.
	return render(request, 'category.html', context_dict)

def add_category(request):
	if request.method == 'POST':
		form = CategoryForm(request.POST)
		if form.is_valid():
			form.save(commit=True)
			return index(request)
		else:
			print form.errors
	else:
		form = CategoryForm()

	return render(request, 'add_category.html', {'form':form})

def add_page(request, category_name_slug):
	try:
		cat = Category.objects.get(slug=category_name_slug)
	
	except Category.DoesNotExist:
			cat = None

	if request.method == 'POST':
		form = PageForm(request.POST)
		if form.is_valid():
			if cat:
				page = form.save(commit=False)
				page.category = cat
				page.views = 0
				page.save()
				return category(request, category_name_slug)
			else:
				print form.errors
		else:
			print form.errors
	else:
		form = PageForm()
	context_dict = {'form':form, 'category': cat, 'slug': category_name_slug}

	return render(request, 'add_page.html', context_dict)


def register(request):
	registered = False
	if request.method =='POST':
		user_form = UserForm(data=request.POST)
		profile_form = UserProfileForm(data=request.POST)
		if user_form.is_valid() and profile_form.is_valid():
			user = user_form.save()

			user.set_password(user.password)
			user.save()

			profile = profile_form.save(commit=False)
			profile.user = user

			if 'picture' in request.FILES:
				profile.picture = request.FILES['picture']

			profile.save()

			registered = True
		else:
			print user_form.errors, profile_form.errors
	else:
		user_form = UserForm()
		profile_form = UserProfileForm()
	return render(request,
		'register.html',
		{'user_form': user_form,
		 'profile_form': profile_form, 
		 'registered': registered} 
		  )
def user_login(request):
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')

		user = authenticate(username=username, password=password)

		if user:
				if user.is_active:
					login(request, user)
					return HttpResponseRedirect('/')
				else:
					return HttpResponse("Your account is disabled.")
		else:
			print "Invalid login details: {0}, {1}".format(username, password)
			return HttpResponse("Invalid login details supplied.")
	else:
		return render(request, 'login.html', {})

@login_required
def add_category(request):
	if request.method == 'POST':
		form = CategoryForm(request.POST)

		if form.is_valid():
			form.save(commit=True)
			return index(request)
		else:
			form = CategoryForm()

		return render(request, 'add_category.html', {'form':form})

@login_required
def add_page(request):
	if request.method == 'POST':
		form = PageForm(request.POST)

		if form.is_valid():
			form.save(commit=True)
			return index(request)
		else:
			form = PageForm()

		return render(request, 'add_page.html', {'form':form})

@login_required
def user_logout(request):
	logout(request)

	return HttpResponseRedirect('/')
