from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from django_pandas.managers import DataFrameManager
from django_resized import ResizedImageField


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=10, null=True, blank=True)
    first_login = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        return str(self.user)

class Product(models.Model):
    product_id = models.IntegerField(default=0)
    name = models.CharField(max_length=250)
    category = models.CharField(max_length=250, blank=True, null=True)
    date_added = models.DateField(default=now)
    price = models.FloatField( blank=True, null=True)
    image = models.ImageField( upload_to="", default="")
##    name = models.CharField(max_length=100)
##    category = models.CharField(max_length=100)
##    date_added = models.DateField(default=now)
##    price = models.FloatField()
##    image = ResizedImageField(size=[500, 300], upload_to="", default="")
    objects = models.Manager()
    pdobjects = DataFrameManager() 

    def __str__(self):
        return self.name

class Feature(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    feature = models.CharField(max_length=1000, null=True, blank=True)

    def __str__(self):
        return str(self.product) + " Feature: " + self.feature

class Review(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE) 
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    content = models.TextField()
    tag = models.TextField(default=False,null=True,blank=True)
    posted_by =  models.TextField(default="",null=True,blank=True)
    posted_on =  models.TextField(default="",null=True,blank=True)
    votes_up =  models.IntegerField(default=0,null=True,blank=True)
    votes_down = models.IntegerField(default=0,null=True,blank=True)
    verified_purchase =  models.TextField(default="",null=True,blank=True)
    datetime = models.DateTimeField(default=now)

    def __str__(self):
        return str(self.customer) +  " Review: " + self.content

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    date_ordered = models.DateTimeField(default=now)
    complete = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)

    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        return total

    @property
    def get_cart_items(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total

class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=0)
    date_added = models.DateTimeField(default=now)

    def __str__(self):
        return str(self.order)

    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total

class UpdateOrder(models.Model):
    order_id = models.ForeignKey(Order, on_delete=models.CASCADE)
    desc = models.CharField(max_length=500)
    date = models.DateField(default=now)

    def __str__(self):
        return str(self.order_id)

class CheckoutDetail(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    phone_number = models.CharField(max_length=10, blank=True, null=True)
    total_amount = models.CharField(max_length=10, blank=True,null=True)
    address = models.CharField(max_length=300)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zipcode = models.CharField(max_length=100)
    payment = models.CharField(max_length=100, blank=True)
    date_added = models.DateTimeField(default=now)

    def __str__(self):
        return self.address

class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=50)
    phone = models.CharField(max_length=10)
    desc = models.CharField(max_length=1000)

    def __str__(self):
        return self.name


class Preferences(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product  = models.IntegerField(max_length=2, blank=True, null=True)
    category = models.CharField(max_length=100, blank=True, null=True)
    date_added = models.DateTimeField(default=now)
    objects = models.Manager()
    probjects = DataFrameManager()  # Pandas-Enabled Manager 

    def __str__(self):
        return str(self.customer)

    
