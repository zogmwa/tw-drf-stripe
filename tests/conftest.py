import djstripe.models
import pytest, stripe, collections
from django.conf import settings
from djstripe.models import Product, Price, Event
from django.test import Client
from api.models.solution_booking import SolutionBooking
from api.models.webhooks_stripe import (
    product_created_handler,
    price_created_handler,
)
from api.models import (
    Asset,
    User,
    Tag,
    Attribute,
    AssetAttributeVote,
    AssetQuestionVote,
    AssetSnapshot,
    PricePlan,
    Solution,
    SolutionQuestion,
)
from django.db.models.signals import post_save, pre_save
from django.core.signals import request_finished


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass


@pytest.fixture(autouse=True)
def patch_elasticsearch(mocker):
    # Patch elasticsearch so that whenever a db save happens an elastic search index update request does not fail
    # in the tests. Later on figure out how to patch this in a better way with some data so that we can still have a
    # mock index that can be used for testing search flows.
    mocker.patch('elasticsearch.Transport.perform_request')


@pytest.fixture
def example_stripe_product():
    return Product.objects.create(
        name='test stripe product', description='description for stripe product'
    )


@pytest.fixture
def example_stripe_price(example_stripe_product):
    return Price.objects.create(
        currency='usd',
        product_id=example_stripe_product.id,
        unit_amount=20000,
        unit_amount_decimal=20000.000000000000,
        active=True,
    )


@pytest.fixture
def example_stripe_product_create_event() -> Event:
    data = {
        "object": {
            "id": "prod_Kszx5SEOfUDUQZ",
            "object": "product",
            "active": True,
            "attributes": [],
            "created": 1641068051,
            "description": "Mailchimp is an email marketing tool. This solution will be focused on running an email marketing campaign using Mailchimp given an email template and an excel sheet with emails and other information.",
            "images": [],
            "livemode": False,
            "metadata": {},
            "name": "Run an email marketing campaign given an excel sheet with Mailchimp",
            "package_dimensions": None,
            "shippable": None,
            "statement_descriptor": None,
            "tax_code": None,
            "type": "service",
            "unit_label": None,
            "updated": 1641068051,
            "url": None,
        },
    }
    return Event(data=data)


@pytest.fixture
def example_stripe_price_create_event(
    example_stripe_product_create_event: Event,
) -> Event:

    # A stripe price is always associated with a stripe product, so a corresponding product must exist for this stripe
    # price.
    product_dict = example_stripe_product_create_event.data['object']
    Product.sync_from_stripe_data(product_dict)

    data = {
        "object": {
            "id": "price_1KDDxvJNxEeFbcNwlynxIXH2",
            "object": "price",
            "active": True,
            "billing_scheme": "per_unit",
            "created": 1641068051,
            "currency": "usd",
            "livemode": False,
            "lookup_key": None,
            "metadata": {},
            "nickname": None,
            "product": product_dict["id"],
            "recurring": None,
            "tax_behavior": "unspecified",
            "tiers_mode": None,
            "transform_quantity": None,
            "type": "one_time",
            "unit_amount": 100000,
            "unit_amount_decimal": "100000",
        }
    }
    return Event(data=data, type="price.created")


@pytest.fixture
def example_stripe_price_archive_event(
    example_stripe_product_create_event: Event, example_stripe_price_create_event: Event
) -> Event:

    # A stripe price is always associated with a stripe product, so a corresponding product must exist for this stripe
    # price.
    product_dict = example_stripe_product_create_event.data['object']
    Product.sync_from_stripe_data(product_dict)
    price_archive_event = example_stripe_price_create_event
    price_archive_event.data['object']['active'] = False
    return price_archive_event


@pytest.fixture
def example_stripe_price_delete_event(
    example_stripe_price_create_event: Event,
) -> Event:

    # in order to delete a price, we need to create it first.
    price_dict = example_stripe_price_create_event.data['object']
    Price.sync_from_stripe_data(price_dict)
    # created response like this from: https://stripe.com/docs/api/coupons/delete
    data = {
        "object": {
            "id": example_stripe_price_create_event.data['object']['id'],
            "object": "price",
            "deleted": True,
        }
    }
    return Event(data=data, type="price.deleted")


