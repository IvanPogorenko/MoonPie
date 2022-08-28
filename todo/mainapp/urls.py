from django.urls import path

from .views import *

urlpatterns = [
    path('', BaseView.as_view(), name='base'),
    path('catalog/all', CatalogView.as_view(), name='catalog'),
    path('catalog/<str:slug>/', CategoryDetailView.as_view(), name='category_detail'),
    path('catalog/<str:ct_model>/<str:slug>/', ProductDetailView.as_view(), name='product_description'),
    path('brand/', brand_view, name='brand'),
    path('fabrics/', fabrics_view, name='fabrics'),
    path('contacts/', contacts_view, name='contacts'),
    path('how_to_order', how_to_order_view, name='how_to_order'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', AuthenticationView.as_view(), name='login'),
    path('cart/', CartView.as_view(), name='cart'),
    path('add-to-cart/<str:ct_model>/<str:slug>', AddToCartView.as_view(), name='add_to_cart'),
    path('remove-from-cart/<str:ct_model>/<str:slug>', DeleteFromCartView.as_view(), name='delete_from_cart'),
    path('change-qty/<str:ct_model>/<str:slug>', ChangeQTYView.as_view(), name='change_qty'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('make-order/', MakeOrderView.as_view(), name='make_order')
]


