# Yêu cầu chung Project 5

**Quản lý hãng vận tải hành khách đường dài**

**Bản 1.0 · Áp dụng cho 5 thành viên**

Bản này quy định tên bảng, cách tính và phần bàn giao để cả nhóm làm trên cùng một dự án. Sản phẩm là web app nội bộ cho nhân viên hãng xe. Nhân viên nhập danh mục xe, tuyến và tài xế, lập chuyến, xác nhận chuyến đã chạy rồi xem lương, doanh thu và hạn bảo dưỡng.

Đề bài yêu cầu **mô hình EER và PDF (40%)**, **CSDL MySQL, dữ liệu mẫu và truy vấn trong file SQL (30%)**, **ứng dụng có giao diện và link GitHub (30%)**. Phần ứng dụng có 10% cho các truy vấn bắt buộc và tối đa 20% cho tính năng phụ. Flask, cách đặt tên, hệ số và quy trình bên dưới là các quyết định triển khai của nhóm.

## 1. Phân công và phần bàn giao

| Thành viên | Phụ trách | Bàn giao để ghép vào dự án |
|---|---|---|
| **TV1** | Xe và báo cáo thiết kế CSDL | Bảng `xe`, màn hình xe, dữ liệu mẫu. Chủ trì vẽ EER và tổng hợp PDF từ phần mô tả của cả nhóm. Điều phối lượt ghép cuối và kiểm tra bản nộp. |
| **TV2** | Tuyến xe, doanh thu và file SQL | Bảng `tuyen_xe`, màn hình tuyến, truy vấn và màn hình doanh thu từng xe. Tổng hợp lệnh tạo bảng, dữ liệu mẫu và cả ba truy vấn vào `sql/project5.sql`. |
| **TV3** | Tài xế và lương tháng | Bảng `tai_xe`, màn hình tài xế, dữ liệu mẫu, truy vấn và màn hình lương tháng. |
| **TV4** | Chuyến xe và kiểm tra ràng buộc | Bảng `chuyen_xe`, màn hình lập và cập nhật chuyến, kiểm tra giới hạn khách và hai vai trò. Bàn giao một chuyến mẫu ngay sau khi chốt cấu trúc bảng để TV2, TV3 và TV5 làm báo cáo song song. |
| **TV5** | Bảo dưỡng và khung giao diện | Truy vấn, màn hình bảo dưỡng và thao tác cập nhật mốc bảo dưỡng. Dựng trang chủ, menu, khung Flask và kết nối MySQL. Viết hướng dẫn cài và chạy trong `README.md`. |

Mỗi thành viên tự kiểm tra phần mình, gửi mô tả các bảng hoặc quy tắc mình phụ trách cho TV1 và gửi SQL cho TV2. TV1 ghép mô hình và báo cáo từ các phần đã được kiểm tra.

## 2. Công nghệ và giao diện

- **Công nghệ chung** dùng Python, Flask, Jinja, HTML/CSS và MySQL 8. Kết nối bằng `mysql-connector-python`. App chạy cục bộ trên trình duyệt và kết nối cùng cấu trúc CSDL `quan_ly_van_tai`. Dùng InnoDB và `utf8mb4`.
- **Cấu hình** dùng chung hàm `db.get_connection()` với các biến `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`. TV5 cung cấp `.env.example`, `requirements.txt` và hướng dẫn thiết lập. Mỗi máy dùng cấu hình riêng, giữ mật khẩu thật ngoài Git.
- **Giao diện** dùng tiếng Việt và cùng một `templates/base.html`. Hiển thị ngày theo `dd/mm/yyyy`, tiền theo VND. Khi lưu thất bại, báo lỗi cạnh nội dung liên quan và giữ lại dữ liệu đã nhập để người dùng sửa.
- **Dữ liệu** dùng `DATE` cho ngày, số thập phân cho km và số nguyên đồng cho tiền. Lấy mốc ngày hiện tại theo giờ Việt Nam. Khoảng ngày bao gồm cả ngày bắt đầu và ngày kết thúc.

