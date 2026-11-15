-- Project 5 - TV3
-- Bảng tai_xe, dữ liệu mẫu và câu truy vấn tính lương tháng.

USE quan_ly_van_tai;

CREATE TABLE IF NOT EXISTS tai_xe (
    ma_tai_xe INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    ho_ten VARCHAR(100) NOT NULL,
    cmt_cccd VARCHAR(20) NOT NULL UNIQUE,
    ma_bang_lai VARCHAR(30) NOT NULL UNIQUE,
    loai_bang_lai VARCHAR(20) NOT NULL,
    dia_chi VARCHAR(255) NOT NULL,
    ngay_sinh DATE NOT NULL,
    ngay_bat_dau_lai_xe DATE NOT NULL,
    CONSTRAINT chk_tai_xe_ngay_bat_dau
        CHECK (ngay_bat_dau_lai_xe > ngay_sinh)
) ENGINE = InnoDB DEFAULT CHARACTER SET = utf8mb4;

-- Dữ liệu mẫu phục vụ kiểm tra chung (tối thiểu 2 tài xế khác nhau cho lái xe và phụ xe)
INSERT INTO tai_xe (
    ho_ten, cmt_cccd, ma_bang_lai, loai_bang_lai,
    dia_chi, ngay_sinh, ngay_bat_dau_lai_xe
) VALUES
    ('Nguyễn Văn An', '000000000401', 'B2-01020304', 'D', 'Cầu Giấy, Hà Nội', '1985-05-12', '2010-08-01'),
    ('Trần Minh Bình', '000000000402', 'B2-05060708', 'E', 'Thanh Xuân, Hà Nội', '1992-11-20', '2016-03-15'),
    ('Lê Hoàng Cường', '036095009999', 'B2-09101112', 'D', 'Đống Đa, Hà Nội', '1995-02-10', '2019-06-01')
ON DUPLICATE KEY UPDATE ma_tai_xe = tai_xe.ma_tai_xe;

-- =========================================
-- TV3: TRUY VẤN BÁO CÁO LƯƠNG TÀI XẾ THEO THÁNG
-- Tham số: @thang (ngày đầu tháng, VD: '2026-11-01'), @ngay_gioi_han (ngày cuối kỳ hoặc hôm nay, VD: '2026-11-11')
-- =========================================
SET @thang = '2026-11-01';
SET @ngay_gioi_han = '2026-11-11';

SELECT
    tx.ma_tai_xe,
    tx.ho_ten,
    COALESCE(lx.so_chuyen_lai, 0) AS so_chuyen_lai,
    COALESCE(px.so_chuyen_phu, 0) AS so_chuyen_phu,
    COALESCE(lx.luong_lai, 0) + COALESCE(px.luong_phu, 0) AS tong_luong
FROM tai_xe tx
LEFT JOIN (
    SELECT
        ma_lai_xe,
        COUNT(*) AS so_chuyen_lai,
        SUM(
            200000 * CASE do_phuc_tap_chot
                WHEN 1 THEN 1.00
                WHEN 2 THEN 1.25
                WHEN 3 THEN 1.50
                ELSE 0
            END
        ) AS luong_lai
    FROM chuyen_xe
    WHERE trang_thai = 'HOAN_THANH'
      AND ngay_chay >= @thang
      AND ngay_chay < DATE_ADD(@thang, INTERVAL 1 MONTH)
      AND ngay_chay <= @ngay_gioi_han
    GROUP BY ma_lai_xe
) lx ON tx.ma_tai_xe = lx.ma_lai_xe
LEFT JOIN (
    SELECT
        ma_phu_xe,
        COUNT(*) AS so_chuyen_phu,
        SUM(
            100000 * CASE do_phuc_tap_chot
                WHEN 1 THEN 1.00
                WHEN 2 THEN 1.25
                WHEN 3 THEN 1.50
                ELSE 0
            END
        ) AS luong_phu
    FROM chuyen_xe
    WHERE trang_thai = 'HOAN_THANH'
      AND ngay_chay >= @thang
      AND ngay_chay < DATE_ADD(@thang, INTERVAL 1 MONTH)
      AND ngay_chay <= @ngay_gioi_han
    GROUP BY ma_phu_xe
) px ON tx.ma_tai_xe = px.ma_phu_xe
ORDER BY tx.ho_ten, tx.ma_tai_xe;