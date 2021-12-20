from api.models.solution_booking import Solution, SolutionBooking
from django.core import mail


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
