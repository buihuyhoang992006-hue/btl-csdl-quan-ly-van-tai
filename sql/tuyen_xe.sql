
CREATE TABLE IF NOT EXISTS tuyen_xe (
    ma_tuyen INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    diem_dau VARCHAR(100) NOT NULL,
    diem_cuoi VARCHAR(100) NOT NULL,
    do_dai_km DECIMAL(8,2) NOT NULL,
    do_phuc_tap TINYINT UNSIGNED NOT NULL,

    CONSTRAINT chk_tuyen_do_dai
        CHECK (do_dai_km > 0),

    CONSTRAINT chk_tuyen_do_phuc_tap
        CHECK (do_phuc_tap IN (1, 2, 3))
) ENGINE = InnoDB
  DEFAULT CHARACTER SET = utf8mb4;
  
INSERT INTO tuyen_xe (diem_dau, diem_cuoi, do_dai_km, do_phuc_tap)
VALUES
('Ha Noi', 'Hai Phong', 120.00, 2),
('Ha Noi', 'Da Nang', 760.00, 3),
('Ha Noi', 'Nam Dinh', 90.00, 1),
('Ha Noi', 'Thanh Hoa', 160.00, 2),
('Ha Noi', 'Lao Cai', 300.00, 3);

SELECT * FROM tuyen_xe;