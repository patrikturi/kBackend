from django.contrib import admin
from users.models import User, UserDetails


class UserAdmin(admin.ModelAdmin):
    pass


class UserDetailsAdmin(admin.ModelAdmin):
    pass


admin.site.register(User, UserAdmin)
admin.site.register(UserDetails, UserDetailsAdmin)
