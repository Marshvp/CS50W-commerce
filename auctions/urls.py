from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create_page, name="create_page"),
    path("category", views.category_page, name="category_page"),
    path("watchlist", views.watchlist_page, name="watchlist_page"),
    path("listing/<int:listing_id>/", views.listing_page, name="listing_page"),
    path("listing/<int:listing_id>/bid/", views.place_bid, name="place_bid"),
    path('add_to_watchlist/<int:listing_id>/', views.add_to_watchlist, name='add_to_watchlist'),
    path("watchlist", views.watchlist_page, name="watchlist_page"),
    path('category/', views.category_page, name='category'),
    path('category/<str:category_name>/', views.category_page, name='category'),
    path('addcomment/<int:listing_id>/', views.addcomment,name='addcomment'),
    path('closeauction/<int:listing_id>/', views.closeauction, name='closeauction'),
    
]
