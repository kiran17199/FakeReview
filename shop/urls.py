from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("cart/", views.cart, name="cart"),
    path("checkout/", views.checkout, name="checkout"),
    path("update_item/", views.updateItem, name="update_item"),
    path("product_view/<int:myid>/", views.product_view, name="product_view"),
    path("search/", views.search, name="search"),
    path("tracker/", views.tracker, name="tracker"),
    path("contact/", views.contact, name="contact"),
    path("loggedin_contact/", views.loggedin_contact, name="loggedin_contact"),
    path("register/", views.register, name="register"),
    path("preferences/", views.preferences, name="preferences"),
    path("change_password/", views.change_password, name="change_password"),
    path("login/", views.Login, name="login"),
    path("logout/", views.Logout, name="logout"),
    path('product_upload/', views.product_upload, name="product_upload"),
    path('feature_upload/', views.feature_upload, name="feature_upload"),
    path('review_upload/', views.review_upload, name="review_upload"),
    path("product_price/<int:prod_id>/", views.product_price, name="product_price"),
    path("payment/<str:address>/<str:city>/<str:state>/<str:zipcode>/<str:phone_number>/<str:payment>/", views.payment, name="payment"),
]