@pytest.fixture
def example_stripe_customer_object():
    example_stripe_customer = {
        "id": "cus_Kzn1wGfMcrNJy4",
        "object": "customer",
        "address": None,
        "balance": 0,
        "created": 1642598630,
        "currency": "usd",
        "default_source": None,
        "delinquent": False,
        "description": "This is test customer",
        "discount": None,
        "email": None,
        "invoice_prefix": "99775FF",
        "invoice_settings": {
            "custom_fields": None,
            "default_payment_method": None,
            "footer": None,
        },
        "livemode": False,
        "metadata": {},
        "name": '',
        "next_invoice_sequence": 1,
        "phone": None,
        "preferred_locales": [],
        "shipping": None,
        "tax_exempt": "none",
    }

    return example_stripe_customer


@pytest.fixture
def example_stripe_customer_has_default_payment_method_object():
    example_stripe_customer_has_default_payment_method = {
        "id": "cus_Kzn1wGfMcrNJy4",
        "object": "customer",
        "address": None,
        "balance": 0,
        "created": 1642598630,
        "currency": "usd",
        "default_source": None,
        "delinquent": False,
        "description": "This is test customer",
        "discount": None,
        "email": None,
        "invoice_prefix": "99775FF",
        "invoice_settings": {
            "custom_fields": None,
            "default_payment_method": "pm_1KFFan2eZvKYlo2C50uGTC8w",
            "footer": None,
        },
        "livemode": False,
        "metadata": {},
        "name": '',
        "next_invoice_sequence": 1,
        "phone": None,
        "preferred_locales": [],
        "shipping": None,
        "tax_exempt": "none",
    }

    return example_stripe_customer_has_default_payment_method


@pytest.fixture
def example_stripe_customer_has_not_default_payment_method_object(
    example_stripe_customer_has_default_payment_method_object,
):
    example_stripe_customer_has_not_default_payment_method = {
        "id": example_stripe_customer_has_default_payment_method_object['id'],
        "object": "customer",
        "address": None,
        "balance": 0,
        "created": 1642598630,
        "currency": "usd",
        "default_source": None,
        "delinquent": False,
        "description": "This is test customer",
        "discount": None,
        "email": None,
        "invoice_prefix": "99775FF",
        "invoice_settings": {
            "custom_fields": None,
            "default_payment_method": None,
            "footer": None,
        },
        "livemode": False,
        "metadata": {},
        "name": '',
        "next_invoice_sequence": 1,
        "phone": None,
        "preferred_locales": [],
        "shipping": None,
        "tax_exempt": "none",
    }

    return example_stripe_customer_has_not_default_payment_method


@pytest.fixture
def example_stripe_attach_payment_method_customer_object_1():
    attached_payment_method = {
        "id": "pm_1KFFan2eZvKYlo2C50uGTC8w",
        "object": "payment_method",
        "billing_details": {
            "address": {
                "city": None,
                "country": None,
                "line1": None,
                "line2": None,
                "postal_code": None,
                "state": None,
            },
            "email": None,
            "name": '',
            "phone": None,
        },
        "card": {
            "brand": "visa",
            "checks": {
                "address_line1_check": None,
                "address_postal_code_check": None,
                "cvc_check": "unchecked",
            },
            "country": "US",
            "exp_month": 8,
            "exp_year": 9999,
            "fingerprint": "Xt5EWLLDS7FJjR1c",
            "funding": "credit",
            "generated_from": None,
            "last4": "4242",
            "networks": {"available": ["visa"], "preferred": None},
            "three_d_secure_usage": {"supported": True},
            "wallet": None,
        },
        "created": 1641550961,
        "customer": "cus_Kzn1wGfMcrNJy4",
        "livemode": False,
        "metadata": {"order_id": "673", "card": "amex"},
        "type": "card",
    }

    return attached_payment_method


@pytest.fixture
def example_stripe_detach_payment_method_customer_object_1(
    example_stripe_attach_payment_method_customer_object_1,
):
    detached_payment_method = {
        "billing_details": {
            "address": {
                "city": None,
                "country": None,
                "line1": None,
                "line2": None,
                "postal_code": "42424",
                "state": None,
            },
            "email": None,
            "name": "Test Customer",
            "phone": None,
        },
        "card": {
            "brand": "visa",
            "checks": {
                "address_line1_check": None,
                "address_postal_code_check": "pass",
                "cvc_check": "pass",
            },
            "country": "US",
            "exp_month": 4,
            "exp_year": 2024,
            "fingerprint": example_stripe_attach_payment_method_customer_object_1[
                'card'
            ]['fingerprint'],
            "funding": "credit",
            "generated_from": None,
            "last4": "4242",
            "networks": {"available": ["visa"], "preferred": None},
            "three_d_secure_usage": {"supported": True},
            "wallet": None,
        },
        "created": 1642782075,
        "customer": None,
        "id": example_stripe_attach_payment_method_customer_object_1['id'],
        "livemode": False,
        "metadata": {},
        "object": "payment_method",
        "type": "card",
    }

    return detached_payment_method


