# Bài tập lớn CSDL Quản lý hãng vận tải hành khách đường dài

Project 5 của nhóm 5 thành viên. Ứng dụng dùng Flask và MySQL để quản lý xe, tuyến, tài xế và chuyến xe, đồng thời lập báo cáo doanh thu, lương và hạn bảo dưỡng.

[Bản yêu cầu chung của nhóm](yeu-cau-chung-project-5.md)

## Phân công

| Thành viên | Phần phụ trách | Tên nhánh gợi ý |
|---|---|---|
| TV1 | Quản lý xe và tổng hợp EER | `feature/xe-eer` |
| TV2 | Quản lý tuyến, doanh thu và file SQL | `feature/tuyen-doanh-thu` |
| TV3 | Quản lý tài xế và lương tháng | `feature/tai-xe-luong` |
| TV4 | Quản lý chuyến và ràng buộc | `feature/chuyen-xe` |
| TV5 | Bảo dưỡng và khung ứng dụng | `feature/bao-duong-khung-app` |

## Quy trình làm việc

1. Clone repo và cập nhật nhánh `develop`.
2. Tạo nhánh `feature/...` từ `develop` theo phần được giao.
3. Đẩy nhánh của mình lên GitHub và mở pull request vào `develop`.
4. Sau khi kiểm tra bản tích hợp, đưa bản nộp sang `main`.

## Thành phần cần nộp

- PDF mô tả cơ sở dữ liệu và sơ đồ EER.
- `sql/project5.sql` chứa cấu trúc bảng, dữ liệu mẫu và ba truy vấn.
- Mã nguồn Flask, giao diện và hướng dẫn chạy ứng dụng.

Repo được khởi tạo với tài liệu chung để nhóm bắt đầu triển khai.


## Hướng dẫn cài đặt và chạy chương trình

### 1. Yêu cầu

- Python
- MySQL 8
- MySQL Workbench
- Visual Studio Code

### 2. Tạo môi trường Python

Mở Terminal tại thư mục dự án:

```powershell
python -m venv .venv
```

Kích hoạt môi trường:

```powershell
.\.venv\Scripts\Activate.ps1
```

Nếu PowerShell chặn kích hoạt, chạy:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### 3. Cài thư viện

```powershell
python -m pip install -r requirements.txt
```

### 4. Cấu hình MySQL

Tạo file `.env` từ mẫu `.env.example`.

Nhập thông tin kết nối MySQL của máy:

```env
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=quan_ly_van_tai
```

Thay `DB_PASSWORD` bằng mật khẩu MySQL cá nhân.

Không đưa file `.env` chứa mật khẩu lên GitHub.


### 5. Khởi tạo cơ sở dữ liệu

1. Mở MySQL Workbench và kết nối tới MySQL 8.
2. Chọn File → Open SQL Script.
3. Mở file `sql/project5.sql` trong thư mục dự án.
4. Nhấn Execute để chạy toàn bộ file SQL.
5. Kiểm tra phần Action Output để đảm bảo không có lỗi.

File `project5.sql` bao gồm:
- Khởi tạo cơ sở dữ liệu `quan_ly_van_tai`.
- Tạo các bảng `xe`, `tuyen_xe`, `tai_xe`, `chuyen_xe`.
- Khai báo khóa chính, khóa ngoại và các ràng buộc.
- Thêm dữ liệu mẫu và thực hiện các truy vấn báo cáo.

Kiểm tra trong MySQL Workbench:

```sql
USE quan_ly_van_tai;
SHOW TABLES;
```

Kết quả cần có đủ 4 bảng trên.

Lưu ý: Với database đã tồn tại, nên sao lưu dữ liệu
trước khi chạy lại file SQL tổng hợp.


### 6. Chạy ứng dụng

```powershell
python app.py
```

Truy cập:

http://127.0.0.1:5000/

### 7. Các chức năng chính

- Quản lý xe
- Quản lý tuyến xe
- Quản lý tài xế
- Quản lý chuyến xe
- Báo cáo doanh thu
- Báo cáo lương
- Thống kê tuyến xe theo tháng
- Báo cáo hạn bảo dưỡng
- Ghi nhận bảo dưỡng xe

### 8. Kiểm tra các route Flask

```powershell
python -m flask --app app routes
```
