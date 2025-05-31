import random

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify
from faker import Faker

from accounts.models import UserProfile
from properties.models import (
    Feature,
    Inquiry,
    Location,
    Property,
    PropertyImage,
    PropertyType,
)

# Initialize Faker for Lao data, fallback to en_US if Lao provider is limited
# Note: Faker's Lao provider might be limited.
# You might get English-like names or need to customize.
try:
    fake = Faker("lo_LA")
except AttributeError:
    fake = Faker()  # Fallback to default (en_US)


class Command(BaseCommand):
    help = "Seeds the database with sample data"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write("Deleting old data...")
        models_to_clear = [
            Inquiry,
            PropertyImage,
            Property,
            Feature,
            Location,
            PropertyType,
            UserProfile,
            User,
        ]
        for m in models_to_clear:
            m.objects.all().delete()

        self.stdout.write("Creating new data...")

        # --- Create Users and UserProfiles ---
        users = []
        admin_user = User.objects.create_superuser(
            username="admin",
            email="admin@mywayproduction.com",
            password="passwd1234",
            first_name="Admin",
            last_name="User",
        )
        admin_user.profile.user_type = "admin"
        admin_user.profile.phone = fake.phone_number()
        admin_user.profile.save()
        users.append(admin_user)
        self.stdout.write(f"Created Admin: {admin_user.username}")

        agent_users = []
        for i in range(3):  # Create 3 agents
            first_name = fake.first_name()
            last_name = fake.last_name()
            username = f"{slugify(first_name)}_{slugify(last_name)}_{i}".lower()
            if User.objects.filter(username=username).exists():  # ensure username is unique
                username = f"{username}_{random.randint(100,999)}"

            agent = User.objects.create_user(
                username=username,
                email=fake.email(),
                password="passwd1234",
                first_name=first_name,
                last_name=last_name,
            )
            agent.profile.user_type = "agent"
            agent.profile.phone = fake.phone_number()
            agent.profile.bio = fake.paragraph(nb_sentences=3)
            agent.profile.address = fake.address().replace("\n", ", ")
            agent.profile.facebook = f"https://facebook.com/{username}"
            agent.profile.save()
            users.append(agent)
            agent_users.append(agent)
            self.stdout.write(f"Created Agent: {agent.username}")

        customer_users = []
        for i in range(5):  # Create 5 customers
            first_name = fake.first_name()
            last_name = fake.last_name()
            username = f"{slugify(first_name)}_{slugify(last_name)}_cust_{i}".lower()
            if User.objects.filter(username=username).exists():
                username = f"{username}_{random.randint(100,999)}"

            customer = User.objects.create_user(
                username=username,
                email=fake.email(),
                password="passwd1234",
                first_name=first_name,
                last_name=last_name,
            )
            # UserProfile created by signal
            customer.profile.phone = fake.phone_number()
            customer.profile.save()
            users.append(customer)
            customer_users.append(customer)
            self.stdout.write(f"Created Customer: {customer.username}")

        # --- Create Property Types ---
        property_type_names = ["ເຮືອນ", "ອາພາດເມັນ", "ດິນ", "ອາຄານການຄ້າ", "ຫ້ອງແຖວ"]
        property_types = []
        for name in property_type_names:
            pt = PropertyType.objects.create(name=name, description=fake.sentence(nb_words=10))
            property_types.append(pt)
            self.stdout.write(f"Created Property Type: {pt.name}")

        # --- Create Locations ---
        # Using more specific Lao locations
        location_data = [
            {"name": "ສີຫອມ", "city": "ຈັນທະບູລີ", "state": "ນະຄອນຫຼວງວຽງຈັນ", "zip_code": "01000"},
            {"name": "ທາດຫຼວງ", "city": "ໄຊເສດຖາ", "state": "ນະຄອນຫຼວງວຽງຈັນ", "zip_code": "01000"},
            {"name": "ໂພນຕ້ອງ", "city": "ຈັນທະບູລີ", "state": "ນະຄອນຫຼວງວຽງຈັນ", "zip_code": "01000"},
            {
                "name": "ໃຈກາງເມືອງຫຼວງພະບາງ",
                "city": "ຫຼວງພະບາງ",
                "state": "ແຂວງຫຼວງພະບາງ",
                "zip_code": "06000",
            },
            {"name": "ປາກເຊ", "city": "ປາກເຊ", "state": "ແຂວງຈຳປາສັກ", "zip_code": "16000"},
        ]
        locations = []
        for loc_data in location_data:
            loc = Location.objects.create(
                name=loc_data["name"],
                city=loc_data["city"],
                state=loc_data["state"],
                zip_code=loc_data["zip_code"],
                latitude=fake.latitude(),
                longitude=fake.longitude(),
            )
            locations.append(loc)
            self.stdout.write(f"Created Location: {loc.name}")

        # --- Create Features ---
        feature_names_icons = [
            ("ສະລອຍນ້ຳ", "water"),  # Example Flowbite/Bootstrap icon name
            ("ບ່ອນຈອດລົດ", "car-sport"),
            ("ເຄື່ອງປັບອາກາດ", "snow"),
            ("ລະບຽງ", "apps"),
            ("ສວນ", "leaf"),
            ("ຄວາມປອດໄພ 24ຊມ", "shield-checkmark"),
            ("ເຟີນິເຈີຄົບຊຸດ", "bed"),
        ]
        features = []
        for name, icon in feature_names_icons:
            feat = Feature.objects.create(name=name, icon=icon)
            features.append(feat)
            self.stdout.write(f"Created Feature: {feat.name}")

        # --- Create Properties ---
        properties_list = []
        for i in range(15):  # Create 15 properties
            prop_title = (
                f"{random.choice(property_type_names)}ງາມທີ່ {random.choice(locations).name} #{i+1}"
            )
            prop = Property.objects.create(
                title=prop_title,
                property_type=random.choice(property_types),
                description=fake.paragraph(nb_sentences=5),
                price=random.randint(50000, 500000),
                status=random.choice([s[0] for s in Property.STATUS_CHOICES]),
                area=random.randint(50, 500),
                bedrooms=random.randint(1, 5),
                bathrooms=random.randint(1, 3),
                garages=random.randint(0, 2),
                location=random.choice(locations),
                address=f"{fake.street_address()}, {random.choice(locations).city}",
                # For main_image, you'd typically handle file uploads.
                # For seeding, we'll leave it blank or point to a placeholder.
                # main_image='placeholders/property_main.jpg', # if you have a placeholder
                agent=random.choice(agent_users),
                is_featured=random.choice([True, False, False]),  # Make featured less common
            )
            # Add some random features
            prop.features.set(random.sample(features, k=random.randint(2, 5)))
            properties_list.append(prop)
            self.stdout.write(f"Created Property: {prop.title}")

            # --- Create Property Images for each property ---
            for j in range(random.randint(1, 5)):  # 1 to 5 images per property
                PropertyImage.objects.create(
                    property=prop,
                    # image=f'placeholders/gallery_{j+1}.jpg', # if you have placeholders
                    caption=fake.sentence(nb_words=4),
                    is_primary=(j == 0),  # Make the first image primary
                    order=j,
                )
            self.stdout.write(f"  Added {prop.images.count()} images to {prop.title}")

        # --- Create Inquiries ---
        for i in range(20):  # Create 20 inquiries
            selected_property = random.choice(properties_list)
            inquirer_user = random.choice(users)  # Can be any user, or None
            Inquiry.objects.create(
                property=selected_property,
                name=inquirer_user.get_full_name() or fake.name(),
                email=inquirer_user.email or fake.email(),
                phone=inquirer_user.profile.phone or fake.phone_number(),
                message=fake.paragraph(nb_sentences=3),
                status=random.choice([s[0] for s in Inquiry.STATUS_CHOICES]),
                user=(
                    inquirer_user if random.choice([True, False]) else None
                ),  # Randomly assign user
            )
            self.stdout.write(f"Created Inquiry for: {selected_property.title}")

        self.stdout.write(self.style.SUCCESS("Successfully seeded database!"))
