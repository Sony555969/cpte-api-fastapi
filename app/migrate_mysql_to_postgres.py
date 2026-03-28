from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, DateTime, Boolean, SmallInteger
from sqlalchemy.dialects.mysql import ENUM as MySQLEnum


MYSQL_URL = "mysql+pymysql://root:@localhost:3306/base_drnoflu"

POSTGRES_URL = "postgresql://root:eFcupGoH3YTP2hB1O7BpukmfJf2U4gIe@dpg-d733hdggjchc73aufrhg-a.oregon-postgres.render.com/base_drnoflu?sslmode=require"

# 🔹 Créer les moteurs SQLAlchemy
source_engine = create_engine(MYSQL_URL)
target_engine = create_engine(POSTGRES_URL)

# 🔹 Charger les tables MySQL
source_meta = MetaData()
source_meta.reflect(bind=source_engine)

# 🔹 Nouveau MetaData pour PostgreSQL
target_meta = MetaData()

# 🔹 Copier les tables en adaptant les types MySQL → PostgreSQL
for table_name, table in source_meta.tables.items():
    columns = []
    for column in table.columns:
        col_type_name = column.type.__class__.__name__
        # ENUM/SET → String
        if col_type_name in ["ENUM", "SET"]:
            columns.append(Column(column.name, String(255), primary_key=column.primary_key))

        # DATETIME → DateTime
        elif col_type_name == "DATETIME":
            columns.append(Column(column.name, DateTime, primary_key=column.primary_key))

        # TINYINT → Boolean
        elif col_type_name == "TINYINT":
            columns.append(Column(column.name, Boolean, primary_key=column.primary_key))

        # Les autres types restent inchangés
        else:
            columns.append(Column(column.name, column.type, primary_key=column.primary_key))

    Table(table_name, target_meta, *columns)
    # 🔹 Créer toutes les tables sur PostgreSQL Render
target_meta.create_all(bind=target_engine)

print("✅ Toutes les tables créées sur PostgreSQL Render (sans données)")