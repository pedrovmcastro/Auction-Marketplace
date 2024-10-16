from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("categories", views.categories, name="categories"),
    path("categories/<int:category_id>", views.category_matches, name="category_matches"),
    path("listing/<int:listing_id>", views.listing_details, name="listing_details"),
    path("create", views.create, name="create"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("listing/<int:listing_id>/toggle_watchlist", views.toggle_watchlist, name='toggle_watchlist'),
    path("listing/<int:listing_id>/comment", views.comment, name='comment'),
    path("listing/<int:listing_id>/bid", views.bid, name="bid"),
    path("listing/<int:listing_id>/close_auction", views.close_auction, name="close_auction")
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
