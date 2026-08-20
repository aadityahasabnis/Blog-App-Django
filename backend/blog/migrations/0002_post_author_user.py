from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def move_posts_to_users(apps, schema_editor):
    Author = apps.get_model("blog", "Author")
    Post = apps.get_model("blog", "Post")
    User = apps.get_model("auth", "User")

    for author in Author.objects.all().iterator():
        user = User.objects.filter(email__iexact=author.email).first()
        if user is None:
            username = author.name.strip() or author.email.split("@", 1)[0]
            base_username = username[:150]
            username = base_username
            suffix = 1
            while User.objects.filter(username=username).exists():
                suffix_text = f"-{suffix}"
                username = f"{base_username[:150 - len(suffix_text)]}{suffix_text}"
                suffix += 1

            user = User.objects.create(
                username=username,
                email=author.email,
                first_name=author.name,
                password="!",
            )

        Post.objects.filter(author_id=author.id).update(author_id=user.id)


def reverse_move_posts(apps, schema_editor):
    # The old Author rows cannot be reconstructed reliably from User rows.
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("blog", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RunPython(move_posts_to_users, reverse_move_posts),
        migrations.AlterField(
            model_name="post",
            name="author",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="posts",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.DeleteModel(name="Author"),
    ]
