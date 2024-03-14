import csv
from typing import Dict, Any

from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Permission
from django.db.models import Avg
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views import View
from utils.views import render_to_pdf
from .enums import UserTypes
from .forms import (
    VendorForm,
    ProductForm,
    CommentForm,
    UserForm,
    DocumentFormSet,
    PermissionForm
)
from .models import (
    User,
    Vendor,
    Product,
    Comment, Permissions
)


@login_required
def home(request):
    users = User.objects.all().count()
    companies = Vendor.objects.all().count()
    applications = Product.objects.all().count()
    latest_applications = Product.objects.order_by('-created_at')[:5]

    context: dict[str, Any] = {
        'users': users,
        'companies': companies,
        'applications': applications,
        'latest_applications': latest_applications
    }
    return render(request, 'home.html', context)


class SignUpView(View):
    template_name = 'authentication/signup.html'
    success_url = reverse_lazy('home')

    def get(self, request):
        form = UserForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = UserForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password1 = form.cleaned_data['password1']
            password2 = form.cleaned_data['password2']
            user_type = form.cleaned_data['user_type']

            # check if user with this  username or email exists
            if User.objects.filter(username=username) | User.objects.filter(email=email):
                messages.error(request, 'User with these details already exists')
                return render(request, self.template_name, {'form': form})

            if password1 != password2:
                messages.error(request, 'Passwords do not match')
                return render(request, self.template_name, {'form': form})

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
                user_type=user_type
            )

            messages.success(request, f"{user.username} account has been created successfully")
            if user.user_type == UserTypes.VENDOR:
                user = authenticate(request, username=username, password=password1)
                if user is not None:
                    login(request, user)
                    return redirect(reverse('create_vendor'))
            else:
                user = authenticate(request, username=username, password=password1)
                if user is not None:
                    login(request, user)
                    return redirect(self.success_url)

        # If form is not valid, re-render the form with errors
        return render(request, self.template_name, {'form': form})


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')
            return render(request, 'authentication/login.html')
    else:
        return render(request, 'authentication/login.html')


def update_profile_view(request):
    if request.method == "POST":
        user = request.user
        user_profile = user.profile
        profile_picture = request.FILES.get("profile_picture")
        username = request.POST.get("username")
        name = request.POST.get("name")
        email = request.POST.get("email")

        # Split name if necessary
        if ' ' in name:
            first_name, last_name = name.split(' ', 1)
            user.first_name = first_name
            user.last_name = last_name
        else:
            user.first_name = name
        user.username = username
        user.email = email

        user.save()

        if profile_picture:
            user_profile.image = profile_picture
            user_profile.save()
        messages.success(request, "Your profile has been updated successfully")
        return redirect(reverse('profile'))
    else:
        return render(request, 'profile.html')


def user_logout(request):
    logout(request)
    return redirect('login')


def users_list(request):
    users = User.objects.all()
    context: dict[str, Any] = {
        'users': users,
    }
    return render(request, 'users/users_list.html', context)


def user_details(request, user_id):
    user = get_object_or_404(User, id=user_id)
    all_permissions = Permissions.objects.all()
    result = []
    for permission in user.user_permissions.all():
        result.append(permission.id)

    context: dict[str, Any] = {
        'user': user,
        'all_permissions': all_permissions,
        'user_permissions': result
    }
    return render(request, 'users/user_detail.html', context)


def profile(request):
    return render(request, 'users/account.html')


def vendors(request):
    companies = Vendor.objects.all()
    context: dict[str, Any] = {
        'vendors': companies
    }
    return render(request, 'vendors/vendors.html', context)


def create_vendor(request):
    if request.method == 'POST':
        vendor_form = VendorForm(request.POST)
        if vendor_form.is_valid():
            vendor = vendor_form.save(commit=False)
            vendor.user = request.user
            vendor.created_by = request.user.username
            vendor.save()
            messages.success(
                request,
                f'Vendor {vendor.vendor_name} was created successfully.')
            return redirect('vendors')
    else:
        vendor_form = VendorForm()

    return render(
        request,
        'vendors/create_vendor.html',
        {'vendor_form': vendor_form})


