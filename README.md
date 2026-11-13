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

Mở MySQL Workbench.

Sau khi nhóm tích hợp xong, chạy file:

`sql/project5.sql`

File này do TV2 tổng hợp, gồm cấu trúc các bảng
và dữ liệu mẫu của nhóm.

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
- Báo cáo hạn bảo dưỡng
- Ghi nhận bảo dưỡng xe

### 8. Kiểm tra các route Flask

```powershell
python -m flask --app app routes
```
