from rest_framework.decorators import api_view
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.response import Response
from django.shortcuts import render, get_object_or_404
from .models import *
from rest_framework import viewsets, filters, permissions, status
from .serializers import ClothesSerializer, UserSerializer, CartItemSerializer, SizeSerializer, TypeSerializer
from django.contrib.auth.models import User
from django.http import HttpResponse


def index(request):
    return render(request, "index.html")


def search(request):
    return render(request, "search.html")


def itemcart(request):
    return render(request, "cart.html")


def userItems(request):
    return render(request, "userCart.html")


class ClothesViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ClothesSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', '=vendor_code', 'sizes__size', '=type_category__category_name']
    ordering_fields = ['price']

    def get_queryset(self):
        queryset = Clothes.objects.all()
        category_name = self.request.query_params.get('category', None)
        item_id = self.request.query_params.get('id', None)
        lower_bound_price = self.request.query_params.get('lprice', None)
        upper_bound_price = self.request.query_params.get('uprice', None)

        if item_id:
            queryset = queryset.filter(id=item_id)
        if lower_bound_price or upper_bound_price:
            queryset = queryset.filter(price__gte=lower_bound_price)
            queryset = queryset.filter(price__lte=upper_bound_price)
        if category_name:
            type_category = Type.objects.filter(category_name=category_name).first()

            # Check if type_category exists
            if type_category:
                queryset = queryset.filter(type_category=type_category)
            else:
                # If no matching category, return an empty queryset
                queryset = Clothes.objects.none()
        return queryset


class UserView(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all();
    serializer_class = UserSerializer


class UserRegister(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all();
    http_method_names = ['post']


class CartItemViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CartItemSerializer

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user).select_related('clothes')

    from django.shortcuts import get_object_or_404
    from rest_framework.exceptions import ValidationError
    from rest_framework.response import Response

    def create(self, *args, **kwargs):
        data = self.request.data.copy()
        clothes_id = data.get('clothes_id')
        size_str = data.get('size')

        # Получаем объект Clothes или возвращаем ошибку, если таковой не найден
        clothes = get_object_or_404(Clothes, id=clothes_id)

        # Получаем объект Size, соответствующий переданной строке, или возвращаем ошибку, если таковой не найден
        size = get_object_or_404(Size, size=size_str)

        # Проверяем, существует ли уже элемент в корзине с указанными товаром и размером
        existing_item = CartItem.objects.filter(
            user=self.request.user,
            clothes=clothes,
            size=size
        ).first()

        if existing_item:
            # Если такой элемент существует, увеличиваем его количество
            existing_item.quantity += 1
            existing_item.save(update_fields=['quantity'])
            serializer = self.get_serializer(existing_item)
        else:
            # Если такого элемента нет, создаем новый
            data['user'] = self.request.user.pk
            data['clothes'] = clothes.pk
            data['size'] = size.pk  # Устанавливаем ForeignKey на объект Size
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user:
            # Проверка, принадлежит ли объект корзины текущему пользователю
            raise PermissionDenied("Вы не можете удалить этот элемент корзины.")
        if instance.quantity > 1:
            instance.quantity -= 1
            instance.save(update_fields=['quantity'])
        else:
            instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user:
            raise PermissionDenied("Вы не можете обновить этот элемент корзины.")
        data = request.data.copy()
        new_size = data.get('size')
        new_quantity = data.get('quantity')
        if new_size:
            instance.size = new_size
        if new_quantity:
            if int(new_quantity) > instance.clothes.count:
                raise PermissionDenied("Вы не можете добавить в корзину больше товаров, чем есть в наличии.")
            instance.quantity = new_quantity
        instance.save()

        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)


def size_view(request):
    if request.method == 'GET':
        queryset = Size.objects.all()
        serializer = SizeSerializer(queryset, many=True)
        return Response(serializer.data)

    else:
        return HttpResponse(status=405, reason='Method Not Allowed')


def type_view(request):
    if request.method == 'GET':
        queryset = Type.objects.all()
        serializer = TypeSerializer(queryset, many=True)
        return Response(serializer.data)

    else:
        return HttpResponse(status=405, reason='Method Not Allowed')
