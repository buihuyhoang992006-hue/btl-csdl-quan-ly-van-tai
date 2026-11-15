-- Dùng trên schema kiểm thử khi chưa có SQL của TV3.
CREATE TABLE IF NOT EXISTS tai_xe (
    ma_tai_xe INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    ho_ten VARCHAR(100) NOT NULL,
    cmt_cccd VARCHAR(20) NOT NULL UNIQUE,
    ma_bang_lai VARCHAR(30) NOT NULL UNIQUE,
    loai_bang_lai VARCHAR(20) NOT NULL,
    dia_chi VARCHAR(255) NOT NULL,
    ngay_sinh DATE NOT NULL,
    ngay_bat_dau_lai_xe DATE NOT NULL,
    CHECK (ngay_bat_dau_lai_xe > ngay_sinh)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO tai_xe (
    ho_ten, cmt_cccd, ma_bang_lai, loai_bang_lai, dia_chi,
    ngay_sinh, ngay_bat_dau_lai_xe
) VALUES
    ('Nguyễn Văn Lái', '000000000401', 'DEMO-TV4-401', 'D', 'Hà Nội', '1985-03-10', '2009-06-01'),
    ('Trần Văn Phụ', '000000000402', 'DEMO-TV4-402', 'D', 'Hà Nội', '1990-08-20', '2012-07-01')
ON DUPLICATE KEY UPDATE ma_tai_xe = tai_xe.ma_tai_xe;