@pytest.fixture
def example_stripe_attach_payment_method_customer_object_2():
    attached_payment_method = {
        "id": "pm_1KFFan2eZvKYlo2C50uGTC9w",
        "object": "payment_method",
        "billing_details": {
            "address": {
                "city": None,
                "country": None,
                "line1": None,
                "line2": None,
                "postal_code": None,
                "state": None,
            },
            "email": None,
            "name": '',
            "phone": None,
        },
        "card": {
            "brand": "visa",
            "checks": {
                "address_line1_check": None,
                "address_postal_code_check": None,
                "cvc_check": "unchecked",
            },
            "country": "US",
            "exp_month": 8,
            "exp_year": 9999,
            "fingerprint": "Xt5EWLLDS7FJjR1e",
            "funding": "credit",
            "generated_from": None,
            "last4": "4242",
            "networks": {"available": ["visa"], "preferred": None},
            "three_d_secure_usage": {"supported": True},
            "wallet": None,
        },
        "created": 1641550961,
        "customer": "cus_Kzn1wGfMcrNJy4",
        "livemode": False,
        "metadata": {"order_id": "673", "card": "amex"},
        "type": "card",
    }

    return attached_payment_method


@pytest.fixture
def example_stripe_subscription_object(
    example_stripe_price_create_event,
    example_stripe_product_create_event,
    example_stripe_customer_has_default_payment_method_object,
):
    example_subscription = {
        "application_fee_percent": None,
        "automatic_tax": {"enabled": False},
        "billing_cycle_anchor": 1642693255,
        "billing_thresholds": None,
        "cancel_at": None,
        "cancel_at_period_end": False,
        "canceled_at": None,
        "collection_method": "charge_automatically",
        "created": 1642693255,
        "current_period_end": 9999999999,
        "current_period_start": 1643298055,
        "customer": example_stripe_customer_has_default_payment_method_object['id'],
        "days_until_due": None,
        "default_payment_method": None,
        "default_source": None,
        "default_tax_rates": [],
        "discount": None,
        "ended_at": None,
        "id": "sub_1KK2kuGAiB8oTF44Puf2fqSG",
        "items": {
            "data": [
                {
                    "billing_thresholds": None,
                    "created": 1642693256,
                    "id": "si_L02qrgsquQSjQe",
                    "metadata": {},
                    "object": "subscription_item",
                    "plan": {
                        "active": True,
                        "aggregate_usage": "last_during_period",
                        "amount": 10000,
                        "amount_decimal": "10000",
                        "billing_scheme": "per_unit",
                        "created": 1642512894,
                        "currency": "usd",
                        "id": example_stripe_price_create_event.data['object']['id'],
                        "interval": "week",
                        "interval_count": 1,
                        "livemode": False,
                        "metadata": {},
                        "nickname": None,
                        "object": "plan",
                        "product": example_stripe_product_create_event.data['object'][
                            'id'
                        ],
                        "tiers_mode": None,
                        "transform_usage": None,
                        "trial_period_days": None,
                        "usage_type": "metered",
                    },
                    "price": {
                        "active": True,
                        "billing_scheme": "per_unit",
                        "created": 1642512894,
                        "currency": "usd",
                        "id": example_stripe_price_create_event.data['object']['id'],
                        "livemode": False,
                        "lookup_key": None,
                        "metadata": {},
                        "nickname": None,
                        "object": "price",
                        "product": example_stripe_product_create_event.data['object'][
                            'id'
                        ],
                        "recurring": {
                            "aggregate_usage": "sum",
                            "interval": "week",
                            "interval_count": 1,
                            "trial_period_days": None,
                            "usage_type": "metered",
                        },
                        "tax_behavior": "unspecified",
                        "tiers_mode": None,
                        "transform_quantity": None,
                        "type": "recurring",
                        "unit_amount": 10000,
                        "unit_amount_decimal": "10000",
                    },
                    "subscription": "sub_1KK2kuGAiB8oTF44Puf2fqSG",
                    "tax_rates": [],
                }
            ],
            "has_more": False,
            "object": "list",
            "total_count": 1,
            "url": "/v1/subscription_items?subscription=sub_1KK2kuGAiB8oTF44Puf2fqSG",
        },
        "livemode": False,
        "metadata": {},
        "next_pending_invoice_item_invoice": None,
        "object": "subscription",
        "pause_collection": None,
        "payment_settings": {
            "payment_method_options": None,
            "payment_method_types": None,
        },
        "pending_invoice_item_interval": None,
        "pending_setup_intent": None,
        "pending_update": None,
        "plan": {
            "active": True,
            "aggregate_usage": "sum",
            "amount": 10000,
            "amount_decimal": "10000",
            "billing_scheme": "per_unit",
            "created": 1642512894,
            "currency": "usd",
            "id": example_stripe_price_create_event.data['object']['id'],
            "interval": "week",
            "interval_count": 1,
            "livemode": False,
            "metadata": {},
            "nickname": None,
            "object": "plan",
            "product": example_stripe_product_create_event.data['object']['id'],
            "tiers_mode": None,
            "transform_usage": None,
            "trial_period_days": None,
            "usage_type": "metered",
        },
        "quantity": 1,
        "schedule": None,
        "start_date": 1642693255,
        "status": "active",
        "transfer_data": None,
        "trial_end": None,
        "trial_start": None,
    }

    return example_subscription


