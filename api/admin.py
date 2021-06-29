from django.contrib import admin
from django.db import models
from django.forms import TextInput
from guardian.shortcuts import get_objects_for_user

from guardian.admin import GuardedModelAdmin

from api.models import Tag, Asset, User, AssetQuestion, PricePlan


class TagInline(admin.TabularInline):
    model = Asset.tags.through
    autocomplete_fields = ['tag']


class PricePlanInline(admin.TabularInline):
    model = PricePlan
    # For other fields the detailed PricePlanAdmin will be used
    # Restricting number of inline fields to make the admin display compact
    fields = ['name', 'price', 'per']


class UserAdmin(admin.ModelAdmin):
    inlines = []


class TagAdmin(admin.ModelAdmin):
    model = Tag
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',), }


class AssetQuestionAdmin(admin.ModelAdmin):
    model = AssetQuestion
    autocomplete_fields = ['asset']
    search_fields = ['asset__name', 'question']


class PricePlanAdmin(admin.ModelAdmin):
    model = PricePlan
    autocomplete_fields = ['asset']
    search_fields = ['asset__name', 'name']


class AssetAdmin(GuardedModelAdmin):
    model = Asset
    user_owned_objects_field = 'owner'
    user_can_access_owned_objects_only = False
    list_display = ('name', 'slug', 'website', 'short_description', 'owner')
    search_fields = ['name', ]
    prepopulated_fields = {'slug': ('name',), }
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '128'})},
    }
    inlines = [
        TagInline,
        PricePlanInline
    ]


# Admin site headers
admin.site.site_header = 'TaggedWeb Admin'

# Register Models
admin.site.register(User, UserAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Asset, AssetAdmin)
admin.site.register(AssetQuestion, AssetQuestionAdmin)
admin.site.register(PricePlan, PricePlanAdmin)
