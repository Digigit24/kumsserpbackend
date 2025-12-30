# Generated manually
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
        ('teachers', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='assignment',
            name='college',
            field=models.ForeignKey(
                default=3,  # Set default to your college ID
                help_text='College reference',
                on_delete=django.db.models.deletion.CASCADE,
                related_name='assignments',
                to='core.college'
            ),
            preserve_default=False,
        ),
    ]