@pytest.fixture
def example_stripe_invoice_event() -> Event:
    data = {
        "object": {
            "id": "in_1KOuwWGAiB8oTF44osF2bkWn",
            "object": "invoice",
            "account_country": "US",
            "account_name": "Taggedweb",
            "account_tax_ids": None,
            "amount_due": 2000,
            "amount_paid": 0,
            "amount_remaining": 2000,
            "application_fee_amount": None,
            "attempt_count": 0,
            "attempted": False,
            "auto_advance": False,
            "automatic_tax": {"enabled": False, "status": None},
            "billing_reason": "manual",
            "charge": None,
            "collection_method": "charge_automatically",
            "created": 1643854864,
            "currency": "usd",
            "custom_fields": None,
            "customer": "cus_L556Z0dXglWiDn",
            "customer_address": None,
            "customer_email": None,
            "customer_name": None,
            "customer_phone": None,
            "customer_shipping": None,
            "customer_tax_exempt": None,
            "customer_tax_ids": [],
            "default_payment_method": None,
            "default_source": None,
            "default_tax_rates": [],
            "description": "(created by Stripe CLI)",
            "discount": None,
            "discounts": [],
            "due_date": None,
            "ending_balance": None,
            "footer": None,
            "hosted_invoice_url": None,
            "invoice_pdf": None,
            "last_finalization_error": None,
            "lines": {
                "object": "list",
                "data": [
                    {
                        "id": "il_1KOuwVGAiB8oTF44VbqWjb73",
                        "object": "line_item",
                        "amount": 2000,
                        "currency": "usd",
                        "description": "(created by Stripe CLI)",
                        "discount_amounts": [],
                        "discountable": True,
                        "discounts": [],
                        "invoice_item": "ii_1KOuwVGAiB8oTF44BPmNQ6VD",
                        "livemode": False,
                        "metadata": {},
                        "period": {"end": 1643854863, "start": 1643854863},
                        "plan": None,
                        "price": {
                            "id": "price_1KOuwVGAiB8oTF44OC9CPL97",
                            "object": "price",
                            "active": False,
                            "billing_scheme": "per_unit",
                            "created": 1643854863,
                            "currency": "usd",
                            "livemode": False,
                            "lookup_key": None,
                            "metadata": {},
                            "nickname": None,
                            "product": "prod_L556D1gwX2fR55",
                            "recurring": None,
                            "tax_behavior": "unspecified",
                            "tiers_mode": None,
                            "transform_quantity": None,
                            "type": "one_time",
                            "unit_amount": 2000,
                            "unit_amount_decimal": "2000",
                        },
                        "proration": False,
                        "quantity": 1,
                        "subscription": None,
                        "tax_amounts": [],
                        "tax_rates": [],
                        "type": "invoiceitem",
                    }
                ],
                "has_more": False,
                "total_count": 1,
                "url": "/v1/invoices/in_1KOuwWGAiB8oTF44osF2bkWn/lines",
            },
            "livemode": False,
            "metadata": {},
            "next_payment_attempt": None,
            "number": None,
            "on_behalf_of": None,
            "paid": False,
            "paid_out_of_band": False,
            "payment_intent": None,
            "payment_settings": {
                "payment_method_options": None,
                "payment_method_types": None,
            },
            "period_end": 1643854864,
            "period_start": 1643854864,
            "post_payment_credit_notes_amount": 0,
            "pre_payment_credit_notes_amount": 0,
            "quote": None,
            "receipt_number": None,
            "starting_balance": 0,
            "statement_descriptor": None,
            "status": "draft",
            "status_transitions": {
                "finalized_at": None,
                "marked_uncollectible_at": None,
                "paid_at": None,
                "voided_at": None,
            },
            "subscription": None,
            "subtotal": 2000,
            "tax": None,
            "total": 2000,
            "total_discount_amounts": [],
            "total_tax_amounts": [],
            "transfer_data": None,
            "webhooks_delivered_at": None,
        }
    }
    return Event(data=data)


