from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.response import Response
from django.shortcuts import render
from .models import *
from rest_framework import viewsets, filters, permissions, status
from .serializers import ClothesSerializer, UserSerializer, CartItemSerializer
from django.contrib.auth.models import User


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




class CartItemViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CartItemSerializer

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user).select_related('clothes')

    def create(self, *args, **kwargs):
        data = self.request.data.copy()
        clothes_id = data.get('clothes_id')  # Изменено здесь
        size = data.get('size')
        try:
            clothes = Clothes.objects.get(id=clothes_id)
        except Clothes.DoesNotExist:
            raise NotFound('Товар (одежда) с указанным ID не найден.')

        existing_item = CartItem.objects.filter(
            user=self.request.user, clothes=clothes
        ).first()

        # Pass the user's primary key (pk) to the serializer
        data['user'] = self.request.user.pk
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        if existing_item and size == existing_item.size:
            existing_item.quantity += 1
            existing_item.save(update_fields=['quantity'])
        else:
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
