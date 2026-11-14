-- Chạy sau khi đã thêm xe mẫu và hai tài xế giả.
-- Đổi hai CCCD sang dữ liệu giả TV3 thống nhất khi ghép project5.sql.
SET @tv4_cccd_lai = '000000000401';
SET @tv4_cccd_phu = '000000000402';
SET @tv4_diem_dau = 'Hà Nội';
SET @tv4_diem_cuoi = 'Ninh Bình';

SET @tv4_xe = (SELECT ma_xe FROM xe WHERE bien_so = '29B-123.45' AND so_ghe >= 42);
SET @tv4_lai = (SELECT ma_tai_xe FROM tai_xe WHERE cmt_cccd = @tv4_cccd_lai);
SET @tv4_phu = (SELECT ma_tai_xe FROM tai_xe WHERE cmt_cccd = @tv4_cccd_phu);

SET @tv4_tuyen_co_san = (
    SELECT MIN(ma_tuyen) FROM tuyen_xe
    WHERE diem_dau = @tv4_diem_dau AND diem_cuoi = @tv4_diem_cuoi
      AND do_dai_km = 120.00 AND do_phuc_tap = 3
);
INSERT INTO tuyen_xe (diem_dau, diem_cuoi, do_dai_km, do_phuc_tap)
SELECT @tv4_diem_dau, @tv4_diem_cuoi, 120.00, 3
WHERE @tv4_tuyen_co_san IS NULL
  AND @tv4_xe IS NOT NULL AND @tv4_lai IS NOT NULL AND @tv4_phu IS NOT NULL
  AND @tv4_lai <> @tv4_phu;

SET @tv4_tuyen = (
    SELECT MIN(ma_tuyen) FROM tuyen_xe
    WHERE diem_dau = @tv4_diem_dau AND diem_cuoi = @tv4_diem_cuoi
      AND do_dai_km = 120.00 AND do_phuc_tap = 3
);

SET @tv4_chuyen_co_san = (
    SELECT MIN(ma_chuyen) FROM chuyen_xe
    WHERE ma_xe = @tv4_xe AND ma_lai_xe = @tv4_lai AND ma_phu_xe = @tv4_phu
      AND ngay_chay = '2026-11-10' AND so_khach = 40 AND gia_ve = 120000
      AND trang_thai = 'HOAN_THANH'
      AND do_dai_km_chot = 120.00 AND do_phuc_tap_chot = 3
);

INSERT INTO chuyen_xe (
    ma_xe, ma_tuyen, ma_lai_xe, ma_phu_xe, ngay_chay,
    so_khach, gia_ve, trang_thai, do_dai_km_chot, do_phuc_tap_chot
)
SELECT
    @tv4_xe, @tv4_tuyen, @tv4_lai, @tv4_phu, '2026-11-10',
    40, 120000, 'HOAN_THANH', 120.00, 3
WHERE @tv4_xe IS NOT NULL AND @tv4_tuyen IS NOT NULL
  AND @tv4_lai IS NOT NULL AND @tv4_phu IS NOT NULL AND @tv4_lai <> @tv4_phu
  AND @tv4_chuyen_co_san IS NULL;

SELECT CASE
    WHEN @tv4_xe IS NULL THEN 'Kiểm tra biển số và số ghế của xe mẫu.'
    WHEN @tv4_lai IS NULL OR @tv4_phu IS NULL OR @tv4_lai = @tv4_phu
        THEN 'Cần hai tài xế mẫu khác nhau. Kiểm tra lại CCCD mẫu.'
    ELSE 'Chuyến mẫu đã sẵn sàng.'
END AS ket_qua_du_lieu_mau;
