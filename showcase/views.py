import copy

from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.shortcuts import get_object_or_404, render, HttpResponse, redirect
from django.db.models import F
from django.views import View

from .models import Category, Product
from payments.forms import PickColor, PickQuantity, PickSize, AddProductToBasket
from payments.cart import Cart


class CategoryListView(ListView):
    model = Category
    template_name = 'showcase/category_list.html'

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return Category.objects.filter(name__icontains=query)
        else:
            return super(CategoryListView, self).get_queryset()


class ProductsInCategoryDetailView(ListView):
    """Возвращает все продукты в одной категории"""
    model = Product
    template_name = 'showcase/category_detail.html'

    def get_queryset(self):
        category = get_object_or_404(Category, slug=self.kwargs['slug'])
        query = self.request.GET.get('q')
        if query:
            return Product.objects.filter(name__icontains=query).filter(category=category)
        else:
            return Product.objects.filter(category=category)

    def get_context_data(self, **kwargs):
        context = super(ProductsInCategoryDetailView, self).get_context_data()
        context['category_slug'] = self.kwargs['slug']
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'showcase/product_detail.html'

    def get_context_data(self, **kwargs):
        context = super(ProductDetailView, self).get_context_data()
        if self.request.method == 'GET':
            context['form'] = AddProductToBasket()
            context['size_form'] = PickSize()
            context['color_form'] = PickColor()
            context['quantity_form'] = PickQuantity()
        # print(self.request.session.get('product'))
        print(self.request.session['cart'])
        # self.request.session.flush()
        return context

    def post(self, request, *args, **kwargs):
        # self.request.session.flush()
        cart = Cart(request)
        print(request.session['cart'])
        form = AddProductToBasket(request.POST)
        if form.is_valid():
            if kwargs['pk'] not in self.request.session['cart']:
                cart.add(kwargs['pk'], form.cleaned_data['color'],
                         form.cleaned_data['size'], form.cleaned_data['count'])
            else:
                cart.update(kwargs['pk'], form.cleaned_data['color'],
                            form.cleaned_data['size'], form.cleaned_data['count'])
        return redirect('product_detail', pk=int(kwargs['pk']))


def basket(request, pk=None):
    """Корзина в которой можно просматривать, а также изменять количество, цвет, размер товаров"""
    cart = Cart(request)
    cart_sessions = request.session['cart']
    total_price = cart.get_total_price()
    if request.method == 'POST':
        size, color, quantity = None, None, None
        size_form = PickSize(request.POST)
        color_form = PickColor(request.POST)
        quantity_form = PickQuantity(request.POST)
        if size_form.is_valid():
            size = size_form.cleaned_data['size']
        if color_form.is_valid():
            color = color_form.cleaned_data['color']
        if quantity_form.is_valid():
            quantity = quantity_form.cleaned_data['count']
        cart.update(pk, sizes=size, colors=color, quantity=quantity)
        return redirect('basket')
    else:
        size_form = PickSize()
        color_form = PickColor()
        quantity_form = PickQuantity()
    return render(request, 'showcase/basket.html', {'size_form': size_form, 'pr': cart_sessions,
                                                    'total_price': total_price,
                                                    'color_form': color_form, 'quantity_form': quantity_form})


def cart_remove(request, pk):
    """Удалить товар из сессии"""
    cart = Cart(request)
    product = get_object_or_404(Product, pk=pk)
    cart.remove(product)
    return redirect('basket')