@pytest.fixture
def example_stripe_invoice_object():
    example_invoice = {
        "account_country": "US",
        "account_name": "Zogmwa Tech",
        "account_tax_ids": None,
        "amount_due": 2000,
        "amount_paid": 0,
        "amount_remaining": 2000,
        "application_fee_amount": None,
        "attempt_count": 0,
        "attempted": False,
        "auto_advance": False,
        "automatic_tax": {"enabled": False, "status": None},
        "billing_reason": "manual",
        "charge": None,
        "collection_method": "charge_automatically",
        "created": 1643854864,
        "currency": "usd",
        "custom_fields": None,
        "customer": "cus_L556Z0dXglWiDn",
        "customer_address": None,
        "customer_email": None,
        "customer_name": None,
        "customer_phone": None,
        "customer_shipping": None,
        "customer_tax_exempt": "none",
        "customer_tax_ids": [],
        "default_payment_method": None,
        "default_source": None,
        "default_tax_rates": [],
        "description": "(created by Stripe CLI)",
        "discount": None,
        "discounts": [],
        "due_date": None,
        "ending_balance": None,
        "footer": None,
        "hosted_invoice_url": None,
        "id": "in_1KOuwWGAiB8oTF44osF2bkWn",
        "invoice_pdf": None,
        "last_finalization_error": None,
        "lines": {
            "data": [
                {
                    "amount": 2000,
                    "currency": "usd",
                    "description": "(created by Stripe CLI)",
                    "discount_amounts": [],
                    "discountable": True,
                    "discounts": [],
                    "id": "il_1KOuwVGAiB8oTF44VbqWjb73",
                    "invoice_item": "ii_1KOuwVGAiB8oTF44BPmNQ6VD",
                    "livemode": False,
                    "metadata": {},
                    "object": "line_item",
                    "period": {"end": 1643854863, "start": 1643854863},
                    "plan": None,
                    "price": {
                        "active": False,
                        "billing_scheme": "per_unit",
                        "created": 1643854863,
                        "currency": "usd",
                        "id": "price_1KOuwVGAiB8oTF44OC9CPL97",
                        "livemode": False,
                        "lookup_key": None,
                        "metadata": {},
                        "nickname": None,
                        "object": "price",
                        "product": "prod_L556D1gwX2fR55",
                        "recurring": None,
                        "tax_behavior": "unspecified",
                        "tiers_mode": None,
                        "transform_quantity": None,
                        "type": "one_time",
                        "unit_amount": 2000,
                        "unit_amount_decimal": "2000",
                    },
                    "proration": False,
                    "quantity": 1,
                    "subscription": None,
                    "tax_amounts": [],
                    "tax_rates": [],
                    "type": "invoiceitem",
                }
            ],
            "has_more": False,
            "object": "list",
            "total_count": 1,
            "url": "/v1/invoices/in_1KOuwWGAiB8oTF44osF2bkWn/lines",
        },
        "livemode": False,
        "metadata": {},
        "next_payment_attempt": None,
        "number": None,
        "object": "invoice",
        "on_behalf_of": None,
        "paid": False,
        "paid_out_of_band": False,
        "payment_intent": None,
        "payment_settings": {
            "payment_method_options": None,
            "payment_method_types": None,
        },
        "period_end": 1643854864,
        "period_start": 1643854864,
        "post_payment_credit_notes_amount": 0,
        "pre_payment_credit_notes_amount": 0,
        "quote": None,
        "receipt_number": None,
        "starting_balance": 0,
        "statement_descriptor": None,
        "status": "draft",
        "status_transitions": {
            "finalized_at": None,
            "marked_uncollectible_at": None,
            "paid_at": None,
            "voided_at": None,
        },
        "subscription": None,
        "subtotal": 2000,
        "tax": None,
        "total": 2000,
        "total_discount_amounts": [],
        "total_tax_amounts": [],
        "transfer_data": None,
        "webhooks_delivered_at": None,
    }

    return example_invoice


