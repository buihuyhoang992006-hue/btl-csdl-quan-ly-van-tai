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
