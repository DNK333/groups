from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Article, Product, CustomUser, Comment


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {'fields': ('phone', 'birth_data')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Дополнительная информация', {'fields': ('phone', 'birth_data')}),
    )


admin.site.register(Article)
admin.site.register(Product)
admin.site.register(Comment)