@pytest.fixture
def example_stripe_usage_object():
    example_stripe_usage_object = {
        "id": "mbur_1KO6LTGAiB8oTF44M7V1QpQx",
        "livemode": False,
        "object": "usage_record",
        "quantity": 3,
        "subscription_item": "si_L30ndfFJV9NMiy",
        "timestamp": 1643660313,
    }

    return example_stripe_usage_object


@pytest.fixture
def example_event():
    # TODO: Rename to example_stripe_event
    data = {
        'object': {
            "id": "cs_test_5PIAqHlxs921ujN9ftgymLMyywUM55VhoRTgE09KWjs6KUYc0uT6y8bV",
            "object": "checkout.session",
            "expires_at": 1637391616,
            "livemode": False,
            "metadata": {},
            "mode": "payment",
            "payment_intent": "pi_3JxPZ8JNxEeFbcNw0exlygHf",
            "payment_method_options": {},
            "payment_method_types": ["card"],
            "payment_status": "paid",
            "success_url": "https://example.com/success",
        }
    }
    return Event(data=data)


@pytest.fixture
def example_asset():
    return Asset.objects.create(
        slug='mailchimp',
        name='Mailchimp',
        website='https://mailchimp.com/',
        short_description='bla bla',
        description='bla bla bla',
        promo_video='https://www.youtube.com/embed/Q0hi9d1W3Ag',
        is_published=True,
    )


@pytest.fixture
def example_solution(admin_user):
    return Solution.objects.create(
        slug='test-solution',
        title='Test Solution',
        type='I',
        description='bla bla bla',
        promo_video='https://www.youtube.com/embed/Q0hi9d1W3Ag',
        scope_of_work='bla bla bla',
        point_of_contact=admin_user,
    )


@pytest.fixture
def example_consultation_solution(admin_user):
    return Solution.objects.create(
        slug='test-solution',
        title='Test Solution',
        type=Solution.Type.CONSULTATION,
        description='bla bla bla',
        scope_of_work='bla bla bla',
        point_of_contact=admin_user,
    )


@pytest.fixture
def example_solution_booking(example_solution, admin_user):
    return SolutionBooking.objects.create(
        booked_by_id=admin_user.id,
        solution=example_solution,
        provider_notes='first solution booking',
    )


@pytest.fixture
def example_solution_booking2(example_solution, admin_user):
    return SolutionBooking.objects.create(
        booked_by_id=admin_user.id,
        solution=example_solution,
    )


# TODO: If we don't see the use for this ahead we can remove this later
def stripe_product_event(self, **params):
    dictionary = {
        "id": "prod_KkGmWqkik2VpYo",
        "stripe_id": "prod_KkGmWqkik2VpYo",
        "object": "product",
        "active": True,
        "created": 1639054823,
        "description": params['name'],
        "images": [],
        "livemode": False,
        "metadata": {},
        "name": params['name'],
        "package_dimensions": None,
        "shippable": None,
        "statement_descriptor": None,
        "tax_code": None,
        "unit_label": None,
        "updated": 1639054823,
        "url": None,
    }
    return collections.namedtuple("ObjectName", dictionary.keys())(*dictionary.values())


@pytest.fixture
def example_solution_question(example_solution):
    return example_solution.questions.create(
        title='test solution question',
    )


@pytest.fixture
def example_asset_2():
    return Asset.objects.create(
        slug='test-service-2',
        name='Test Service 2',
        is_published=True,
    )


@pytest.fixture
def example_asset_3():
    return Asset.objects.create(
        slug='test-service-3',
        name='Test Service 3',
        is_published=True,
    )


@pytest.fixture
def example_asset_4():
    return Asset.objects.create(
        slug='test-service-4',
        name='Test Service 4',
        is_published=True,
    )


