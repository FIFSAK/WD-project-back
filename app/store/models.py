import boto3
from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
from app import settings


class Size(models.Model):
    size = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.size


class Type(models.Model):
    category_name = models.CharField(max_length=300)

    def __str__(self):
        return self.category_name


class Image(models.Model):
    image = models.ImageField(upload_to='images/', null=True)

    def delete(self, *args, **kwargs):
        # Connect to S3
        s3 = boto3.client('s3',
                          aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)

        # Delete the file from S3
        if self.image:
            s3.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=self.image.name)
        super().delete(*args, **kwargs)


class Clothes(models.Model):
    type_category = models.ForeignKey(Type, on_delete=models.CASCADE)
    images = models.ManyToManyField(Image)
    name = models.TextField()
    vendor_code = models.BigIntegerField()
    price = models.IntegerField()
    sizes = models.ManyToManyField(Size, through='ClothesSize')

    # def delete(self, *args, **kwargs):
    #     # Connect to S3
    #     s3 = boto3.client('s3',
    #                       aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    #                       aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
    #
    #     # Delete the file from S3
    #     if self.image:
    #         s3.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=self.image.name)
    #     super(Clothes, self).delete(*args, **kwargs)

    def __str__(self):
        return str(self.name) + " " + str(self.type_category)


class ClothesSize(models.Model):
    clothes = models.ForeignKey(Clothes, on_delete=models.CASCADE, related_name='clothes_sizes')
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.clothes.name} - {self.size.size} - {self.quantity}"


class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    clothes = models.ForeignKey(Clothes, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    size = models.ForeignKey(Size, on_delete=models.CASCADE, related_name='cartItem_size')


class ClothesSizeInline(admin.TabularInline):
    model = ClothesSize
    extra = 1


class ClothesAdmin(admin.ModelAdmin):
    inlines = (ClothesSizeInline,)

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            obj.delete()
#
# class Trousers(Clothes):
#
#     def __str__(self):
#         return self.name
#
#
# class TShirtsAndTops(Clothes):
#
#     def __str__(self):
#         return self.name
#
#
# class Jacket(Clothes):
#
#     def __str__(self):
#         return self.name
#
#
# class ShirtsAndBlouses(Clothes):
#
#     def __str__(self):
#         return self.name
#
#
# class Dresses(Clothes):
#
#     def __str__(self):
#         return self.name
#
#
# class OverallsJacketsRaincoatsCardigans(Clothes):
#
#     def __str__(self):
#         return self.name
#
#
# class PantsuitsShortsSkirts(Clothes):
#
#     def __str__(self):
#         return self.name
#
#
# class Jeans(Clothes):
#
#     def __str__(self):
#         return self.name
#
#
# class Underwear(Clothes):
#
#     def __str__(self):
#         return self.name
