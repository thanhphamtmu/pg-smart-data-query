import csv
import os
import psycopg2
from dotenv import load_dotenv

print("Bắt đầu script!")

load_dotenv()

db_config = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT")),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASS"),
}

col_patterns = ["col_name1", "col_name1"]
search_values = ["search_value", ]
target_schema = "schema_name"
excluded_tables = [("schema_name", "excluded_table_name")]


try:
    print("Kết nối database...")
    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()
    print("Đã kết nối thành công.")

    # Lấy danh sách khóa chính
    cur.execute("""
        SELECT kcu.table_schema, kcu.table_name, kcu.column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
          ON tc.constraint_name = kcu.constraint_name
         AND tc.constraint_schema = kcu.constraint_schema
        WHERE tc.constraint_type = 'PRIMARY KEY'
    """)
    pk_map = {(row[0], row[1]): row[2] for row in cur.fetchall()}

    # Tìm tất cả cột có tên gần giống col_patterns
    col_conditions = " OR ".join(["column_name ILIKE %s" for _ in col_patterns])
    cur.execute(f"""
        SELECT table_schema, table_name, column_name
        FROM information_schema.columns
        WHERE table_schema = %s AND ({col_conditions})
        ORDER BY table_name
    """, [target_schema] + [f"%{p}%" for p in col_patterns])
    candidates = cur.fetchall()

    all_rows = []
    all_header = None

    for schema, table, matched_col in candidates:
        if (schema, table) in excluded_tables:
            print(f"  -> Bỏ qua bảng loại trừ: {schema}.{table}")
            continue

        full_table = f'"{schema}"."{table}"'
        order_by_col = pk_map.get((schema, table), matched_col)

        try:
            cur.execute(f"SELECT * FROM {full_table} WHERE 1=0")
            colnames = [desc[0] for desc in cur.description]
        except Exception as e:
            print(f"  -> Bỏ qua bảng lỗi: {full_table}: {e}")
            continue

        for val in search_values:
            print(f"\n{full_table} | cột: {matched_col} | tìm: {val}")
            try:
                cur.execute(f"""
                    SELECT * FROM {full_table}
                    WHERE {matched_col} ILIKE %s
                    ORDER BY {order_by_col} DESC
                    LIMIT 20
                """, ('%' + val + '%',))
                rows = cur.fetchall()

                if rows:
                    fname = f"{schema}_{table}_{matched_col}_{val}_result.csv".replace("/", "_")
                    with open(fname, mode="w", newline="", encoding="utf-8") as f:
                        writer = csv.writer(f)
                        writer.writerow(colnames)
                        writer.writerows(rows)
                    print(f"  -> Xuất {len(rows)} dòng -> {fname}")

                    if not all_header:
                        all_header = ["schema", "table", "column", "search_value"] + colnames
                    for row in rows:
                        all_rows.append([schema, table, matched_col, val] + list(row))
                else:
                    print("  -> Không có kết quả.")
            except Exception as qerr:
                print(f"  -> Lỗi truy vấn: {qerr}")

    cur.close()
    conn.close()
    print("\nĐóng kết nối database.")

    if all_rows:
        with open("all_results.csv", mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(all_header)
            writer.writerows(all_rows)
        print(f"\nĐã xuất file tổng hợp all_results.csv ({len(all_rows)} dòng)")
    else:
        print("Không có dữ liệu để xuất.")

except Exception as main_e:
    print(f"Lỗi chính: {main_e}")

print("Kết thúc script!")