def vendor_detail(request, vendor_id):
    vendor = get_object_or_404(Vendor, id=vendor_id)

    applications = Product.objects.filter(vendor=vendor)
    comments = Comment.objects.filter(vendor=vendor).order_by('-timestamp')

    avg_rating = comments.aggregate(rating=Avg('rating'))['rating']
    average_rating = round(avg_rating) if avg_rating else None

    # count reviews
    review_count = comments.count()

    review_form = CommentForm()

    context = {
        'vendor': vendor,
        'reviews': comments,
        'count': review_count,
        'average_rating': average_rating,
        'applications': applications,
        'review_form': review_form,
    }

    return render(request, 'vendors/vendor_detail.html', context)


def edit_vendor(request, vendor_id):
    vendor = get_object_or_404(Vendor, id=vendor_id)

    if request.method == 'POST':
        vendor_form = VendorForm(request.POST, instance=vendor)

        if vendor_form.is_valid():
            vendor_form.save()
            messages.success(
                request,
                f'Vendor {vendor.vendor_name} was updated successfully.')
            return redirect('vendors')
        else:
            messages.error(request, 'There was an error saving the form. Please check the information.')
    else:
        vendor_form = VendorForm(instance=vendor)

    return render(
        request,
        'vendors/edit_vendor.html', {
            'vendor_form': vendor_form,
            'vendor': vendor,
        })


def delete_vendor(request, vendor_id):
    vendor = get_object_or_404(Vendor, id=vendor_id)
    if request.method == 'POST':
        vendor.delete()

        messages.success(request, f'Company {vendor.vendor_name} was deleted successfully.')
        return redirect('vendors')
    else:
        return redirect('vendors')


def create_product(request):
    if request.method == 'POST':
        product_form = ProductForm(request.POST)
        document_formset = DocumentFormSet(request.POST, request.FILES)

        if product_form.is_valid() and document_formset.is_valid():
            product = product_form.save()

            for form in document_formset:
                if form.cleaned_data.get('document'):
                    document = form.save(commit=False)
                    document.product = product
                    document.save()

                    if document.document:
                        product.document_attached = True
                        product.save()

        return redirect('applications')

    else:
        product_form = ProductForm()
        document_formset = DocumentFormSet()

    return render(
        request,
        'vendors/create_product.html',
        {
            'product_form': product_form,
            'document_formset': document_formset})


@login_required
def update_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        product_form = ProductForm(request.POST, instance=product)
        document_formset = DocumentFormSet(request.POST, request.FILES, instance=product)

        if product_form.is_valid() and document_formset.is_valid():
            product = product_form.save()

            for form in document_formset:
                if form.cleaned_data.get('document'):
                    document = form.save(commit=False)
                    document.product = product
                    document.save()
                    if document.document:
                        product.document_attached = True
                        product.save()

            messages.success(request, f'{product.name} updated successfully')
            return redirect('applications')
    else:
        product_form = ProductForm(instance=product)
        document_formset = DocumentFormSet(instance=product)

    return render(
        request,
        'vendor_products/update_product.html',
        {
            'product_form': product_form,
            'document_formset': document_formset,
            'product': product
        }
    )


def applications(request):
    applications = Product.objects.all()
    context: dict[str, Any] = {
        'applications': applications
    }
    return render(request, 'vendor_products/applications.html', context)


def add_comment(request, vendor_id=None, product_id=None):
    if request.method == 'POST':
        rating = request.POST.get('rating')
        content = request.POST.get('content')
        user = request.user

        if vendor_id:
            instance = Vendor.objects.filter(pk=vendor_id).first()
            redirect_path = reverse('vendor_detail', args=[vendor_id])

        elif product_id:
            instance = Product.objects.filter(pk=product_id).first()
            redirect_path = reverse('product_detail', args=[product_id])

        if not instance:
            messages.error(request, 'Invalid request.')
            return redirect('home')

        existing_comment = Comment.objects.filter(
            commented_by=user, vendor_id=vendor_id if vendor_id else None,
            product_id=product_id if product_id else None).exists()

        if existing_comment:
            messages.error(request, 'You have already commented.')
            return redirect(redirect_path)

        comment = Comment(
            commented_by=user,
            rating=rating,
            content=content,
            vendor=instance if vendor_id else None,
            product=instance if product_id else None
        )
        comment.save()

        messages.success(request, 'Comment added successfully.')
        return redirect(redirect_path)

    messages.error(request, 'Invalid request method.')
    return redirect('home')