| Màn hình | Đường dẫn thống nhất | Thành viên |
|---|---|---|
| Trang chủ | `/` | TV5 |
| Quản lý xe | `/xe` | TV1 |
| Quản lý tuyến | `/tuyen-xe` | TV2 |
| Quản lý tài xế | `/tai-xe` | TV3 |
| Quản lý chuyến | `/chuyen-xe` | TV4 |
| Doanh thu theo xe | `/bao-cao/doanh-thu` | TV2 |
| Lương tài xế | `/bao-cao/luong` | TV3 |
| Hạn bảo dưỡng | `/bao-cao/bao-duong` | TV5 |

Màn hình danh mục có bảng và thao tác thêm, sửa, xóa mục chưa được tham chiếu. Màn hình chuyến dùng danh sách chọn xe, tuyến và tài xế, hiển thị giới hạn khách ngay khi chọn xe. Màn hình báo cáo có bộ lọc phù hợp và hiển thị kết quả dạng bảng.

TV5 quản lý `app.py`, `db.py` và giao diện dùng chung. Mỗi màn hình nghiệp vụ dùng một Flask Blueprint trong `modules/` và thư mục giao diện tương ứng trong `templates/`. Dùng tên `xe`, `tuyen_xe`, `tai_xe`, `chuyen_xe`, `doanh_thu`, `luong` và `bao_duong`. TV5 đăng ký các Blueprint trong `app.py` theo bảng đường dẫn trên.

## 3. Cấu trúc CSDL dùng chung

Quy ước tên bảng, cột viết thường, không dấu, có dấu gạch dưới. Các cột có `NOT NULL` trừ hai cột chốt thông tin tuyến. **PK** là khóa chính, **FK** là khóa ngoại. Bốn khóa chính dùng `INT UNSIGNED AUTO_INCREMENT`, các FK cùng kiểu `INT UNSIGNED`.

### Bảng xe

| Cột | Kiểu hoặc ràng buộc | Ý nghĩa |
|---|---|---|
| `ma_xe` | PK | Mã nội bộ của xe |
| `bien_so` | `VARCHAR(20) UNIQUE` | Biển số. Bỏ khoảng trắng thừa và chuyển chữ hoa trước khi lưu |
| `mau_xe`, `hang_san_xuat`, `model` | `VARCHAR(80)` | Màu, hãng và model xe |
| `doi_xe` | `SMALLINT UNSIGNED` | Năm sản xuất |
| `ngay_dua_vao_su_dung` | `DATE` | Mốc tính số năm sử dụng |
| `so_ghe` | `SMALLINT UNSIGNED`, tối thiểu 3 | Tổng số ghế, gồm hai ghế cho lái xe và phụ xe |
| `ngay_bao_duong_cuoi` | `DATE` | Mốc bắt đầu chu kỳ bảo dưỡng hiện tại |

Số năm sử dụng là số năm tròn từ `ngay_dua_vao_su_dung` đến ngày xem. Ngày đưa vào sử dụng và ngày bảo dưỡng cuối không được sau hôm nay, ngày bảo dưỡng cuối không được trước ngày đưa vào sử dụng.

### Bảng tai_xe

| Cột | Kiểu hoặc ràng buộc | Ý nghĩa |
|---|---|---|
| `ma_tai_xe` | PK | Mã nội bộ của tài xế |
| `ho_ten` | `VARCHAR(100)` | Họ tên |
| `cmt_cccd` | `VARCHAR(20) UNIQUE` | Số giấy tờ lưu dạng chuỗi để giữ số 0 đầu |
| `ma_bang_lai` | `VARCHAR(30) UNIQUE` | Mã số bằng lái |
| `loai_bang_lai` | `VARCHAR(20)` | Loại bằng lái |
| `dia_chi` | `VARCHAR(255)` | Địa chỉ |
| `ngay_sinh` | `DATE` | Ngày sinh |
| `ngay_bat_dau_lai_xe` | `DATE` | Mốc tính thâm niên |

Thâm niên là số năm tròn từ `ngay_bat_dau_lai_xe` đến ngày xem. Mốc bắt đầu phải sau ngày sinh và không sau hôm nay.

### Bảng tuyen_xe

