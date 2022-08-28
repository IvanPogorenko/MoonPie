from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User

User = get_user_model()


def get_product_url(obj, viewname):
    ct_model = obj.__class__._meta.model_name
    return reverse(viewname, kwargs={'ct_model': ct_model, 'slug': obj.slug})


class LatestProductsManager:

    @staticmethod
    def get_products_for_main_page(*args, **kwargs):
        with_respect_to = kwargs.get('with_respect_to')
        products = []
        ct_models = ContentType.objects.filter(model__in=args)
        for ct_model in ct_models:
            model_products = ct_model.model_class()._base_manager.all.order_by('-id')[:10]
            products.extend(model_products)
        if with_respect_to:
            ct_model = ContentType.objects.filter(model=with_respect_to)
            if ct_model.exists():
                if with_respect_to in args:
                    return sorted(products, key=lambda x: x.__class__._meta.model_name.startwith(with_respect_to, reverse=True))
        return products


class LatestProducts:

    objects = LatestProductsManager()


def get_models_for_count(*model_names):
    return [models.Count(model_name) for model_name in model_names]


class CategoryManager(models.Manager):

    CATEGORY_NAME_COUNT_NAME = {
        'Блузы': 'blouse__count',
        'Брюки': 'trousers__count',
        'Комбинезоны': 'overalls__count'
    }

    def get_queryset(self):
        return super().get_queryset()

    def get_categories_for_head(self):
        models = get_models_for_count('blouse', 'trousers', 'overalls')
        qs = list(self.get_queryset().annotate(*models))
        data = [
            dict(name=c.name, url=c.get_absolute_url(), count=getattr(c, self.CATEGORY_NAME_COUNT_NAME[c.name])) for c in qs
        ]
        return data


class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name='Имя категории')
    slug = models.SlugField(unique=True)
    objects = CategoryManager()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'slug': self.slug})


class Product(models.Model):

    class Meta:
        abstract = True

    category = models.ForeignKey(Category, verbose_name='Категория', on_delete=models.CASCADE)
    title = models.CharField(max_length=255, verbose_name='Наименование')
    slug = models.SlugField(unique=True)
    description = models.TextField(verbose_name='Описание', null=True)
    image1 = models.ImageField(verbose_name='Изображение товара', blank=True, null=True)
    image2 = models.ImageField(verbose_name='Изображение товара', blank=True, null=True)
    image3 = models.ImageField(verbose_name='Изображение товара', blank=True, null=True)
    image4 = models.ImageField(verbose_name='Изображение товара', blank=True, null=True)
    image5 = models.ImageField(verbose_name='Изображение товара', blank=True, null=True)
    image6 = models.ImageField(verbose_name='Изображение товара', blank=True, null=True)
    max_size = models.SmallIntegerField(verbose_name='Максимальный размер', blank=True, null=True)
    price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Цена')

    def __str__(self):
        return self.title

    def get_model_name(self):
        return self.__class__.__name__.lower()


class CartProduct(models.Model):

    COLORS = (
        (None, 'Не выбран'),
        ('Mint', 'Мята'),
        ('Blue', 'Голубой'),
        ('Graphite', 'Графит'),
        ('White', 'Белый'),
        ('Dark Blue', 'Темно-синий')

    )

    user = models.ForeignKey('Customer', verbose_name='Покупатель', on_delete=models.CASCADE)
    size = models.PositiveIntegerField(verbose_name='Размер', default=0, blank=True, null=True)
    height = models.PositiveIntegerField(verbose_name='Рост', default=0)
    size_of_rud = models.PositiveIntegerField(verbose_name='Обхват груди', default=0, blank=True, null=True)
    size_of_waist = models.PositiveIntegerField(verbose_name='Обхват талии', default=0, blank=True, null=True)
    size_of_hips = models.PositiveIntegerField(verbose_name='Обхват бедер', default=0, blank=True, null=True)
    color = models.CharField(max_length=50, verbose_name='Цвет', blank=True, null=True, choices=COLORS)
    qty = models.PositiveIntegerField(verbose_name='Количество товара одного вида', default=1)
    final_price = models.DecimalField(max_digits=9, default=0, decimal_places=2, verbose_name=' Общая Цена')
    cart = models.ForeignKey('Cart', on_delete=models.PROTECT, verbose_name='Корзина', related_name='related_products', blank=True, null=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return "Продукт: {} (для корзины)".format(self.content_object.title)

    def save(self, *args, **kwargs):
        self.final_price = self.qty * self.content_object.price
        super().save(*args, **kwargs)


class Cart(models.Model):

    owner = models.ForeignKey('Customer', null=True, verbose_name='Владелец', on_delete=models.CASCADE)
    products = models.ManyToManyField(CartProduct, blank=True, related_name='related_cart')
    total_products = models.PositiveIntegerField(verbose_name='Общее количество товаров', default=0)
    final_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Общая Цена', default=0)
    in_order = models.BooleanField(default=False)
    for_anonymous_user = models.BooleanField(default=False )

    def __str__(self):
        return str(self.id)


class Customer(models.Model):
    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE)
    email = models.EmailField(verbose_name='Почта', null=True, blank=True)

    def __str__(self):
        return "Покупатель: {}".format(self.user.username)


class Order(models.Model):

    STATUS_NEW = 'new'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_READY = 'is_ready'
    STATUS_COMPLETED = 'completed'

    STATUS_CHOICES = (
        (STATUS_NEW, 'Новый заказ'),
        (STATUS_IN_PROGRESS, 'Заказ в обработке'),
        (STATUS_READY, 'Заказ готов'),
        (STATUS_COMPLETED, 'Заказ выполнен')
    )

    customer = models.ForeignKey(Customer, verbose_name='Покупатель', on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255, verbose_name='Имя')
    last_name = models.CharField(max_length=255, verbose_name='Фамилия')
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    cart = models.ForeignKey(Cart, verbose_name='Корзина', on_delete=models.CASCADE, null=True, blank=True)
    address = models.CharField(max_length=1024, verbose_name='Адрес')
    status = models.CharField(max_length=100, verbose_name='Статус заказа', choices=STATUS_CHOICES, default=STATUS_NEW)
    comment = models.TextField(verbose_name='Комментарий к заказу', null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True, verbose_name='Дата создания заказа')

    def __str__(self):
        return str(self.id)


class Trousers(Product):

    def __str__(self):
        return "{} : {}".format(self.category.name, self.title)

    def get_absolute_url(self):
        return get_product_url(self, 'product_description')


class Overalls(Product):

    def __str__(self):
        return "{} : {}".format(self.category.name, self.title)

    def get_absolute_url(self):
        return get_product_url(self, 'product_description')


class Blouse(Product):

    def __str__(self):
        return "{} : {}".format(self.category.name, self.title)

    def get_absolute_url(self):
        return get_product_url(self, 'product_description')