from django.urls import path
from social_network_app import views

app_name = 'social_network_app'
urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('friendships/', views.FriendsView.as_view(), name='friendships'),
    path('user_items_list/<int:user_id>/', views.UserItemsView.as_view(), name='user_items_list'),
    path('borrow_requests/', views.BorrowRequestsView.as_view(), name='borrow_requests'),
    path('all_items/', views.AllItemsView.as_view(), name='all_items'),
    path('all_users/', views.AllUsersView.as_view(), name='all_users'),
    path('item/<int:item_id>/', views.ItemView.as_view(), name='item'),
]
