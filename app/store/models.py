import boto3
from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User

from app import settings


class Size(models.Model):
    size = models.CharField(max_length=10)

    def __str__(self):
        return self.size


class Type(models.Model):
    category_name = models.CharField(max_length=300)

    def __str__(self):
        return self.category_name


class Clothes(models.Model):
    type_category = models.ForeignKey(Type, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/', null=True)
    name = models.TextField()
    vendor_code = models.BigIntegerField()
    price = models.IntegerField()
    count = models.IntegerField()
    sizes = models.ManyToManyField(Size)

    def delete(self, *args, **kwargs):
        # Connect to S3
        s3 = boto3.client('s3',
                          aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)

        # Delete the file from S3
        if self.image:
            s3.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=self.image.name)
        super(Clothes, self).delete(*args, **kwargs)

    def __str__(self):
        return str(self.name) + " " + str(self.type_category )


class ClothesAdmin(admin.ModelAdmin):
    def delete_queryset(self, request, queryset):
        for obj in queryset:
            obj.delete()


class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    clothes = models.ForeignKey(Clothes, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    size = models.CharField(max_length=100)
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
