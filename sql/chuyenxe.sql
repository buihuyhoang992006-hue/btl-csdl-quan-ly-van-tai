-- Chọn schema của dự án trước khi chạy. Tạo xe, tuyen_xe và tai_xe trước.
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

    CONSTRAINT fk_chuyen_xe FOREIGN KEY (ma_xe) REFERENCES xe(ma_xe),
    CONSTRAINT fk_chuyen_tuyen FOREIGN KEY (ma_tuyen) REFERENCES tuyen_xe(ma_tuyen),
    CONSTRAINT fk_chuyen_lai FOREIGN KEY (ma_lai_xe) REFERENCES tai_xe(ma_tai_xe),
    CONSTRAINT fk_chuyen_phu FOREIGN KEY (ma_phu_xe) REFERENCES tai_xe(ma_tai_xe),

    CONSTRAINT chk_chuyen_vai_tro CHECK (ma_lai_xe <> ma_phu_xe),
    CONSTRAINT chk_chuyen_gia_ve CHECK (gia_ve >= 0),
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
