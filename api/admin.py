from django.contrib import admin
from django.db import models
from django.forms import TextInput

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
    AssetClaim,
)
from api.models.asset_review import AssetReview
from api.models.asset_snapshot import AssetSnapshot
from api.models.asset_attribute_vote import AssetAttributeVote
from api.models.solution import Solution
from api.models.solution_vote import SolutionVote
from api.models.solution_booking import SolutionBooking
from api.models.solution_bookmark import SolutionBookmark
from api.models.organization import Organization
from api.models.solution_question import SolutionQuestion
from api.models.newsletter_contact import NewsLetterContact
from api.models.solution_review import SolutionReview


class TagInline(admin.TabularInline):
    model = Asset.tags.through
    autocomplete_fields = ['tag']


class SolutionTagInline(admin.TabularInline):
    model = Solution.tags.through
    autocomplete_fields = ['tag']


class SolutionInLine(admin.TabularInline):
    model = Asset.solutions.through
    autocomplete_fields = ['solution']


class AssetInlineWithinSolution(admin.TabularInline):
    model = Asset.solutions.through
    autocomplete_fields = ['asset']
    verbose_name = "Related Software"
    verbose_name_plural = "Related Softwares"


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


class SolutionQuestionInline(admin.TabularInline):
    model = SolutionQuestion
    fields = ['title', 'primary_answer', 'submitted_by']


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
        SolutionInLine,
        CustomerOrganizationInLine,
    ]


class AssetReviewAdmin(admin.ModelAdmin):
    model = AssetReview
    autocomplete_fields = ['asset', 'user']
    search_fields = ['asset__name']


class SolutionReviewAdmin(admin.ModelAdmin):
    model = SolutionReview
    autocomplete_fields = ['solution', 'user']
    search_fields = ['solution__name']


class AssetVoteAdmin(admin.ModelAdmin):
    model = AssetVote
    autocomplete_fields = ['asset', 'user']
    search_fields = ['asset__name', 'user']


class AttributeAdmin(admin.ModelAdmin):
    model = Attribute
    autocomplete_fields = ['submitted_by']
    search_fields = ['name']


class AttributeVoteAdmin(admin.ModelAdmin):
    model = AssetAttributeVote
    autocomplete_fields = ['asset', 'user', 'attribute']
    search_fields = ['asset__name', 'attribute__name']


class AssetQuestionVoteAdmin(admin.ModelAdmin):
    model = AssetQuestionVote
    autocomplete_fields = ['user', 'question']
    search_fields = ['question__asset__name', 'question__title']


class AssetClaimAdmin(admin.ModelAdmin):
    model = AssetClaim
    autocomplete_fields = ['asset']
    search_fields = ['asset__name', 'title', 'status']
    list_display = ('asset', 'status', 'user_comment')


class SolutionAdmin(admin.ModelAdmin):
    model = Solution
    autocomplete_fields = [
        'organization',
        'point_of_contact',
        'assets',
        'stripe_product',
        'pay_now_price',
    ]
    search_fields = ['title']
    list_display = ('title', 'type', 'organization', 'livemode')
    list_filter = (
        'type',
        'stripe_product__livemode',
    )
    inlines = [
        AssetInlineWithinSolution,
        SolutionTagInline,
        SolutionQuestionInline,
    ]
    readonly_fields = ('livemode', 'pay_now_price_unit_amount')


class SolutionBookingAdmin(admin.ModelAdmin):
    model = SolutionBooking

    def livemode_display(self, obj):
        return obj.solution.livemode

    livemode_display.short_description = "livemode"
    autocomplete_fields = [
        'booked_by',
        'manager',
    ]
    list_display = ('booked_by', 'status', 'created', 'livemode_display')


class SolutionQuestionAdmin(admin.ModelAdmin):
    model = SolutionQuestion
    autocomplete_fields = ['solution']
    search_fields = ['solution__title', 'title']


class SolutionVoteAdmin(admin.ModelAdmin):
    model = SolutionVote
    autocomplete_fields = ['solution', 'user']
    search_fields = ['solution__name', 'user']


class SolutionBookmarkAdmin(admin.ModelAdmin):
    model = SolutionBookmark
    autocomplete_fields = ['solution', 'user']
    search_fields = ['solution__name', 'user']


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
admin.site.register(AssetAttributeVote, AttributeVoteAdmin)
admin.site.register(AssetQuestionVote, AssetQuestionVoteAdmin)
admin.site.register(AssetClaim, AssetClaimAdmin)
admin.site.register(Solution, SolutionAdmin)
admin.site.register(SolutionBooking, SolutionBookingAdmin)
admin.site.register(SolutionQuestion, SolutionQuestionAdmin)
admin.site.register(SolutionVote, SolutionVoteAdmin)
admin.site.register(SolutionBookmark, SolutionBookmarkAdmin)
admin.site.register(NewsLetterContact)
admin.site.register(SolutionReview, SolutionReviewAdmin)
