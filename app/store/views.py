from rest_framework.decorators import api_view
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
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
        quantity = int(data.get('quantity', 1))

        # Получаем объекты Clothes и Size
        clothes = get_object_or_404(Clothes, id=clothes_id)
        size = get_object_or_404(Size, size=size_str)

        # Проверяем наличие товара указанного размера и его доступное количество
        try:
            clothes_size = ClothesSize.objects.get(clothes=clothes, size=size)
            if clothes_size.quantity < quantity:
                raise ValidationError('Недостаточно товара в наличии.')
        except ClothesSize.DoesNotExist:
            raise NotFound('Данный размер отсутствует для выбранной одежды.')

        # Проверяем наличие товара с выбранным размером в корзине пользователя
        existing_item = CartItem.objects.filter(user=self.request.user, clothes=clothes, size=size).first()

        if existing_item:
            # Если товар уже есть в корзине, проверяем, можно ли увеличить его количество
            if existing_item.quantity + quantity <= clothes_size.quantity:
                existing_item.quantity += quantity
                existing_item.save(update_fields=['quantity'])
            else:
                raise ValidationError('Добавление данного количества превысит доступное количество товара в наличии.')
            serializer = self.get_serializer(existing_item)
        else:
            # Если товара с таким размером нет в корзине, создаем новый элемент
            new_item = CartItem.objects.create(user=self.request.user, clothes=clothes, size=size, quantity=quantity)
            serializer = self.get_serializer(new_item)

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
        new_size_str = data.get('size', None)
        new_quantity = int(data.get('quantity', 1))
        new_size = None

        # Изначально берём текущий размер и количество instance
        clothes_size = ClothesSize.objects.filter(clothes=instance.clothes, size=instance.size).first()
        if not clothes_size or clothes_size.quantity < new_quantity:
            raise ValidationError("Недостаточно товара в наличии по текущему размеру.")

        if new_size_str:
            try:
                new_size = Size.objects.get(size=new_size_str)
                # Если новый размер отличается от текущего, обновляем clothes_size и задаём количество = 1
                if instance.size != new_size:
                    clothes_size = ClothesSize.objects.filter(clothes=instance.clothes, size=new_size).first()
                    if not clothes_size:
                        raise NotFound("Данный размер отсутствует для выбранной одежды.")
                    if clothes_size.quantity < 1:
                        raise ValidationError("Недостаточно товара в наличии.")
                    new_quantity = 1  # Устанавливаем количество равным 1 для нового размера
            except Size.DoesNotExist:
                raise NotFound("Указанный размер не найден.")

        query = CartItem.objects.filter(user=request.user, clothes=instance.clothes, size=new_size or instance.size)
        existing_item = query.exclude(id=instance.id).first()

        if existing_item:
            if existing_item.quantity + new_quantity <= clothes_size.quantity:
                existing_item.quantity += new_quantity
                existing_item.save(update_fields=['quantity'])
                instance.delete()
            else:
                raise ValidationError("Добавление данного количества превысит доступное количество товара в наличии.")
        else:
            if new_size:
                instance.size = new_size
            instance.quantity = new_quantity
            instance.save()

        serializer = self.get_serializer(existing_item if existing_item else instance)
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