def generate_pdf(request, context, template, filename):
    pdf = render_to_pdf(template, context)
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        content = f"inline; filename={filename}"
        download = request.GET.get("download")
        if download:
            content = f"attachment; filename={filename}"
        response['Content-Disposition'] = content
        return response
    return HttpResponse("Not found")


def generate_softwares_pdf(request):
    template = 'vendor_products/software_pdf.html'
    softwares = Product.objects.all()
    context = {"applications": softwares}
    file_name = 'softwares.pdf'
    return generate_pdf(request, context, template, file_name)


def export_data_to_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="software_data.csv"'

    writer = csv.writer(response)

    # Write header row for Software
    writer.writerow(
        [
            'Name',
            'Software Type',
            'Module',
            'Client Type',
            'Last Demo Date',
            'Last Review Date',
            'Next Review Date',
            'Document Attached',
            'Cloud Status',
            'Additional Information',
            'Internal Professional Services',
            'Business Area',
        ]
    )

    softwares = Product.objects.all()

    # Write data rows for Software
    for software in softwares:
        writer.writerow(
            [
                software.name,
                software.software_type,
                software.module,
                software.client_type,
                software.last_demo_date,
                software.last_review_date,
                software.next_review_date,
                software.document_attached,
                software.cloud_status,
                software.additional_information,
                software.internal_professional_services,
                software.business_area,
            ]
        )

    return response


def product_detail(request, product_id):
    software = get_object_or_404(Product, pk=product_id)
    comments = Comment.objects.filter(product=software).order_by('-timestamp')

    avg_rating = comments.aggregate(rating=Avg('rating'))['rating']
    average_rating = round(avg_rating) if avg_rating else None

    # count reviews
    review_count = comments.count()

    review_form = CommentForm()

    context = {
        'software': software,
        'reviews': comments,
        'count': review_count,
        'average_rating': average_rating,
        'applications': applications,
        'review_form': review_form,
    }
    return render(request, 'vendor_products/software_detail.html', context)


def delete_product(request, product_id):
    software = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        software.delete()
        messages.success(request, f'{software.name} was deleted successfully.')
        return redirect('applications')
    else:
        return redirect('applications')


def create_permission(request):
    if request.method == 'POST':
        permission_form = PermissionForm(request.POST)
        if permission_form.is_valid():
            permission = permission_form.save()
            messages.success(request, f'{permission.name} created successfully.')
            return redirect('permissions')
    else:
        permission_form = PermissionForm()

    return render(
        request,
        'permissions/create_permission.html',
        {
            'permission_form': permission_form
        }
    )


def permissions(request):
    permissions = Permissions.objects.all()
    context: dict[str, Any] = {
        'permissions': permissions
    }
    return render(request, 'permissions/permissions.html', context)


def update_permission(request, permission_id):
    try:
        permission = get_object_or_404(Permission, pk=permission_id)

        if request.method == 'POST':
            permission_form = PermissionForm(request.POST, instance=permission)
            if permission_form.is_valid():
                permission = permission_form.save()
                messages.success(request, f'{permission.name} updated successfully.')
                return redirect('permissions')
        else:
            permission_form = PermissionForm(instance=permission)

        return render(
            request,
            'permissions/update_permission.html',
            {
                'permission_form': permission_form,
                'permission': permission
            }
        )

    except Exception as e:
        messages.error(request, str(e))
        return redirect('permissions')


def assign_permission_to_user(request):
    try:
        if request.method == 'POST':
            user_id = request.POST.get('user_id')
            permission_id = request.POST.get('permission_id')
            checked = request.POST.get('checked') == 'true'

            user = get_object_or_404(User, pk=user_id)
            permission = get_object_or_404(Permission, pk=permission_id)

            if checked:
                user.user_permissions.add(permission)
                message = f'{permission.name} assigned to {user.username} successfully.'
            else:
                user.user_permissions.remove(permission)
                message = f'{permission.name} removed from {user.username} successfully.'

            return JsonResponse({'message': message})

        return JsonResponse({'error': 'Invalid request'}, status=400)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def delete_permission(request, permission_id):
    try:
        permission = get_object_or_404(Permission, pk=permission_id)
        if request.method == 'POST':
            permission.delete()
            messages.success(request, f'{permission.name} was deleted successfully.')
            return redirect('permissions')
        else:
            return redirect('permissions')
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
