from django.shortcuts import render
from django.http import HttpResponse
from models import Page
from forms import CategoryForm, PageForm

# Create your views here.

def index(request):
	# Query the database for a list of ALL categories currently stored.
	# Order the categories by no. likes in descending order.
	# Retrieve the top 5 only - or all if less than 5.
	# Place the list in our context_dict dictionary which will be passed to the template engine.
	category_list = Category.objects.order_by('-likes')[:5]
	context_dict = {'categories': category_list}
	page_list = Page.objects.order_by('-views')[:5]
	context_dict = {'categories' : category_list,	'pages' : page_list }
	# Render the response nd send it back!
	return render(request, 'index.html', context_dict)

def about(request):
	return HttpResponse ('About Us')

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


