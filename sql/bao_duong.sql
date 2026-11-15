USE quan_ly_van_tai;

-- Ngày cố định dùng để đối chiếu bài tập
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