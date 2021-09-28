from django.contrib import admin
from django.db import models
from django.forms import TextInput
from guardian.shortcuts import get_objects_for_user

from guardian.admin import GuardedModelAdmin

from api.models import (
    Tag,
    Asset,
    User,
    AssetQuestion,
    PricePlan,
    AssetVote,
    Attribute,
    AssetQuestionVote,
    ClaimAsset,
)
from api.models.asset_review import AssetReview
from api.models.asset_snapshot import AssetSnapshot
from api.models.attribute_vote import AttributeVote
from api.models.organization import Organization


class TagInline(admin.TabularInline):
    model = Asset.tags.through
    autocomplete_fields = ['tag']


class CustomerOrganizationInLine(admin.TabularInline):
    model = Asset.customer_organizations.through
    autocomplete_fields = ['organization']


class AttributeInline(admin.TabularInline):
    model = Asset.attributes.through
    autocomplete_fields = ['attribute']


class AssetSnapshotInline(admin.TabularInline):
    model = AssetSnapshot
    # For other fields the detailed PricePlanAdmin will be used
    # Restricting number of inline fields to make the admin display compact
    fields = ['url']


class PricePlanInline(admin.TabularInline):
    model = PricePlan
    # For other fields the detailed PricePlanAdmin will be used
    # Restricting number of inline fields to make the admin display compact
    fields = ['name', 'price', 'per']


class UserAdmin(admin.ModelAdmin):
    search_fields = ['username']
    inlines = []


class TagAdmin(admin.ModelAdmin):
    model = Tag
    search_fields = ['name']
    prepopulated_fields = {
        'slug': ('name',),
    }


class AssetQuestionAdmin(admin.ModelAdmin):
    model = AssetQuestion
    autocomplete_fields = ['asset']
    search_fields = ['asset__name', 'title']


class PricePlanAdmin(admin.ModelAdmin):
    model = PricePlan
    autocomplete_fields = ['asset']
    search_fields = ['asset__name', 'name']


class OrganizationAdmin(admin.ModelAdmin):
    model = Organization
    search_fields = ['name']


class AssetAdmin(GuardedModelAdmin):
    model = Asset
    user_owned_objects_field = 'owner'
    user_can_access_owned_objects_only = False
    list_display = ('name', 'slug', 'website', 'short_description', 'owner')
    search_fields = [
        'name',
    ]
    autocomplete_fields = ['owner_organization', 'submitted_by', 'owner']
    prepopulated_fields = {
        'slug': ('name',),
    }
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '128'})},
    }
    inlines = [
        TagInline,
        AttributeInline,
        AssetSnapshotInline,
        PricePlanInline,
        CustomerOrganizationInLine,
    ]


class AssetReviewAdmin(admin.ModelAdmin):
    model = AssetReview
    autocomplete_fields = ['asset', 'user']
    search_fields = ['asset__name']


class AssetVoteAdmin(admin.ModelAdmin):
    model = AssetVote
    autocomplete_fields = ['asset', 'user']
    search_fields = ['asset__name', 'user']


class AttributeAdmin(admin.ModelAdmin):
    model = Attribute
    autocomplete_fields = ['submitted_by']
    search_fields = ['name']


class AttributeVoteAdmin(admin.ModelAdmin):
    model = AttributeVote
    autocomplete_fields = ['asset', 'user', 'attribute']
    search_fields = ['asset__name', 'attribute__name']


class AssetQuestionVoteAdmin(admin.ModelAdmin):
    model = AssetQuestionVote
    autocomplete_fields = ['user', 'question']
    search_fields = ['question__asset__name', 'question__title']


# Admin site headers
admin.site.site_header = 'TaggedWeb Admin'

# Register Models
admin.site.register(User, UserAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Organization, OrganizationAdmin)
admin.site.register(Asset, AssetAdmin)
admin.site.register(AssetQuestion, AssetQuestionAdmin)
admin.site.register(PricePlan, PricePlanAdmin)
admin.site.register(AssetReview, AssetReviewAdmin)
admin.site.register(AssetVote, AssetVoteAdmin)
admin.site.register(Attribute, AttributeAdmin)
admin.site.register(AttributeVote, AttributeVoteAdmin)
admin.site.register(AssetQuestionVote, AssetQuestionVoteAdmin)
