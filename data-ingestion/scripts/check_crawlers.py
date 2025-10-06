#!/usr/bin/env python3
"""Script para verificar estado de crawlers y tablas"""

import boto3
import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

glue = boto3.client('glue', region_name='us-east-1')

# Verificar crawlers
crawlers = ['passengers-crawler', 'trips-crawler', 'tickets-crawler']
print("Estado de los crawlers:")
print("=" * 50)
for crawler_name in crawlers:
    try:
        response = glue.get_crawler(Name=crawler_name)
        state = response['Crawler']['State']
        last_crawl = response['Crawler'].get('LastCrawl', {})
        status = last_crawl.get('Status', 'N/A')
        print(f"✅ {crawler_name}: {state} (Last status: {status})")
    except Exception as e:
        print(f"❌ {crawler_name}: Error - {e}")

# Listar tablas
print("\n" + "=" * 50)
print("Tablas en el catálogo:")
print("=" * 50)
try:
    response = glue.get_tables(DatabaseName='bus_mvp_db')
    if response['TableList']:
        for table in response['TableList']:
            name = table['Name']
            location = table.get('StorageDescriptor', {}).get('Location', 'N/A')
            print(f"📊 {name}")
            print(f"   Location: {location}")
    else:
        print("⚠️  No hay tablas en el catálogo aún")
except Exception as e:
    print(f"❌ Error: {e}")
