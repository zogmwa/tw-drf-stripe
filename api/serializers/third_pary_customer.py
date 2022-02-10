import stripe
from djstripe.models import Customer as StripeCustomer
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from api.models import ThirdPartyCustomer


class ThirdPartyCustomerSerializer(ModelSerializer):
    customer_email = serializers.EmailField()

    class Meta:
        model = ThirdPartyCustomer
        fields = [
            'customer_uid',
            'customer_email',
        ]
        extra_kwargs = {
            'name': {'validators': []},
        }

    def create(self, validated_data):
        self._set_organization_based_on_authenticated_user(validated_data)
        # Nested objects in DRF are not supported/are-read only by default so we have to pop this and create snapshot
        # objects and associate them with the asset separately after creation of the asset.
        customer_email = validated_data.pop('customer_email', '')
        customer_email = customer_email.strip()
        self._create_stripe_customer_and_associate_with_third_party_customer(
            customer_email
        )
        third_party_customer = super().create(validated_data)

        return third_party_customer

    def _set_organization_based_on_authenticated_user(self, validated_data):
        """
        Organization will be set based on the organization of the user who is making this request. Requests to create
        ThirdPartyCustomer's will be performed by ThirdParty Organization staff users.
        """
        # Mutate validated_data to set submitted_by to logged-in user if we have one
        logged_in_user = self.context['request'].user
        if logged_in_user:
            validated_data['organization'] = self.context['request'].user.organization

    def _create_stripe_customer_and_associate_with_third_party_customer(
        self, customer_email
    ):
        if customer_email:
            stripe_customer_object = stripe.Customer.create(email=customer_email)
            djstripe_customer = StripeCustomer.sync_from_stripe_data(
                stripe_customer_object
            )
            self.stripe_customer = djstripe_customer