| Cột | Kiểu hoặc ràng buộc | Ý nghĩa |
|---|---|---|
| `ma_tuyen` | PK | Mã nội bộ của tuyến |
| `diem_dau`, `diem_cuoi` | `VARCHAR(100)` | Điểm đi và điểm đến |
| `do_dai_km` | `DECIMAL(8,2)`, lớn hơn 0 | Quãng đường của một chuyến theo tuyến |
| `do_phuc_tap` | `TINYINT UNSIGNED`, nhận 1, 2 hoặc 3 | Mức độ khó |

### Bảng chuyen_xe

| Cột | Kiểu hoặc ràng buộc | Ý nghĩa |
|---|---|---|
| `ma_chuyen` | PK | Mã chuyến |
| `ma_xe` | FK → `xe.ma_xe` | Xe thực hiện chuyến |
| `ma_tuyen` | FK → `tuyen_xe.ma_tuyen` | Tuyến của chuyến |
| `ma_lai_xe`, `ma_phu_xe` | Hai FK → `tai_xe.ma_tai_xe` | Hai tài xế khác nhau, mỗi người giữ một vai trò |
| `ngay_chay` | `DATE` | Ngày dự kiến khi lập chuyến, ngày thực tế khi xác nhận hoàn thành |
| `so_khach` | `SMALLINT UNSIGNED` | Số khách trên chuyến |
| `gia_ve` | `DECIMAL(12,0)`, lớn hơn hoặc bằng 0 | Giá một vé, đơn vị đồng |
| `trang_thai` | `ENUM('DA_LEN_LICH','HOAN_THANH','DA_HUY')` | Mặc định `DA_LEN_LICH` |
| `do_dai_km_chot` | `DECIMAL(8,2)`, cho phép NULL | Km của tuyến tại lúc xác nhận hoàn thành |
| `do_phuc_tap_chot` | `TINYINT UNSIGNED`, cho phép NULL | Độ khó của tuyến tại lúc xác nhận hoàn thành |

**Quan hệ cần có trên EER.** Xe và tuyến đều có thể gắn với 0 hoặc nhiều chuyến. Mỗi chuyến có đúng một xe, một tuyến, một lái xe và một phụ xe. Tài xế có thể tham gia 0 hoặc nhiều chuyến ở từng vai trò. Vẽ hai quan hệ riêng giữa tài xế và chuyến, đồng thời ghi ràng buộc hai vai trò do hai người khác nhau đảm nhiệm. Ghi số năm sử dụng và thâm niên là thuộc tính dẫn xuất.

## 4. Quy tắc khi nhập và cập nhật

1. **Giới hạn số khách.** Khi lưu hoặc xác nhận chuyến, kiểm tra `0 ≤ so_khach ≤ so_ghe - 2` theo xe được chọn. Nếu sửa số ghế của xe, kiểm tra số khách của các chuyến đã lên lịch đang dùng xe đó. Ví dụ xe 45 ghế chở tối đa 43 khách.
2. **Phân công tài xế.** Hai vai trò đều bắt buộc và phải khác nhau. Một người có thể lái chuyến này và làm phụ xe ở chuyến khác.
3. **Vòng đời chuyến.** Chuyến đã lên lịch có thể sửa thông tin, chuyển sang hoàn thành hoặc hủy. Khi hoàn thành, xác nhận lại ngày chạy, số khách và giá vé. Ngày chạy không được sau hôm nay. Lưu hai cột chốt của tuyến cùng lần cập nhật trạng thái. Chuyến đã hoàn thành hoặc đã hủy dùng để tra cứu.
4. **Giữ dữ liệu liên kết.** MySQL giữ PK, FK, tính duy nhất và các kiểm tra như độ khó hợp lệ, giá vé không âm. Hai cột chốt phải có giá trị hợp lệ khi chuyến hoàn thành, còn lại để NULL. App kiểm tra các điều kiện phụ thuộc bảng khác hoặc ngày hiện tại trước khi ghi. Nếu một xe, tuyến hoặc tài xế đã được chuyến tham chiếu, báo rõ lý do khi người dùng yêu cầu xóa.
5. **Ghi nhận bảo dưỡng.** Chọn xe và nhập ngày bảo dưỡng trong khoảng từ ngày bảo dưỡng cuối đã lưu đến hôm nay. Lưu vào `xe.ngay_bao_duong_cuoi` để bắt đầu chu kỳ mới.

