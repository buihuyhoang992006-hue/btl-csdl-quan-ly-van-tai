
-- =====================================================
-- PROJECT 5 - QUAN LY VAN TAI
-- FILE SQL TONG HOP CUA 5 THANH VIEN
-- =====================================================

CREATE DATABASE IF NOT EXISTS quan_ly_van_tai
    DEFAULT CHARACTER SET utf8mb4;

USE quan_ly_van_tai;


-- =====================================================
-- TV1: TAO BANG XE
-- =====================================================

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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- =====================================================
-- TV2: TAO BANG TUYEN XE
-- =====================================================

CREATE TABLE IF NOT EXISTS tuyen_xe (
    ma_tuyen INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    diem_dau VARCHAR(100) NOT NULL,
    diem_cuoi VARCHAR(100) NOT NULL,
    do_dai_km DECIMAL(8,2) NOT NULL,
    do_phuc_tap TINYINT UNSIGNED NOT NULL,

    CHECK (do_dai_km > 0),
    CHECK (do_phuc_tap IN (1, 2, 3))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- =====================================================
-- TV3: TAO BANG TAI XE
-- =====================================================

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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- =====================================================
-- TV4: TAO BANG CHUYEN XE
-- =====================================================

CREATE TABLE IF NOT EXISTS chuyen_xe (
    ma_chuyen INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    ma_xe INT UNSIGNED NOT NULL,
    ma_tuyen INT UNSIGNED NOT NULL,
    ma_lai_xe INT UNSIGNED NOT NULL,
    ma_phu_xe INT UNSIGNED NOT NULL,
    ngay_chay DATE NOT NULL,
    so_khach SMALLINT UNSIGNED NOT NULL,
    gia_ve DECIMAL(12,0) NOT NULL,
    trang_thai ENUM('DA_LEN_LICH', 'HOAN_THANH', 'DA_HUY')
        NOT NULL DEFAULT 'DA_LEN_LICH',
    do_dai_km_chot DECIMAL(8,2) NULL,
    do_phuc_tap_chot TINYINT UNSIGNED NULL,

    CONSTRAINT fk_chuyen_xe
        FOREIGN KEY (ma_xe) REFERENCES xe(ma_xe),

    CONSTRAINT fk_chuyen_tuyen
        FOREIGN KEY (ma_tuyen) REFERENCES tuyen_xe(ma_tuyen),

    CONSTRAINT fk_chuyen_lai
        FOREIGN KEY (ma_lai_xe) REFERENCES tai_xe(ma_tai_xe),

    CONSTRAINT fk_chuyen_phu
        FOREIGN KEY (ma_phu_xe) REFERENCES tai_xe(ma_tai_xe),

    CONSTRAINT chk_chuyen_vai_tro
        CHECK (ma_lai_xe <> ma_phu_xe),

    CONSTRAINT chk_chuyen_gia_ve
        CHECK (gia_ve >= 0),

    CONSTRAINT chk_chuyen_trang_thai
        CHECK (trang_thai IN ('DA_LEN_LICH', 'HOAN_THANH', 'DA_HUY')),

    CONSTRAINT chk_chuyen_thong_tin_chot CHECK (
        (
            trang_thai = 'HOAN_THANH'
            AND do_dai_km_chot IS NOT NULL
            AND do_phuc_tap_chot IS NOT NULL
            AND do_dai_km_chot > 0
            AND do_phuc_tap_chot IN (1, 2, 3)
        ) OR (
            trang_thai IN ('DA_LEN_LICH', 'DA_HUY')
            AND do_dai_km_chot IS NULL
            AND do_phuc_tap_chot IS NULL
        )
    ),

    INDEX idx_chuyen_xe_trang_thai (ma_xe, trang_thai, so_khach),
    INDEX idx_chuyen_lich (trang_thai, ngay_chay)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- =====================================================
-- TV1: DU LIEU MAU XE
-- =====================================================

INSERT INTO xe (
    bien_so, mau_xe, hang_san_xuat, model, doi_xe,
    ngay_dua_vao_su_dung, so_ghe, ngay_bao_duong_cuoi
) VALUES (
    '29B-123.45', 'Trắng', 'Thaco', 'Bluesky', 2019,
    '2020-01-15', 45, '2026-10-01'
)
ON DUPLICATE KEY UPDATE ma_xe = xe.ma_xe;


-- =====================================================
-- TV2: DU LIEU MAU TUYEN XE
-- =====================================================

INSERT INTO tuyen_xe
    (diem_dau, diem_cuoi, do_dai_km, do_phuc_tap)
SELECT 'Ha Noi', 'Hai Phong', 120.00, 2
WHERE NOT EXISTS (
    SELECT 1 FROM tuyen_xe
    WHERE diem_dau = 'Ha Noi' AND diem_cuoi = 'Hai Phong'
      AND do_dai_km = 120.00 AND do_phuc_tap = 2
);

INSERT INTO tuyen_xe
    (diem_dau, diem_cuoi, do_dai_km, do_phuc_tap)
SELECT 'Ha Noi', 'Da Nang', 760.00, 3
WHERE NOT EXISTS (
    SELECT 1 FROM tuyen_xe
    WHERE diem_dau = 'Ha Noi' AND diem_cuoi = 'Da Nang'
      AND do_dai_km = 760.00 AND do_phuc_tap = 3
);

INSERT INTO tuyen_xe
    (diem_dau, diem_cuoi, do_dai_km, do_phuc_tap)
SELECT 'Ha Noi', 'Nam Dinh', 90.00, 1
WHERE NOT EXISTS (
    SELECT 1 FROM tuyen_xe
    WHERE diem_dau = 'Ha Noi' AND diem_cuoi = 'Nam Dinh'
      AND do_dai_km = 90.00 AND do_phuc_tap = 1
);

INSERT INTO tuyen_xe
    (diem_dau, diem_cuoi, do_dai_km, do_phuc_tap)
SELECT 'Ha Noi', 'Thanh Hoa', 160.00, 2
WHERE NOT EXISTS (
    SELECT 1 FROM tuyen_xe
    WHERE diem_dau = 'Ha Noi' AND diem_cuoi = 'Thanh Hoa'
      AND do_dai_km = 160.00 AND do_phuc_tap = 2
);

INSERT INTO tuyen_xe
    (diem_dau, diem_cuoi, do_dai_km, do_phuc_tap)
SELECT 'Ha Noi', 'Lao Cai', 300.00, 3
WHERE NOT EXISTS (
    SELECT 1 FROM tuyen_xe
    WHERE diem_dau = 'Ha Noi' AND diem_cuoi = 'Lao Cai'
      AND do_dai_km = 300.00 AND do_phuc_tap = 3
);


-- =====================================================
-- TV3: DU LIEU MAU TAI XE
-- =====================================================

INSERT INTO tai_xe (
    ho_ten, cmt_cccd, ma_bang_lai, loai_bang_lai,
    dia_chi, ngay_sinh, ngay_bat_dau_lai_xe
) VALUES
    ('Nguyễn Văn An', '001085001234', 'B2-01020304', 'D',
     'Cầu Giấy, Hà Nội', '1985-05-12', '2010-08-01'),

    ('Trần Minh Bình', '001092005678', 'B2-05060708', 'E',
     'Thanh Xuân, Hà Nội', '1992-11-20', '2016-03-15'),

    ('Lê Hoàng Cường', '036095009999', 'B2-09101112', 'D',
     'Đống Đa, Hà Nội', '1995-02-10', '2019-06-01')

ON DUPLICATE KEY UPDATE ma_tai_xe = tai_xe.ma_tai_xe;


-- =====================================================
-- TV4: DU LIEU MAU TUYEN VA CHUYEN XE
-- =====================================================

SET @tv4_diem_dau = 'Hà Nội';
SET @tv4_diem_cuoi = 'Ninh Bình';
SET @tv4_ngay_chay = '2026-11-10';

SET @tv4_xe = (
    SELECT ma_xe FROM xe
    WHERE bien_so = '29B-123.45'
      AND so_ghe >= 42
      AND ngay_dua_vao_su_dung <= @tv4_ngay_chay
);

-- Hai bộ demo dùng hai cặp tài xế khác nhau cho cùng một chuyến mẫu.
SET @tv4_lai_moi = (SELECT ma_tai_xe FROM tai_xe WHERE cmt_cccd = '001085001234');
SET @tv4_phu_moi = (SELECT ma_tai_xe FROM tai_xe WHERE cmt_cccd = '001092005678');
SET @tv4_lai_cu = (SELECT ma_tai_xe FROM tai_xe WHERE cmt_cccd = '000000000401');
SET @tv4_phu_cu = (SELECT ma_tai_xe FROM tai_xe WHERE cmt_cccd = '000000000402');

SET @tv4_co_cap_moi = (@tv4_lai_moi IS NOT NULL AND @tv4_phu_moi IS NOT NULL);
SET @tv4_lai = IF(@tv4_co_cap_moi, @tv4_lai_moi, @tv4_lai_cu);
SET @tv4_phu = IF(@tv4_co_cap_moi, @tv4_phu_moi, @tv4_phu_cu);

INSERT INTO tuyen_xe (diem_dau, diem_cuoi, do_dai_km, do_phuc_tap)
SELECT @tv4_diem_dau, @tv4_diem_cuoi, 120.00, 3
WHERE @tv4_xe IS NOT NULL
  AND @tv4_lai IS NOT NULL
  AND @tv4_phu IS NOT NULL
  AND @tv4_lai <> @tv4_phu
  AND NOT EXISTS (
      SELECT 1 FROM tuyen_xe
      WHERE diem_dau = @tv4_diem_dau
        AND diem_cuoi = @tv4_diem_cuoi
        AND do_dai_km = 120.00
        AND do_phuc_tap = 3
  );

SET @tv4_tuyen = (
    SELECT MIN(ma_tuyen) FROM tuyen_xe
    WHERE diem_dau = @tv4_diem_dau
      AND diem_cuoi = @tv4_diem_cuoi
      AND do_dai_km = 120.00
      AND do_phuc_tap = 3
);

-- Giữ chuyến mẫu đã có với một trong hai cặp tài xế của bộ demo.
INSERT INTO chuyen_xe (
    ma_xe, ma_tuyen, ma_lai_xe, ma_phu_xe, ngay_chay,
    so_khach, gia_ve, trang_thai, do_dai_km_chot, do_phuc_tap_chot
)
SELECT
    @tv4_xe, @tv4_tuyen, @tv4_lai, @tv4_phu, @tv4_ngay_chay,
    40, 120000, 'HOAN_THANH', 120.00, 3
WHERE @tv4_xe IS NOT NULL
  AND @tv4_tuyen IS NOT NULL
  AND @tv4_lai IS NOT NULL
  AND @tv4_phu IS NOT NULL
  AND @tv4_lai <> @tv4_phu
  AND NOT EXISTS (
      SELECT 1
      FROM chuyen_xe c
      JOIN tuyen_xe t ON t.ma_tuyen = c.ma_tuyen
      WHERE c.ma_xe = @tv4_xe
        AND t.diem_dau = @tv4_diem_dau
        AND t.diem_cuoi = @tv4_diem_cuoi
        AND c.ngay_chay = @tv4_ngay_chay
        AND c.so_khach = 40
        AND c.gia_ve = 120000
        AND c.trang_thai = 'HOAN_THANH'
        AND c.do_dai_km_chot = 120.00
        AND c.do_phuc_tap_chot = 3
        AND (
            (c.ma_lai_xe = @tv4_lai_moi AND c.ma_phu_xe = @tv4_phu_moi)
            OR (c.ma_lai_xe = @tv4_lai_cu AND c.ma_phu_xe = @tv4_phu_cu)
        )
  );


-- =====================================================
-- TV2: BAO CAO DOANH THU TUNG XE
-- =====================================================

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
GROUP BY x.ma_xe, x.bien_so
ORDER BY x.bien_so;


-- =====================================================
-- TV2: THONG KE TUYEN XE THEO THANG
-- =====================================================

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
    t.ma_tuyen, t.diem_dau, t.diem_cuoi, t.do_dai_km
ORDER BY t.ma_tuyen;


-- =====================================================
-- TV3: BAO CAO LUONG TAI XE THEO THANG
-- =====================================================

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


-- =====================================================
-- TV5: BAO CAO HAN BAO DUONG XE
-- =====================================================

SET @ngay_xem = '2026-11-11';

SELECT
    k.ma_xe,
    k.bien_so,
    k.ngay_bao_duong_cuoi,
    k.tong_km_quy_doi,

    GREATEST(
        0, 360 - FLOOR(k.tong_km_quy_doi / 100)
    ) AS chu_ky_ngay,

    DATE_ADD(
        k.ngay_bao_duong_cuoi,
        INTERVAL GREATEST(
            0, 360 - FLOOR(k.tong_km_quy_doi / 100)
        ) DAY
    ) AS ngay_den_han

FROM (
    SELECT
        x.ma_xe,
        x.bien_so,
        x.ngay_bao_duong_cuoi,

        COALESCE(SUM(
            c.do_dai_km_chot *
            CASE c.do_phuc_tap_chot
                WHEN 1 THEN 1.00
                WHEN 2 THEN 1.25
                WHEN 3 THEN 1.50
                ELSE 0
            END
        ), 0) AS tong_km_quy_doi

    FROM xe x
    LEFT JOIN chuyen_xe c
        ON c.ma_xe = x.ma_xe
       AND c.trang_thai = 'HOAN_THANH'
       AND c.ngay_chay > x.ngay_bao_duong_cuoi
       AND c.ngay_chay <= @ngay_xem
    GROUP BY
        x.ma_xe,
        x.bien_so,
        x.ngay_bao_duong_cuoi
) AS k

ORDER BY ngay_den_han, k.bien_so;