@pytest.fixture
def example_featured_asset():
    return Asset.objects.create(
        slug='featured_asset',
        name='Featured Asset',
        is_homepage_featured=True,
    )


@pytest.fixture
def example_attribute(example_asset):
    return Attribute.objects.create(name='Test Attribute')


@pytest.fixture
def example_asset_attribute(example_asset):
    return example_asset.attributes.create(name='Test Asset Attribute')


@pytest.fixture
def example_asset_attribute2(example_asset):
    return example_asset.attributes.create(name='Test Asset Attribute2')


@pytest.fixture
def example_asset_customer_organization(example_asset):
    return example_asset.customer_organizations.create(
        name='Primer',
        logo_url='https://logo.clearbit.com/primer.io',
        website='https://primer.io/',
    )


@pytest.fixture
def example_asset_customer_organization2(example_asset):
    return example_asset.customer_organizations.create(name='Customer Organization2')


@pytest.fixture
def example_asset_tag(example_asset):
    return example_asset.tags.create(
        name='Test Tag', slug='test-tag', description='description'
    )


@pytest.fixture
def example_asset_tag2(example_asset):
    return example_asset.tags.create(name='Test Tag2', slug='test-tag1', description='')


@pytest.fixture
def example_asset_question(example_asset):
    return example_asset.questions.create(title='Test Asset Question')


@pytest.fixture
def example_asset_attribute_vote(
    user_and_password, example_asset, example_asset_attribute
):
    user = user_and_password[0]
    return AssetAttributeVote.objects.create(
        user=user, asset=example_asset, attribute=example_asset_attribute
    )


@pytest.fixture
def example_asset_question_vote(user_and_password, example_asset_question):
    user = user_and_password[0]
    return AssetQuestionVote.objects.create(user=user, question=example_asset_question)


@pytest.fixture
def example_tag():
    return Tag.objects.create(slug='tag', name='tag_name')


@pytest.fixture
def example_featured_tag():
    return Tag.objects.create(
        slug='featured_tag', name='Featured Tag', is_homepage_featured=True
    )


@pytest.fixture
def user_and_password():
    username = 'username'
    password = 'password'
    user = User.objects.create(username=username)
    user.set_password(password)
    user.save()
    return user, password


@pytest.fixture
def user_and_password_with_first_last_name():
    password = 'password'
    user = User.objects.create(
        username='testuser',
        first_name='Test',
        last_name='User',
        email='test@taggedweb.com',
    )
    user.set_password(password)
    user.save()
    return user, password


@pytest.fixture
def user_and_password_2():
    username = 'username2'
    password = 'password2'
    user = User.objects.create(username=username)
    user.set_password(password)
    user.save()
    return user, password


@pytest.fixture
def admin_user_and_password():
    username = 'admin'
    password = 'password'
    user = User.objects.create(username=username)
    user.set_password(password)
    user.is_superuser = True
    user.save()
    return user, password


@pytest.fixture
def staff_user_and_password():
    username = 'staff'
    password = 'password'
    user = User.objects.create(username=username)
    user.set_password(password)
    user.is_staff = True
    user.save()
    return user, password


@pytest.fixture()
def authenticated_client(user_and_password):
    """
    If you need the corresponding user which this authenticated_client represents check user_and_password fixture"
    """
    client = Client()
    client.login(username=user_and_password[0].username, password=user_and_password[1])
    assert client.session['_auth_user_id'] == str(user_and_password[0].id)
    return client


@pytest.fixture()
def authenticated_client_2(user_and_password_2):
    """
    If you need the corresponding user which this authenticated_client represents check user_and_password fixture"
    """
    client = Client()
    client.login(
        username=user_and_password_2[0].username, password=user_and_password_2[1]
    )
    assert client.session['_auth_user_id'] == str(user_and_password_2[0].id)
    return client


@pytest.fixture()
def unauthenticated_client():
    client = Client()
    return client


@pytest.fixture()
def example_snapshot(example_asset):
    return AssetSnapshot.objects.create(
        asset=example_asset,
        url='https://eep.io/images/yzco4xsimv0y/2N9sFG6PG9HDHwJ4mtvS7k/19f56d3cdae2403d604e65f4b3db3ce7/00_-_Hero.png',
    )


@pytest.fixture()
def example_price_plan(example_asset):
    return PricePlan.objects.create(
        asset=example_asset,
        name="standard",
        summary="standard",
        currency="USD",
    )