## 5. Cách tính ba báo cáo

Chỉ dùng chuyến `HOAN_THANH` đã chạy tính đến ngày xem. Hai cột chốt giữ nguyên km và độ khó của chuyến khi người dùng sửa thông tin tuyến sau này. App chạy cùng logic SQL với file nộp và truyền bộ lọc bằng tham số.

| Độ khó | Hệ số lương | Hệ số km | Lương phụ xe mỗi chuyến | Lương lái xe mỗi chuyến |
|---:|---:|---:|---:|---:|
| 1 | 1,00 | 1,00 | 100.000 đ | 200.000 đ |
| 2 | 1,25 | 1,25 | 125.000 đ | 250.000 đ |
| 3 | 1,50 | 1,50 | 150.000 đ | 300.000 đ |

### Lương tài xế

Mặc định hiển thị tháng hiện tại tính đến hôm nay, cho chọn các tháng đã qua. Tính từng chuyến theo `do_phuc_tap_chot`. Lương phụ xe bằng 100.000 đồng nhân hệ số lương. Lương lái xe gấp đôi mức phụ xe. Cộng tiền theo mã tài xế qua cả hai vai trò. Hiển thị tên, số chuyến lái, số chuyến phụ và tổng lương. Tài xế không có chuyến trong kỳ có lương 0 đồng.

### Doanh thu từng xe

Người dùng nhập từ ngày và đến ngày, với ngày bắt đầu không sau ngày kết thúc. Doanh thu của chuyến bằng `so_khach × gia_ve`. Cộng theo mã xe trong khoảng ngày. Hiển thị biển số, số chuyến, tổng khách và tổng doanh thu. Xe không chạy chuyến nào trong kỳ có doanh thu 0 đồng.

### Hạn bảo dưỡng

1. Lấy các chuyến của xe chạy **sau ngày bảo dưỡng cuối** đến hết ngày xem. Nhóm quy ước bảo dưỡng được ghi nhận vào cuối ngày vì hệ thống lưu kiểu `DATE`.
2. Km quy đổi của chuyến bằng `do_dai_km_chot × hệ số km`. Cộng toàn bộ km quy đổi rồi mới lấy phần nguyên của `tổng km quy đổi / 100` để ra số ngày giảm.
3. Số ngày của chu kỳ bằng `max(0, 360 − số ngày giảm)`. Cộng số ngày này vào ngày bảo dưỡng cuối để ra ngày đến hạn.
4. Hiển thị biển số, ngày bảo dưỡng cuối, tổng km quy đổi và ngày đến hạn. Xe có ngày đến hạn **trước ngày xem** vào danh sách quá hạn riêng. Xe có ngày đến hạn bằng ngày xem hiển thị **Đến hạn hôm nay**.

## 6. Tính năng phụ dự kiến để demo

Đề chấm 2% cho mỗi tính năng phụ được công nhận, tối đa 20%. Nhóm dùng danh sách dưới đây để chia việc và đối chiếu khi chuẩn bị demo.

| Thành viên | Tính năng 1 | Tính năng 2 |
|---|---|---|
| TV1 | Quản lý hồ sơ xe | Xem lịch sử chuyến của một xe |
| TV2 | Quản lý danh mục tuyến | Thống kê số chuyến và tổng khách theo tuyến trong tháng |
| TV3 | Quản lý hồ sơ tài xế | Xem lịch sử phân công của tài xế theo vai trò |
| TV4 | Lập chuyến và cập nhật trạng thái | Xem lịch chuyến sắp chạy theo ngày |
| TV5 | Ghi nhận lần bảo dưỡng | Xem tổng quan số xe, chuyến trong ngày và xe quá hạn trên trang chủ |

## 7. Dữ liệu kiểm tra chung

