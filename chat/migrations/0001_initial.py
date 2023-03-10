# Generated by Django 4.1.7 on 2023-02-17 12:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Chat",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("rejected", models.BooleanField(default=False)),
                (
                    "candidate",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="candidate_chats",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Order",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=512)),
                (
                    "status",
                    models.PositiveSmallIntegerField(
                        choices=[
                            (0, "Draft"),
                            (1, "Published"),
                            (2, "Started"),
                            (3, "On Hold"),
                        ],
                        default=0,
                    ),
                ),
                (
                    "candidate",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="candidates",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Message",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "msg_type",
                    models.PositiveSmallIntegerField(
                        choices=[
                            (0, "Message"),
                            (1, "Warning"),
                            (2, "Status"),
                            (3, "Enter"),
                            (4, "Leave"),
                        ],
                        default=0,
                    ),
                ),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                ("message", models.TextField(blank=True, null=True)),
                ("unread", models.BooleanField(default=True)),
                (
                    "chat",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="chat.chat"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["timestamp"],
            },
        ),
        migrations.AddField(
            model_name="chat",
            name="order",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="chat.order"
            ),
        ),
    ]
