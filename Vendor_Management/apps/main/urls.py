from django.contrib.auth.views import (
    PasswordChangeView,
    PasswordChangeDoneView
)
from django.urls import path
from .views import (
    home,
    SignUpView,
    user_login,
    user_logout,
    users_list,
    profile,
    vendors,
    create_vendor,
    edit_vendor,
    vendor_detail,
    delete_vendor,
    create_product,
    update_product,
    applications,
    product_detail,
    delete_product,
    add_comment,
    permissions,
    generate_softwares_pdf,
    export_data_to_csv,
    update_profile_view,
    create_permission,
    update_permission,
    delete_permission,
    user_details,
    assign_permission_to_user
)

urlpatterns = [
    path('', home, name='home'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),

    path('accounts/password_change/', PasswordChangeView.as_view(), name='password_change'),
    path('accounts/password_change/done/', PasswordChangeDoneView.as_view(), name='password_change_done'),
    path('users/', users_list, name='users'),
    path('users/<int:user_id>/', user_details, name='user_detail'),
    path('profile/', profile, name='profile'),
    path('vendors/', vendors, name='vendors'),
    path('create_vendor/', create_vendor, name='create_vendor'),
    path('vendor/<int:vendor_id>/', vendor_detail, name='vendor_detail'),
    path('edit/<int:vendor_id>/', edit_vendor, name='edit_vendor'),
    path('delete/<int:vendor_id>/', delete_vendor, name='delete_vendor'),
    path('create_product/', create_product, name='create_product'),
    path('update/<int:product_id>/', update_product, name='update_product'),
    path('product/<int:product_id>/', product_detail, name='product_detail'),
    path('delete/product/<int:product_id>/', delete_product, name='delete_product'),
    path('applications/', applications, name='applications'),
    path('add-comment/vendor/<int:vendor_id>/', add_comment, name='add_vendor_comment'),
    path('add-comment/product/<int:product_id>/', add_comment, name='add_product_comment'),
    path('update-profile/', update_profile_view, name='update_profile'),
    path('generate_softwares_pdf/', generate_softwares_pdf, name='generate_softwares_pdf'),
    path('export-csv/', export_data_to_csv, name='export_data_to_csv'),
    path('create_permission/', create_permission, name='create_permission'),
    path('permissions/', permissions, name='permissions'),
    path('update_permission/<int:permission_id>/', update_permission, name='update_permission'),
    path('permissions/delete/<int:permission_id>/', delete_permission, name='delete_permission'),
    path('assign_permission/', assign_permission_to_user, name='assign_permission'),
]