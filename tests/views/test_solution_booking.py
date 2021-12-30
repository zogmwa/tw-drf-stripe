from api.models.solution_booking import Solution, SolutionBooking

from django.core import mail
from api.views.solutions import SolutionViewSet

SOLUTIONBOOKINGS_BASE_ENDPOINT = 'http://127.0.0.1:8000/solution_bookings/'
SOLUTIONS_BASE_ENDPOINT = 'http://127.0.0.1:8000/solutions/'


class TestFetchingSolutionBooking:
    def test_authenticated_user_should_be_fetching_solution_bookings_list(
        self, authenticated_client, example_solution, user_and_password
    ):
        solution_booking = SolutionBooking.objects.create(
            solution=example_solution,
            booked_by=user_and_password[0],
            manager=user_and_password[0],
            status='Pending',
        )
        solution_booking.save()

        response = authenticated_client.get(SOLUTIONBOOKINGS_BASE_ENDPOINT)

        assert response.status_code == 200
        assert response.data[0]['solution']['id'] == example_solution.id
        assert response.data[0]['booked_by'] == user_and_password[0].id


class TestCreatingSolutionBooking:
    def check_mail_content(self, email_content, subject, to, body):
        assert email_content.to == to
        assert email_content.subject == subject
        assert email_content.body == body

    def test_send_email_when_solution_booking_status_is_complete(
        self,
        admin_user,
        user_and_password_with_first_last_name,
        example_consultation_solution,
    ):
        example_solution_booking = SolutionBooking.objects.create(
            solution=example_consultation_solution,
            booked_by=user_and_password_with_first_last_name[0],
        )
        example_solution_booking.save()
        email_content = mail.outbox[0]
        self.check_mail_content(
            email_content,
            '{} needs consultation'.format(example_consultation_solution.title),
            [admin_user.email],
            '{} {} user needs consultation about {}'.format(
                user_and_password_with_first_last_name[0].first_name,
                user_and_password_with_first_last_name[0].last_name,
                example_consultation_solution.title,
            ),
        )


class TestDeletingSolutionBooking:
    def test_decrease_pending_solution_booking_fulfillment_count_of_solution(
        self, mocker, authenticated_client, example_solution, user_and_password
    ):
        mocker.patch.object(
            SolutionViewSet,
            '_get_solutions_db_qs_via_elasticsearch_query',
            return_value=Solution.objects.all(),
        )
        example_solution_booking = SolutionBooking.objects.create(
            solution=example_solution,
            booked_by=user_and_password[0],
            status=SolutionBooking.Status.PENDING,
        )

        example_solution_booking.delete()
        solution_list_url = '{}{}/'.format(
            SOLUTIONS_BASE_ENDPOINT, example_solution.slug
        )
        response = authenticated_client.get(solution_list_url)

        assert response.status_code == 200
        assert response.data['bookings_pending_fulfillment_count'] == 0


class TestChangeStatus:
    def test_creating_started_at_field_when_status_from_pending_to_others(
        self,
        admin_user,
        user_and_password,
        example_solution,
    ):
        example_solution_booking = SolutionBooking.objects.create(
            solution=example_solution,
            booked_by=user_and_password[0],
            status=SolutionBooking.Status.PENDING,
        )
        example_solution_booking.status = SolutionBooking.Status.IN_PROGRESS
        example_solution_booking.save()

        contract_instance = SolutionBooking.objects.get(id=example_solution_booking.id)

        assert contract_instance.started_at is not None

    def test_contract_status_when_creating_or_updating_contract_status(
        self, mocker, authenticated_client, user_and_password, example_solution
    ):
        mocker.patch.object(
            SolutionViewSet,
            '_get_solutions_db_qs_via_elasticsearch_query',
            return_value=Solution.objects.all(),
        )

        example_solution_booking = SolutionBooking.objects.create(
            solution=example_solution,
            booked_by=user_and_password[0],
        )
        # When solution contract is created at first, pending count will not increase.
        solution_list_url = '{}{}/'.format(
            SOLUTIONS_BASE_ENDPOINT, example_solution.slug
        )
        response = authenticated_client.get(solution_list_url)
        assert response.status_code == 200
        assert response.data['bookings_pending_fulfillment_count'] == 0

        # When solution contract status is changed from CANCELLED to other status, pending count will increase.
        example_solution_booking.status = SolutionBooking.Status.PENDING
        example_solution_booking.save()
        solution_list_url = '{}{}/'.format(
            SOLUTIONS_BASE_ENDPOINT, example_solution.slug
        )
        response = authenticated_client.get(solution_list_url)
        assert response.status_code == 200
        assert response.data['bookings_pending_fulfillment_count'] == 1

        # When solution contract status is changed to COMPLETED, pending count will decrease.
        example_solution_booking.status = SolutionBooking.Status.COMPLETED
        example_solution_booking.save()
        solution_list_url = '{}{}/'.format(
            SOLUTIONS_BASE_ENDPOINT, example_solution.slug
        )
        response = authenticated_client.get(solution_list_url)
        assert response.status_code == 200
        assert response.data['bookings_pending_fulfillment_count'] == 0

        # When solution contract is deleted and its status is COMPLETED, pending count will not decrease.
        SolutionBooking.objects.filter(id=example_solution_booking.id).delete()
        solution_list_url = '{}{}/'.format(
            SOLUTIONS_BASE_ENDPOINT, example_solution.slug
        )
        response = authenticated_client.get(solution_list_url)
        assert response.status_code == 200
        assert response.data['bookings_pending_fulfillment_count'] == 0
