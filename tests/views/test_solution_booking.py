from api.models.solution_booking import Solution, SolutionBooking

from django.core import mail

SOLUTIONS_BASE_ENDPOINT = 'http://127.0.0.1:8000/solution_bookings/'


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

        response = authenticated_client.get(SOLUTIONS_BASE_ENDPOINT)

        assert response.status_code == 200
        assert response.data[0]['solution']['id'] == example_solution.id
        assert response.data[0]['booked_by'] == user_and_password[0].id


class TestCreatingSolutionBooking:
    def check_mail_content(self, email_content, subject, to, body):
        assert email_content.to == to
        assert email_content.subject == subject
        assert email_content.body == body

    def test_send_email_when_solution_booking_status_is_complete(
        self, admin_user, user_and_password_with_first_last_name, example_solution
    ):
        example_solution.type = Solution.Type.CONSULTATION
        example_solution.save()
        example_solution_booking = SolutionBooking.objects.create(
            solution=example_solution,
            booked_by=user_and_password_with_first_last_name[0],
        )
        example_solution_booking.save()
        email_content = mail.outbox[0]
        self.check_mail_content(
            email_content,
            '{} needs consultation'.format(example_solution.title),
            [admin_user.email],
            '{} {} user needs consultation about {}'.format(
                user_and_password_with_first_last_name[0].first_name,
                user_and_password_with_first_last_name[0].last_name,
                example_solution.title,
            ),
        )