**Mốc đối chiếu cố định là ngày 11/11/2026.** Dùng xe `29B-123.45` có 45 ghế, bảo dưỡng cuối ngày 01/10/2026. Cho xe chạy một chuyến đã hoàn thành ngày 10/11/2026 với 40 khách, giá vé 120.000 đồng, tuyến dài 120 km ở mức 3. Hai vai trò do hai tài xế khác nhau đảm nhiệm. Trong ca này xe và hai tài xế không có chuyến hoàn thành nào khác.

| Thử trên app hoặc SQL | Kết quả cần đạt |
|---|---|
| Nhập 43 rồi 44 khách với xe 45 ghế | 43 hợp lệ, 44 bị từ chối và có thông báo |
| Chọn cùng người làm lái xe và phụ xe | Bị từ chối trước khi ghi chuyến |
| Xem doanh thu từ 10/11 đến 10/11 | Xe có 1 chuyến, 40 khách và 4.800.000 đồng |
| Xem lương tháng 11/2026 | Lái xe 300.000 đồng, phụ xe 150.000 đồng |
| Xem bảo dưỡng tại mốc đối chiếu | 180 km quy đổi, giảm 1 ngày, đến hạn 25/09/2027 |
| Thêm xe khác bảo dưỡng cuối 01/10/2025, chưa có chuyến sau đó | Đến hạn 26/09/2026 và nằm trong danh sách quá hạn |
| Thêm chuyến đã lên lịch hoặc đã hủy | Các số liệu của ba báo cáo không đổi |
| Đổi độ dài hoặc độ khó của tuyến sau khi chuyến đã hoàn thành | Lương và km quy đổi của chuyến cũ không đổi |
| Ghi nhận bảo dưỡng cho xe mẫu vào 11/11/2026 | Km của chu kỳ mới bằng 0, ngày đến hạn mới là 06/11/2027 |

Dữ liệu mẫu dùng thông tin giả. Kiểm tra các ca thêm hoặc sửa dữ liệu trên bản sao để giữ nguyên số liệu đối chiếu. Khi demo khác ngày, chọn kỳ báo cáo chứa dữ liệu đã nhập hoặc điều chỉnh ngày mẫu sao cho chuyến đã hoàn thành nằm trong kỳ cần minh họa.

## 8. Trình tự làm và nộp bài

1. **Chuẩn bị nền chung.** TV1 cùng nhóm đối chiếu EER với bốn bảng. TV2 đưa file SQL tạo bảng và một bộ dữ liệu nhỏ lên nhánh `develop`. TV5 đưa khung Flask, kết nối MySQL và menu chung lên cùng nhánh.
2. **Làm song song.** Mỗi thành viên tách nhánh `feature/...` từ `develop`. Khi cần đổi cột hoặc công thức, cập nhật bản yêu cầu, báo người dùng dữ liệu đó và sửa SQL chung trước khi ghép.
3. **Ghép và chạy thử.** Mở pull request vào `develop`. Dùng cùng một CSDL mẫu để thử màn hình của từng người và các ca ở mục 7. Kiểm tra báo cáo trên app khớp với SQL. Chuyển bản đã kiểm tra sang `main` để nộp.

| Sản phẩm nộp | Nội dung cần đủ | Người tổng hợp |
|---|---|---|
| `bao-cao-project-5.pdf` | Bối cảnh, bốn thực thể, thuộc tính, khóa, sơ đồ EER, bội số quan hệ, mức tham gia, ràng buộc và công thức nhóm chọn | TV1 |
| `sql/project5.sql` | Tạo CSDL và bảng, ràng buộc, dữ liệu mẫu, ba truy vấn có ghi rõ tham số và chạy được trên MySQL | TV2 |
| Link GitHub | Mã nguồn app có giao diện, ba báo cáo, các tính năng phụ đã làm, SQL và README hướng dẫn cài đặt, cấu hình và chạy | TV1 điều phối, TV5 tổng hợp hướng dẫn |

Một phần được coi là bàn giao xong khi chạy được từ giao diện, dùng đúng dữ liệu và công thức chung, có kết quả đối chiếu và đã được ghép vào `develop`.
