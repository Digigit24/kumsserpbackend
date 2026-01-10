"""
Management command to check RabbitMQ connection.
"""
from django.core.management.base import BaseCommand
from apps.communication.rabbitmq_queue import get_rabbitmq


class Command(BaseCommand):
    help = 'Check RabbitMQ connection and setup'

    def handle(self, *args, **options):
        self.stdout.write("Checking RabbitMQ connection...")

        client = get_rabbitmq()

        if client.is_connected():
            self.stdout.write(
                self.style.SUCCESS('✓ RabbitMQ connection successful')
            )

            # Try to get channel
            channel = client.get_channel()
            if channel and not channel.is_closed:
                self.stdout.write(
                    self.style.SUCCESS('✓ RabbitMQ channel operational')
                )

                # Test queue declaration
                try:
                    test_queue = 'test_queue_check'
                    channel.queue_declare(
                        queue=test_queue,
                        durable=False,
                        auto_delete=True
                    )
                    self.stdout.write(
                        self.style.SUCCESS('✓ Queue operations working')
                    )

                    # Cleanup test queue
                    channel.queue_delete(queue=test_queue)
                    self.stdout.write(
                        self.style.SUCCESS('✓ All RabbitMQ checks passed!')
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'✗ Queue operations failed: {e}')
                    )
                    return
            else:
                self.stdout.write(
                    self.style.ERROR('✗ RabbitMQ channel not available')
                )
                return
        else:
            self.stdout.write(
                self.style.ERROR('✗ RabbitMQ connection failed')
            )
            self.stdout.write(
                self.style.WARNING(
                    '\nMake sure RabbitMQ is running:\n'
                    '  Windows: rabbitmq-server.bat\n'
                    '  Linux/Mac: sudo systemctl start rabbitmq-server\n'
                    '  Docker: docker run -d -p 5672:5672 -p 15672:15672 rabbitmq:management\n'
                )
            )
            return

        self.stdout.write(
            self.style.SUCCESS(
                '\n=================================\n'
                'RabbitMQ is ready for use!\n'
                '=================================\n'
            )
        )
