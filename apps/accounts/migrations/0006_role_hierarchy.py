# Generated migration for hierarchical role system

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_alter_user_user_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='role',
            name='parent',
            field=models.ForeignKey(
                blank=True,
                help_text='Parent role in organizational hierarchy',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='children',
                to='accounts.role'
            ),
        ),
        migrations.AddField(
            model_name='role',
            name='is_organizational_position',
            field=models.BooleanField(
                default=True,
                help_text='Whether this is an organizational position'
            ),
        ),
        migrations.AddField(
            model_name='role',
            name='level',
            field=models.IntegerField(
                default=0,
                help_text='Hierarchy level (0=top, increases downward)'
            ),
        ),
        migrations.AddIndex(
            model_name='role',
            index=models.Index(fields=['parent'], name='accounts_ro_parent__idx'),
        ),
        migrations.AddIndex(
            model_name='role',
            index=models.Index(fields=['level'], name='accounts_ro_level_idx'),
        ),
        migrations.AddIndex(
            model_name='role',
            index=models.Index(fields=['college', 'parent'], name='accounts_ro_college_parent_idx'),
        ),
    ]
