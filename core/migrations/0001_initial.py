# Generated by Django 3.2.15 on 2022-09-26 14:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Stock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ticker', models.CharField(max_length=10)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('market_cap', models.FloatField()),
                ('open', models.FloatField(null=True)),
                ('previous_close', models.FloatField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='StockExchange',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('NYSE', 'New York Stock Exchange'), ('TSX', 'Toronto Stock Exchange'), ('LSE', 'London Stock Exchange'), ('FWB', 'Frankfurt Stock Exchange')], max_length=100)),
                ('country', models.CharField(choices=[('US', 'United States'), ('CA', 'Canada'), ('UK', 'United Kingdom'), ('DE', 'Germany')], max_length=2)),
                ('currency', models.CharField(choices=[('USD', 'US Dollar'), ('CAD', 'Canadian Dollar'), ('MXN', 'Mexican Peso'), ('GBP', 'British Pound'), ('EUR', 'Euro')], max_length=100)),
                ('website', models.CharField(blank=True, max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='StockPrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.FloatField()),
                ('datetime_created', models.DateTimeField(auto_now_add=True)),
                ('stock', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.stock')),
            ],
        ),
        migrations.AddField(
            model_name='stock',
            name='exchange',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.stockexchange'),
        ),
    ]
