# Generated manually for SSE chat enhancement

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('communication', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Create Conversation model
        migrations.CreateModel(
            name='Conversation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Timestamp when the record was created')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='Timestamp when the record was last updated')),
                ('is_active', models.BooleanField(db_index=True, default=True, help_text='Indicates if the record is active (soft delete)')),
                ('last_message', models.TextField(blank=True, help_text='Last message preview', null=True)),
                ('last_message_at', models.DateTimeField(blank=True, help_text='Last message timestamp', null=True)),
                ('unread_count_user1', models.IntegerField(default=0, help_text='Unread count for user1')),
                ('unread_count_user2', models.IntegerField(default=0, help_text='Unread count for user2')),
                ('created_by', models.ForeignKey(blank=True, help_text='User who created this record', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_created', to=settings.AUTH_USER_MODEL)),
                ('last_message_by', models.ForeignKey(blank=True, help_text='User who sent last message', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='last_messages', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, help_text='User who last updated this record', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(class)s_updated', to=settings.AUTH_USER_MODEL)),
                ('user1', models.ForeignKey(help_text='First user in conversation', on_delete=django.db.models.deletion.CASCADE, related_name='conversations_as_user1', to=settings.AUTH_USER_MODEL)),
                ('user2', models.ForeignKey(help_text='Second user in conversation', on_delete=django.db.models.deletion.CASCADE, related_name='conversations_as_user2', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'conversation',
            },
        ),

        # Create TypingIndicator model
        migrations.CreateModel(
            name='TypingIndicator',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_typing', models.BooleanField(default=True, help_text='Currently typing')),
                ('timestamp', models.DateTimeField(auto_now=True, help_text='Last update timestamp')),
                ('conversation_partner', models.ForeignKey(help_text='User being typed to', on_delete=django.db.models.deletion.CASCADE, related_name='typing_to', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(help_text='User who is typing', on_delete=django.db.models.deletion.CASCADE, related_name='typing_indicators', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'typing_indicator',
            },
        ),

        # Add new fields to ChatMessage
        migrations.AddField(
            model_name='chatmessage',
            name='conversation',
            field=models.ForeignKey(blank=True, help_text='Related conversation', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='communication.conversation'),
        ),
        migrations.AddField(
            model_name='chatmessage',
            name='attachment_type',
            field=models.CharField(blank=True, help_text='Attachment type (image/video/document)', max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='chatmessage',
            name='delivered_at',
            field=models.DateTimeField(blank=True, help_text='Delivered time', null=True),
        ),

        # Alter ChatMessage message field to allow blank
        migrations.AlterField(
            model_name='chatmessage',
            name='message',
            field=models.TextField(blank=True, default='', help_text='Message content'),
        ),

        # Add indexes for Conversation
        migrations.AddIndex(
            model_name='conversation',
            index=models.Index(fields=['user1', 'user2'], name='conversation_user1_user2_idx'),
        ),
        migrations.AddIndex(
            model_name='conversation',
            index=models.Index(fields=['last_message_at'], name='conversation_last_msg_idx'),
        ),

        # Add unique constraint for Conversation
        migrations.AlterUniqueTogether(
            name='conversation',
            unique_together={('user1', 'user2')},
        ),

        # Add indexes for TypingIndicator
        migrations.AddIndex(
            model_name='typingindicator',
            index=models.Index(fields=['conversation_partner', 'timestamp'], name='typing_partner_time_idx'),
        ),

        # Add unique constraint for TypingIndicator
        migrations.AlterUniqueTogether(
            name='typingindicator',
            unique_together={('user', 'conversation_partner')},
        ),

        # Add index for ChatMessage conversation field
        migrations.AddIndex(
            model_name='chatmessage',
            index=models.Index(fields=['conversation', '-timestamp'], name='chatmsg_conv_time_idx'),
        ),
    ]
