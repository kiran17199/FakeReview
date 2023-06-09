# Generated by Django 4.1.7 on 2023-03-12 12:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="review",
            name="posted_by",
            field=models.TextField(blank=True, default="", null=True),
        ),
        migrations.AddField(
            model_name="review",
            name="posted_on",
            field=models.TextField(blank=True, default="", null=True),
        ),
        migrations.AddField(
            model_name="review",
            name="verified_purchase",
            field=models.TextField(blank=True, default="", null=True),
        ),
        migrations.AddField(
            model_name="review",
            name="votes_down",
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name="review",
            name="votes_up",
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]
