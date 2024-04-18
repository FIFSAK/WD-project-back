from store.models import Clothes, CartItem, Size, ClothesSize
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from rest_framework.exceptions import ValidationError


class ClothesSizeSerializer(serializers.ModelSerializer):
    size = serializers.SlugRelatedField(slug_field='size', read_only=True)

    class Meta:
        model = ClothesSize
        fields = ('size', 'quantity')


class ClothesSerializer(serializers.ModelSerializer):
    type_category = serializers.SlugRelatedField(
        read_only=True,
        slug_field='category_name'
    )
    sizes = ClothesSizeSerializer(
        source='clothes_sizes', many=True, read_only=True
    )

    class Meta:
        model = Clothes
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("username", "password",)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise ValidationError("A user with that username already exists.")
        return value

    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
            password=make_password(validated_data['password'])
        )
        user.save()
        return user


class SizeSerializer(serializers.Serializer):
    class Meta:
        model = Size
        fields = '__all__'


class CartItemClothesSerializer(serializers.ModelSerializer):
    type_category = serializers.SlugRelatedField(
        read_only=True,
        slug_field='category_name'
    )
    sizes = ClothesSizeSerializer(
        source='clothes_sizes', many=True, read_only=True
    )

    class Meta:
        model = Clothes
        fields = '__all__'
        # exclude = ('sizes',)  # Исключаем поле sizes


class CartItemSerializer(serializers.ModelSerializer):
    clothes = CartItemClothesSerializer(read_only=True)  # Используем кастомный сериализатор
    clothes_id = serializers.IntegerField(write_only=True)

    size = serializers.SlugRelatedField(
        slug_field='size',
        queryset=Size.objects.all()
    )
    class Meta:
        model = CartItem
        fields = '__all__'


    def create(self, validated_data):
        clothes_id = validated_data.pop('clothes_id')
        clothes = Clothes.objects.get(id=clothes_id)
        cart_item = CartItem.objects.create(clothes=clothes, **validated_data)
        return cart_item


class TypeSerializer(serializers.Serializer):
    class Meta:
        model = Clothes
        fields = '__all__'
