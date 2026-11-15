-- Chạy sau khi tạo đủ bảng, xe mẫu và một cặp tài xế mẫu.
-- Dùng cùng điều kiện nhận diện chuyến mẫu với project5.sql.
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

SELECT CASE
    WHEN @tv4_xe IS NULL THEN 'Kiểm tra biển số, số ghế và ngày đưa xe vào sử dụng.'
    WHEN @tv4_lai IS NULL OR @tv4_phu IS NULL OR @tv4_lai = @tv4_phu
        THEN 'Cần hai tài xế mẫu khác nhau. Kiểm tra lại CCCD mẫu.'
    ELSE 'Chuyến mẫu đã sẵn sàng.'
END AS ket_qua_du_lieu_mau;
