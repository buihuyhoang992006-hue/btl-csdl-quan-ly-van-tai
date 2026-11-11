-- Project 5 - TV1
-- Bảng xe, dữ liệu mẫu và truy vấn kiểm tra.

CREATE DATABASE IF NOT EXISTS quan_ly_van_tai
    DEFAULT CHARACTER SET utf8mb4;
USE quan_ly_van_tai;

CREATE TABLE IF NOT EXISTS xe (
    ma_xe INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    bien_so VARCHAR(20) NOT NULL UNIQUE,
    mau_xe VARCHAR(80) NOT NULL,
    hang_san_xuat VARCHAR(80) NOT NULL,
    model VARCHAR(80) NOT NULL,
    doi_xe SMALLINT UNSIGNED NOT NULL,
    ngay_dua_vao_su_dung DATE NOT NULL,
    so_ghe SMALLINT UNSIGNED NOT NULL,
    ngay_bao_duong_cuoi DATE NOT NULL,
    CONSTRAINT chk_xe_so_ghe CHECK (so_ghe >= 3),
    CONSTRAINT chk_xe_ngay_bao_duong
        CHECK (ngay_bao_duong_cuoi >= ngay_dua_vao_su_dung)
) ENGINE = InnoDB DEFAULT CHARACTER SET = utf8mb4;

-- Dùng biển số để chỉ tạo một dòng mẫu khi chạy lại file.
INSERT INTO xe (
    bien_so, mau_xe, hang_san_xuat, model, doi_xe,
    ngay_dua_vao_su_dung, so_ghe, ngay_bao_duong_cuoi
) VALUES (
    '29B-123.45', 'Trắng', 'Thaco', 'Bluesky', 2019,
    '2020-01-15', 45, '2026-10-01'
)
ON DUPLICATE KEY UPDATE ma_xe = xe.ma_xe;

-- Đối chiếu sức chứa và số năm sử dụng của xe mẫu.
SELECT
    ma_xe,
    bien_so,
    so_ghe,
    so_ghe - 2 AS so_khach_toi_da,
    TIMESTAMPDIFF(YEAR, ngay_dua_vao_su_dung, CURRENT_DATE) AS so_nam_su_dung
FROM xe
WHERE bien_so = '29B-123.45';