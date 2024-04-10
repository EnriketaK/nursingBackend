# Generated by Django 5.0.2 on 2024-02-28 19:38

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AdmissionForm',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('liveAloneNo', models.BooleanField(default=False)),
                ('liveAloneYes', models.BooleanField(default=False)),
                ('liveAloneLift', models.BooleanField(default=False)),
                ('liveAloneFloor', models.CharField(blank=True, default='', max_length=240)),
                ('obliationsNo', models.BooleanField(default=False)),
                ('obliationsYes', models.BooleanField(default=False)),
                ('relativeSurname1', models.CharField(blank=True, default='', max_length=100)),
                ('relativeFname1', models.CharField(blank=True, default='', max_length=100)),
                ('relativePhone1', models.CharField(blank=True, default='', max_length=20)),
                ('relativeRel1', models.CharField(blank=True, default='', max_length=100)),
                ('relativeSurname2', models.CharField(blank=True, default='', max_length=100)),
                ('relativeFname2', models.CharField(blank=True, default='', max_length=100)),
                ('relativePhone2', models.CharField(blank=True, default='', max_length=20)),
                ('relativeRel2', models.CharField(blank=True, default='', max_length=100)),
                ('relativeSurname3', models.CharField(blank=True, default='', max_length=100)),
                ('relativeFname3', models.CharField(blank=True, default='', max_length=100)),
                ('relativePhone3', models.CharField(blank=True, default='', max_length=20)),
                ('relativeRel3', models.CharField(blank=True, default='', max_length=100)),
                ('careNo', models.BooleanField(default=False)),
                ('careYes', models.BooleanField(default=False)),
                ('careDegree1', models.BooleanField(default=False)),
                ('careDegree2', models.BooleanField(default=False)),
                ('careDegree3', models.BooleanField(default=False)),
                ('careDegree4', models.BooleanField(default=False)),
                ('careDegree5', models.BooleanField(default=False)),
                ('hospitalizedNo', models.BooleanField(blank=True, default='', max_length=100)),
                ('hospitalizedYes', models.BooleanField(blank=True, default='', max_length=100)),
                ('hospAbroadPlace', models.CharField(blank=True, default='', max_length=100)),
                ('hospAbroadTime', models.CharField(blank=True, default='', max_length=100)),
                ('commNoImpairment', models.BooleanField(default=False)),
                ('commForeignLang', models.BooleanField(default=False)),
                ('commForeignLangYes', models.BooleanField(default=False)),
                ('commForeignLangNo', models.BooleanField(default=False)),
                ('commSignLang', models.BooleanField(default=False)),
                ('commDisorder', models.BooleanField(default=False)),
                ('commTrach', models.BooleanField(default=False)),
                ('visionLeft', models.BooleanField(default=False)),
                ('visionRight', models.BooleanField(default=False)),
                ('blindnessLeft', models.BooleanField(default=False)),
                ('blindnessRight', models.BooleanField(default=False)),
                ('visualAidLeft', models.BooleanField(default=False)),
                ('visualAidRight', models.BooleanField(default=False)),
                ('hearingNoImp', models.BooleanField(default=False)),
                ('hearingAidRight', models.BooleanField(default=False)),
                ('hearingAidLeft', models.BooleanField(default=False)),
                ('hearingHardRight', models.BooleanField(default=False)),
                ('hearingHardLeft', models.BooleanField(default=False)),
                ('deafnessRight', models.BooleanField(default=False)),
                ('deafnessLeft', models.BooleanField(default=False)),
                ('disorNoImp', models.BooleanField(default=False)),
                ('disorTime', models.BooleanField(default=False)),
                ('disorPlace', models.BooleanField(default=False)),
                ('disorPerson', models.BooleanField(default=False)),
                ('understNoImp', models.BooleanField(default=False)),
                ('understConfusion', models.BooleanField(default=False)),
                ('understNerv', models.BooleanField(default=False)),
                ('understAltered', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='FormSummaryDto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.CharField(blank=True, default='', max_length=5000)),
                ('admissionFormFk', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Tutorial',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='', max_length=70)),
                ('description', models.CharField(default='', max_length=200)),
                ('published', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='FormSummary',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.CharField(blank=True, default='', max_length=5000)),
                ('admissionFormFk', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tutorials.admissionform')),
            ],
        ),
    ]
