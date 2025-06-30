# 🔍 PostgreSQL Multi-Table Search Script

Script Python giúp **tự động tìm kiếm dữ liệu trong nhiều bảng PostgreSQL** theo:
- ✅ Nhiều cột gợi ý (`contract_number`, `pay_id`, v.v.)
- ✅ Nhiều giá trị tìm kiếm (`20250101010101001`, `PAY123`, v.v.)
- ✅ Tự động xác định cột khóa chính (`PRIMARY KEY`) để sắp xếp `ORDER BY DESC`
- ✅ Ghi kết quả từng bảng ra file `.csv` riêng và một file tổng hợp `all_results.csv`

---

## 🚀 Cách sử dụng

### 1. Cài đặt thư viện cần thiết

```bash
pip install psycopg2 python-dotenv
```

### 2. Tạo file `.env` chứa thông tin kết nối PostgreSQL

~~~env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ten_database
DB_USER=ten_nguoi_dung
DB_PASS=mat_khau
