# Generated by Django 3.1.1 on 2020-09-12 17:06

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
            name='Match',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('home_team', models.CharField(max_length=40)),
                ('away_team', models.CharField(max_length=40)),
            ],
        ),
        migrations.CreateModel(
            name='SoccerStat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('stat_type', models.CharField(choices=[('goal', 'Goal'), ('assist', 'Assist'), ('yellow', 'Yellow Card'), ('red', 'Red Card'), ('sub off', 'Substitute Off'), ('sub on', 'Substitute On'), ('kcoins', 'kCoins')], max_length=10)),
                ('value', models.IntegerField()),
                ('stat_uuid', models.CharField(max_length=36)),
                ('side', models.CharField(blank=True, choices=[('home', 'Home'), ('away', 'Away')], max_length=4)),
                ('match', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='soccer.match')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
