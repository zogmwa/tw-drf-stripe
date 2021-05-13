from django.contrib import admin
from guardian.shortcuts import get_objects_for_user

from guardian.admin import GuardedModelAdmin

from api.models import Tag, Asset, User


class TagInline(admin.TabularInline):
    model = Asset.tags.through


class UserAdmin(admin.ModelAdmin):
    inlines = []


class TagAdmin(admin.ModelAdmin):
    model = Tag
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',), }


class AssetAdmin(GuardedModelAdmin):
    model = Asset
    # user_owned_objects_field = 'owner'
    # user_can_access_owned_objects_only = True
    list_display = ('name', 'company', 'website')
    search_fields = ['name', ]
    autocomplete_fields = ['tags']
    inlines = [
        TagInline
    ]


# Admin site headers
admin.site.site_header = 'TaggedWeb Admin'

# Register Models
admin.site.register(User, UserAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Asset, AssetAdmin)
