from django.urls import path
from . import views


app_name = 'blog'

urlpatterns = [
    # Основные маршруты профиля
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/<str:username>/', views.user_profile, name='profile'),

    # Маршруты категорий
    path('<slug:category_slug>/', views.category_posts, name='category_posts'),

    # Маршруты создания и просмотра постов
    path('posts/create/', views.create_post, name='create_post'),
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),

    # Маршруты комментариев к постам
    path('posts/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('posts/<int:post_id>/edit_comment/<int:comment_id>/', 
         views.edit_comment, name='edit_comment'),
    path('posts/<int:post_id>/delete_comment/<int:comment_id>/', 
         views.delete_comment, name='delete_comment'),

    # Маршруты редактирования и удаления постов
    path('posts/<int:post_id>/edit/', views.edit_post, name='edit_post'),
    path('posts/<int:post_id>/delete/', views.delete_post, name='delete_post'),

    # Главная страница
    path('', views.index, name='index'),
]
