from datetime import date, time

from django.test import TestCase

from apps.core.models import College
from apps.core.utils import set_current_college_id, clear_current_college_id
from apps.accounts.models import User, UserType
from apps.communication.models import (
    Notice,
    NoticeVisibility,
    Event,
    EventRegistration,
    MessageTemplate,
    BulkMessage,
    MessageLog,
    NotificationRule,
    ChatMessage,
)


class CommunicationDummyDataTest(TestCase):
    """Build a dummy communication graph and verify relationships and signals."""

    def setUp(self):
        self.college = College.objects.create(
            code="COM",
            name="Communication College",
            short_name="COM",
            email="info@com.test",
            phone="9999999995",
            address_line1="123 Com St",
            city="City",
            state="State",
            pincode="000004",
            country="Testland",
        )
        set_current_college_id(self.college.id)

        self.user = User.objects.create_user(
            username="user_com",
            email="user@com.test",
            password="dummy-pass",
            first_name="Com",
            last_name="User",
            college=self.college,
            user_type=UserType.TEACHER,
            is_active=True,
        )
        self.other_user = User.objects.create_user(
            username="user2_com",
            email="user2@com.test",
            password="dummy-pass",
            first_name="Com2",
            last_name="User2",
            college=self.college,
            user_type=UserType.TEACHER,
            is_active=True,
        )

        self.notice = Notice.objects.create(
            college=self.college,
            title="Holiday Notice",
            content="College closed on Friday",
            publish_date=date(2025, 6, 1),
            is_published=True,
            is_urgent=True,
        )
        self.visibility = NoticeVisibility.objects.create(
            notice=self.notice,
            target_type='all',
        )

        self.event = Event.objects.create(
            college=self.college,
            title="Tech Fest",
            description="Annual tech fest",
            event_date=date(2025, 7, 10),
            start_time=time(10, 0),
            end_time=time(17, 0),
            registration_required=True,
        )
        self.event_reg = EventRegistration.objects.create(
            event=self.event,
            user=self.user,
            registration_date=date(2025, 6, 5),
        )

        self.template = MessageTemplate.objects.create(
            college=self.college,
            name="General",
            code="GEN",
            message_type="email",
            content="Hello {{name}}",
        )
        self.bulk = BulkMessage.objects.create(
            college=self.college,
            template=self.template,
            title="Bulk Announcement",
            message_type="email",
            recipient_type="teachers",
            total_recipients=1,
            status="pending",
            created_by=self.user,
            updated_by=self.user,
        )
        self.chat = ChatMessage.objects.create(
            sender=self.user,
            receiver=self.other_user,
            message="Hi there!",
        )

    def tearDown(self):
        clear_current_college_id()

    def test_dummy_graph_created(self):
        self.assertEqual(Notice.objects.count(), 1)
        self.assertEqual(NoticeVisibility.objects.count(), 1)
        self.assertEqual(Event.objects.count(), 1)
        self.assertEqual(EventRegistration.objects.count(), 1)
        self.assertEqual(MessageTemplate.objects.count(), 1)
        self.assertEqual(BulkMessage.objects.count(), 1)
        self.assertGreaterEqual(MessageLog.objects.count(), 1)
        self.assertGreaterEqual(NotificationRule.objects.count(), 1)
        self.assertEqual(ChatMessage.objects.count(), 1)

        # Bulk processing updates
        self.bulk.refresh_from_db()
        self.assertEqual(self.bulk.status, 'completed')
        self.assertGreaterEqual(self.bulk.sent_count, 1)

        # Chat read marker
        self.assertFalse(self.chat.is_read)
        self.chat.mark_read()
        self.chat.refresh_from_db()
        self.assertTrue(self.chat.is_read)

        # __str__ calls
        str(self.notice)
        str(self.visibility)
        str(self.event)
        str(self.event_reg)
        str(self.template)
        str(self.bulk)
        str(MessageLog.objects.first())
        str(NotificationRule.objects.first())
        str(self.chat)
