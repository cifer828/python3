#!/usr/bin/env python

import os
import django
import random
from faker import Faker

# Configure settings for project
# Need to run this before calling models from application!
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'first_project.settings')

django.setup()

# faker pop script
fake_gen = Faker()
topics = ["Search", "Social", "Marketplace", "News", "Games"]

# must import these three model after setting env
from first_app.models import AccessRecord, Webpage, Topic
from homework.models import Users


def add_topic():
    t = Topic.objects.get_or_create(top_name=random.choice(topics))[0]
    # t.save()
    return t


def populate(n=5):
    print('populating {} entries into database'.format(n))

    for entry in range(n):
        # get the topic or the entry
        top = add_topic()

        # create fake data for that entry
        fake_url = fake_gen.url()
        fake_date = fake_gen.date()
        fake_name = fake_gen.company()

        # !! Webpage.topic and AccessRecord.name are foreign key, so we should pass an model object instead of a string
        # create the new webpage entry
        webpg = Webpage.objects.get_or_create(topic=top, url=fake_url, name=fake_name)[0]

        # create a fake access record for that webpage
        acc_rec = AccessRecord.objects.get_or_create(name=webpg, date=fake_date)[0]

    print("populating complete")


def populate_user(n=10):
    """
    generate n fake users
    """
    print("begin populating {} users".format(n))
    fake = Faker()
    # clear current data
    Users.objects.all().delete()
    for _ in range(n):
        fake_name = fake.name().split()
        fake_email = fake.email()

        Users.objects.get_or_create(first_name=fake_name[0], last_name=fake_name[1], email=fake_email)

    print("populating complete")


if __name__ == "__main__":
    populate_user(20)
    # populate(20)
