from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Student, Parent
import random
import string


# -----------------------------
# Utility: Generate random password
# -----------------------------
def generate_password(length=8):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


# -----------------------------
# Auto-create User for Students
# -----------------------------
@receiver(post_save, sender=Student)
def create_student_user(sender, instance, created, **kwargs):
    if created and instance.user is None:
        # Base username
        base_username = f"{instance.first_name.lower()}.{instance.last_name.lower()}"
        username = base_username
        counter = 1

        # Ensure username is unique
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        # Generate password
        password = generate_password()

        # Create user
        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=instance.first_name,
            last_name=instance.last_name,
        )

        # Link user to student
        instance.user = user
        instance.save()

        # Store password temporarily for display
        instance.generated_password = password


# -----------------------------
# Auto-create User for Parents
# -----------------------------
@receiver(post_save, sender=Parent)
def create_parent_user(sender, instance, created, **kwargs):
    if created and instance.user is None:
        # Base username
        base_username = f"{instance.first_name.lower()}.{instance.last_name.lower()}.parent"
        username = base_username
        counter = 1

        # Ensure username is unique
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        # Generate password
        password = generate_password()

        # Create user
        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=instance.first_name,
            last_name=instance.last_name,
            email=instance.email,
        )

        # Link user to parent
        instance.user = user
        instance.save()

        # Store password temporarily for display
        instance.generated_password = password
