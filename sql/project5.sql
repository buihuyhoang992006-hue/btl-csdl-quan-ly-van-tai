
-- =========================================
-- TV2: TAO BANG TUYEN XE
-- =========================================

CREATE TABLE IF NOT EXISTS tuyen_xe (
    ma_tuyen INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    diem_dau VARCHAR(100) NOT NULL,
    diem_cuoi VARCHAR(100) NOT NULL,
    do_dai_km DECIMAL(8,2) NOT NULL,
    do_phuc_tap TINYINT UNSIGNED NOT NULL,

    CHECK (do_dai_km > 0),
    CHECK (do_phuc_tap IN (1, 2, 3))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- =========================================
-- TV2: DU LIEU MAU TUYEN XE
-- =========================================

INSERT INTO tuyen_xe
    (diem_dau, diem_cuoi, do_dai_km, do_phuc_tap)
VALUES
    ('Ha Noi', 'Hai Phong', 120.00, 2),
    ('Ha Noi', 'Da Nang', 760.00, 3),
    ('Ha Noi', 'Nam Dinh', 90.00, 1),
    ('Ha Noi', 'Thanh Hoa', 160.00, 2),
    ('Ha Noi', 'Lao Cai', 300.00, 3);


-- =========================================
-- TV2: TRUY VAN BAO CAO DOANH THU TUNG XE
-- =========================================

SET @ngay_bat_dau = '2026-11-01';
SET @ngay_ket_thuc = '2026-11-30';

SELECT
    x.ma_xe,
    x.bien_so,
    COUNT(c.ma_chuyen) AS so_chuyen,
    COALESCE(SUM(c.so_khach), 0) AS tong_khach,
    COALESCE(SUM(c.so_khach * c.gia_ve), 0) AS doanh_thu
FROM xe x
LEFT JOIN chuyen_xe c
    ON x.ma_xe = c.ma_xe
    AND c.trang_thai = 'HOAN_THANH'
    AND c.ngay_chay >= @ngay_bat_dau
    AND c.ngay_chay < DATE_ADD(@ngay_ket_thuc, INTERVAL 1 DAY)
GROUP BY
    x.ma_xe,
    x.bien_so
ORDER BY x.bien_so;


-- =========================================
-- TV2: TRUY VAN THONG KE TUYEN XE THEO THANG
-- =========================================

SET @thang = '2026-11-01';

SELECT
    t.ma_tuyen,
    t.diem_dau,
    t.diem_cuoi,
    t.do_dai_km,
    COUNT(c.ma_chuyen) AS so_chuyen,
    COALESCE(SUM(c.so_khach), 0) AS tong_khach
FROM tuyen_xe t
LEFT JOIN chuyen_xe c
    ON t.ma_tuyen = c.ma_tuyen
    AND c.trang_thai = 'HOAN_THANH'
    AND c.ngay_chay >= @thang
    AND c.ngay_chay < DATE_ADD(@thang, INTERVAL 1 MONTH)
GROUP BY
    t.ma_tuyen,
    t.diem_dau,
    t.diem_cuoi,
    t.do_dai_km
ORDER BY t.ma_tuyen;
