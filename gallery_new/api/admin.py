from django.contrib import admin
from .models import EntityFile, MediaFile, Thumbnail, Token, Quota, VerificationCode

admin.site.register(EntityFile)
admin.site.register(MediaFile)
admin.site.register(Thumbnail)
admin.site.register(VerificationCode)


@admin.register(Quota)
class QuotaAdmin(admin.ModelAdmin):

    readonly_fields = ['used']


@admin.register(Token)
class CustomTokenAdmin(admin.ModelAdmin):

    fields = ['user', 'expires', 'device', 'client']