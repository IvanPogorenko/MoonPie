from django.db import transaction
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.views.generic import DetailView, View, ListView
from .models import *
from .forms import *
from django.contrib.auth.models import User
from .mixins import CategoryDetailMixin, CartMixin
from .utils import recalc_cart


def brand_view(request):
    categories = Category.objects.get_categories_for_head()
    return render(request, 'brand.html', context={'categories': categories})


def fabrics_view(request):
    categories = Category.objects.get_categories_for_head()
    return render(request, 'fabrics.html', context={'categories': categories})


def how_to_order_view(request):
    categories = Category.objects.get_categories_for_head()
    return render(request, 'how_to_order.html', context={'categories': categories})


def contacts_view(request):
    categories = Category.objects.get_categories_for_head()
    return render(request, 'contacts.html', context={'categories': categories})


class BaseView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        categories = Category.objects.get_categories_for_head()
        context = {
            'categories': categories,
            'cart': self.cart
        }
        return render(request, 'base.html', context)


class CatalogView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        categories = Category.objects.get_categories_for_head()
        blouses = Blouse.objects.all()
        trousers = Trousers.objects.all()
        overalls = Overalls.objects.all()
        context = {
            'categories': categories,
            'blouses': blouses,
            'trousers': trousers,
            'overalls': overalls
        }
        return render(request, 'catalog.html', context)


class CategoryDetailView(CartMixin, CategoryDetailMixin, DetailView):

    model = Category
    queryset = Category.objects.all()
    context_object_name = 'category'
    template_name = 'category_detail.html'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cart'] = self.cart
        return context


class ProductDetailView(CartMixin, CategoryDetailMixin, DetailView):

    CT_MODEL_MODEL_CLASS = {
        'trousers': Trousers,
        'blouse': Blouse,
        'overalls': Overalls
    }

    def dispatch(self, request, *args, **kwargs):
        self.model = self.CT_MODEL_MODEL_CLASS[kwargs['ct_model']]
        self.queryset = self.model._base_manager.all()
        return super().dispatch(request, *args, **kwargs)

    context_object_name = 'product'
    template_name = 'product_description.html'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ct_model'] = self.model._meta.model_name
        context['cart'] = self.cart
        context['combobox_colors'] = CartProduct.COLORS
        context['form'] = CartProductDescription(context['product'])
        # print(combobox_max_size)
        # for i in range(42, int(combobox_max_size)+1, 2):
        #     context['combobox'].add(i)
        print(context)
        return context


class RegisterView(CreateView):
    template_name = 'register_page.html'
    form_class = UserRegister
    success_url = '/'

    def for_user(request):
        user = UserRegister.username
        return render(request, "base.html", user)

    def form_valid(self, form):
        user = form.save()
        newSiteUser = Customer.objects.create(user=user)
        newSiteUser.save()
        login(self.request, user)
        return redirect('base')


class AuthenticationView(LoginView):
    template_name = 'login_page.html'
    form_class = Authentication

    def foruser(request):
        user = UserRegister.username
        return render(request, "base.html", user)


class AddToCartView(CartMixin, View):

    def get(self, request, *args, **kwargs):

        ct_model, product_slug = kwargs.get('ct_model'), kwargs.get('slug')
        content_type = ContentType.objects.get(model=ct_model)
        product = content_type.model_class().objects.get(slug=product_slug)
        cart_product, created = CartProduct.objects.get_or_create(user=self.cart.owner, cart=self.cart, content_type=content_type, object_id=product.id)
        if created:
            self.cart.products.add(cart_product)
        recalc_cart(self.cart)
        messages.add_message(request, messages.INFO, "Товар успешно добавлен")
        return HttpResponseRedirect('/cart/')


class DeleteFromCartView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        ct_model, product_slug = kwargs.get('ct_model'), kwargs.get('slug')
        content_type = ContentType.objects.get(model=ct_model)
        product = content_type.model_class().objects.get(slug=product_slug)
        cart_product = CartProduct.objects.get(user=self.cart.owner, cart=self.cart, content_type=content_type, object_id=product.id)
        self.cart.products.remove(cart_product)
        cart_product.delete()
        recalc_cart(self.cart)
        messages.add_message(request, messages.INFO, "Товари успешно удален")
        return HttpResponseRedirect('/cart/')


class ChangeQTYView(CartMixin, View):

    def post(self, request, *args, **kwargs):
        ct_model, product_slug = kwargs.get('ct_model'), kwargs.get('slug')
        content_type = ContentType.objects.get(model=ct_model)
        product = content_type.model_class().objects.get(slug=product_slug)
        cart_product = CartProduct.objects.get(user=self.cart.owner, cart=self.cart, content_type=content_type, object_id=product.id)
        qty = int(request.POST.get('qty'))
        cart_product.qty = qty
        cart_product.save()
        recalc_cart(self.cart)
        messages.add_message(request, messages.INFO, "Кол-во успешно изменено")
        return HttpResponseRedirect('/cart/')


class CartView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        categories = Category.objects.get_categories_for_head()
        context = {
            'cart': self.cart,
            'categories': categories
        }
        return render(request, 'cart_detail.html', context)


class CheckoutView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        categories = Category.objects.get_categories_for_head()
        form = OrderForm(request.POST or None)
        context = {
            'cart': self.cart,
            'categories': categories,
            'form': form
        }
        return render(request, 'checkout.html', context)


class MakeOrderView(CartMixin, View):

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        form = OrderForm(request or None)
        if form.is_valid():
            new_order = form.save(commit=False)
            new_order.customer = Customer.object.get(user=request.user)
            new_order.first_name = form.cleaned_data['first_name']
            new_order.last_name = form.cleaned_data['last_name']
            new_order.phone = form.cleaned_data['phone']
            new_order.address = form.cleaned_data['address']
            new_order.comment = form.cleaned_data['comment']
            new_order.save()
            self.cart.in_order = True
            self.cart.save()
            new_order.cart = self.cart
            new_order.save()
            messages.add_message(request, messages.INFO, 'Спасибо за заказ! Менеджер с Вами свяжется')
            return HttpResponseRedirect('/')
        return HttpResponseRedirect('/checkout/')