from contextlib import closing
from datetime import date

from flask import Blueprint, abort, current_app, redirect, render_template, request, url_for
from mysql.connector import Error, errorcode

from db import get_connection
from modules.bao_duong import hom_nay_vn


bp = Blueprint("chuyen_xe", __name__, url_prefix="/chuyen-xe")

NHAN_TRANG_THAI = {
    "DA_LEN_LICH": "Đã lên lịch",
    "HOAN_THANH": "Hoàn thành",
    "DA_HUY": "Đã hủy",
}
CAC_MA_LIEN_KET = ("ma_xe", "ma_tuyen", "ma_lai_xe", "ma_phu_xe")

TRUY_VAN_DANH_SACH = """
    SELECT c.*, x.bien_so, t.diem_dau, t.diem_cuoi,
           lai.ho_ten AS ten_lai_xe, phu.ho_ten AS ten_phu_xe
    FROM chuyen_xe c
    JOIN xe x ON x.ma_xe = c.ma_xe
    JOIN tuyen_xe t ON t.ma_tuyen = c.ma_tuyen
    JOIN tai_xe lai ON lai.ma_tai_xe = c.ma_lai_xe
    JOIN tai_xe phu ON phu.ma_tai_xe = c.ma_phu_xe
"""


def doc_ngay(gia_tri):
    try:
        ngay = date.fromisoformat(gia_tri)
    except ValueError:
        return None
    return ngay if ngay.isoformat() == gia_tri else None


@bp.get("")
def danh_sach():
    hom_nay = hom_nay_vn()
    loc_lich = request.args.get("lich") == "1"
    ngay_nhap = request.args.get("ngay", "")
    ngay = doc_ngay(ngay_nhap) if ngay_nhap else None

    cac_dieu_kien = []
    tham_so = []
    if loc_lich:
        cac_dieu_kien.append("c.trang_thai = 'DA_LEN_LICH' AND c.ngay_chay >= %s")
        tham_so.append(hom_nay)
    if ngay is not None:
        cac_dieu_kien.append("c.ngay_chay = %s")
        tham_so.append(ngay)

    danh_sach_chuyen = []
    loi = ""
    ma_http = 200

    if ngay_nhap and ngay is None:
        loi, ma_http = "Ngày lọc không hợp lệ.", 400
    elif loc_lich and ngay is not None and ngay < hom_nay:
        loi, ma_http = "Chọn ngày từ hôm nay để xem lịch sắp chạy.", 400
    else:
        cau_lenh = TRUY_VAN_DANH_SACH
        if cac_dieu_kien:
            cau_lenh += " WHERE " + " AND ".join(cac_dieu_kien)
        if loc_lich:
            cau_lenh += " ORDER BY c.ngay_chay ASC, c.ma_chuyen ASC"
        else:
            cau_lenh += " ORDER BY c.ngay_chay DESC, c.ma_chuyen DESC"
        try:
            with closing(get_connection()) as conn:
                with closing(conn.cursor(dictionary=True)) as cursor:
                    cursor.execute(cau_lenh, tuple(tham_so))
                    danh_sach_chuyen = cursor.fetchall()
        except Error:
            current_app.logger.exception("Không tải được danh sách chuyến xe")
            loi, ma_http = "Không tải được chuyến xe. Kiểm tra kết nối và các bảng MySQL.", 503

    return render_template(
        "chuyenxe/index.html",
        danh_sach=danh_sach_chuyen,
        nhan_trang_thai=NHAN_TRANG_THAI,
        loc_lich=loc_lich,
        hom_nay=hom_nay.isoformat(),
        ngay_nhap=ngay_nhap,
        loi=loi,
    ), ma_http


def kiem_tra_form(form, hanh_dong, hom_nay):
    du_lieu, loi = {}, {}

    gioi_han = [
        ("so_khach", 0, 65535, "Số khách"),
        ("gia_ve", 0, 999_999_999_999, "Giá vé"),
    ]
    if hanh_dong != "hoan_thanh":
        gioi_han += [
            ("ma_xe", 1, 4_294_967_295, "Xe"),
            ("ma_tuyen", 1, 4_294_967_295, "Tuyến xe"),
            ("ma_lai_xe", 1, 4_294_967_295, "Lái xe"),
            ("ma_phu_xe", 1, 4_294_967_295, "Phụ xe"),
        ]

    for ten, nho_nhat, lon_nhat, nhan in gioi_han:
        raw = form.get(ten, "").strip()
        if len(raw) <= 12 and raw.isascii() and raw.isdecimal():
            gia_tri = int(raw)
            if nho_nhat <= gia_tri <= lon_nhat:
                du_lieu[ten] = gia_tri
                continue
        if ten in CAC_MA_LIEN_KET:
            loi[ten] = f"Vui lòng chọn {nhan.lower()}."
        else:
            loi[ten] = f"{nhan} phải là số nguyên từ {nho_nhat:,} đến {lon_nhat:,}.".replace(",", ".")

    if "ma_lai_xe" in du_lieu and du_lieu["ma_lai_xe"] == du_lieu.get("ma_phu_xe"):
        loi["ma_phu_xe"] = "Phụ xe phải khác lái xe."

    ngay = doc_ngay(form.get("ngay_chay", ""))
    if ngay is None or ngay.year < 1000:
        loi["ngay_chay"] = "Nhập ngày chạy hợp lệ."
    elif hanh_dong == "hoan_thanh" and ngay > hom_nay:
        loi["ngay_chay"] = "Ngày chạy thực tế không được sau hôm nay."
    else:
        du_lieu["ngay_chay"] = ngay

    return du_lieu, loi


def doc_chuyen(cursor, ma_chuyen, *, khoa=False):
    cau_lenh = "SELECT * FROM chuyen_xe WHERE ma_chuyen = %s"
    if khoa:
        cau_lenh += " FOR UPDATE"
    cursor.execute(cau_lenh, (ma_chuyen,))
    chuyen = cursor.fetchone()
    if chuyen is None:
        abort(404, description="Không tìm thấy chuyến xe.")
    if chuyen["trang_thai"] != "DA_LEN_LICH":
        abort(409, description="Chuyến đã hoàn thành hoặc đã hủy và chỉ dùng để tra cứu.")
    return chuyen


def doc_danh_muc(cursor):
    cursor.execute("SELECT ma_xe, bien_so, so_ghe FROM xe ORDER BY bien_so")
    danh_sach_xe = cursor.fetchall()

    cursor.execute("SELECT ma_tuyen, diem_dau, diem_cuoi FROM tuyen_xe ORDER BY diem_dau, diem_cuoi")
    danh_sach_tuyen = cursor.fetchall()

    cursor.execute("SELECT ma_tai_xe, ho_ten FROM tai_xe ORDER BY ho_ten, ma_tai_xe")
    return {"xe": danh_sach_xe, "tuyen": danh_sach_tuyen, "tai_xe": cursor.fetchall()}


def luu_chuyen(cursor, du_lieu, hanh_dong, ma_chuyen, form, chuyen):
    if hanh_dong == "hoan_thanh":
        du_lieu.update({ten: chuyen[ten] for ten in CAC_MA_LIEN_KET})

    # Khóa cùng dòng xe với thao tác sửa thông tin xe.
    cursor.execute(
        "SELECT so_ghe, ngay_dua_vao_su_dung FROM xe WHERE ma_xe = %s FOR UPDATE",
        (du_lieu["ma_xe"],),
    )
    xe = cursor.fetchone()

    if ma_chuyen is not None:
        chuyen_moi = doc_chuyen(cursor, ma_chuyen, khoa=True)
        if hanh_dong == "hoan_thanh" and any(
            str(chuyen_moi[ten]) != form.get(ten) or chuyen_moi[ten] != du_lieu[ten]
            for ten in CAC_MA_LIEN_KET
        ):
            return {"chung": "Phân công đã thay đổi. Mở lại trang xác nhận để kiểm tra."}, 409

    cursor.execute(
        "SELECT do_dai_km, do_phuc_tap FROM tuyen_xe WHERE ma_tuyen = %s FOR SHARE",
        (du_lieu["ma_tuyen"],),
    )
    tuyen = cursor.fetchone()

    cursor.execute(
        "SELECT ma_tai_xe FROM tai_xe WHERE ma_tai_xe IN (%s, %s) FOR SHARE",
        (du_lieu["ma_lai_xe"], du_lieu["ma_phu_xe"]),
    )
    ma_tai_xe = {dong["ma_tai_xe"] for dong in cursor.fetchall()}

    loi = {}
    if xe is None:
        loi["ma_xe"] = "Xe đã chọn không còn trong danh mục."
    else:
        if du_lieu["so_khach"] > xe["so_ghe"] - 2:
            loi["so_khach"] = f"Xe này chở tối đa {xe['so_ghe'] - 2} khách."
        ngay_su_dung = xe["ngay_dua_vao_su_dung"]
        if du_lieu["ngay_chay"] < ngay_su_dung:
            loi["ngay_chay"] = f"Ngày chạy phải từ ngày xe đưa vào sử dụng ({ngay_su_dung:%d/%m/%Y}) trở đi."

    if tuyen is None:
        loi["ma_tuyen"] = "Tuyến đã chọn không còn trong danh mục."

    for ten in ("ma_lai_xe", "ma_phu_xe"):
        if du_lieu[ten] not in ma_tai_xe:
            loi[ten] = "Tài xế đã chọn không còn trong danh mục."

    if loi:
        return loi, 400

    if hanh_dong == "them":
        cursor.execute("""
            INSERT INTO chuyen_xe (
                ma_xe, ma_tuyen, ma_lai_xe, ma_phu_xe, ngay_chay, so_khach, gia_ve
            ) VALUES (
                %(ma_xe)s, %(ma_tuyen)s, %(ma_lai_xe)s, %(ma_phu_xe)s,
                %(ngay_chay)s, %(so_khach)s, %(gia_ve)s
            )
        """, du_lieu)
    elif hanh_dong == "sua":
        cursor.execute("""
            UPDATE chuyen_xe
            SET ma_xe = %(ma_xe)s, ma_tuyen = %(ma_tuyen)s, ma_lai_xe = %(ma_lai_xe)s,
                ma_phu_xe = %(ma_phu_xe)s, ngay_chay = %(ngay_chay)s,
                so_khach = %(so_khach)s, gia_ve = %(gia_ve)s
            WHERE ma_chuyen = %(ma_chuyen)s AND trang_thai = 'DA_LEN_LICH'
        """, {**du_lieu, "ma_chuyen": ma_chuyen})
    else:
        cursor.execute("""
            UPDATE chuyen_xe
            SET ngay_chay = %(ngay_chay)s, so_khach = %(so_khach)s, gia_ve = %(gia_ve)s,
                do_dai_km_chot = %(do_dai_km)s, do_phuc_tap_chot = %(do_phuc_tap)s,
                trang_thai = 'HOAN_THANH'
            WHERE ma_chuyen = %(ma_chuyen)s AND trang_thai = 'DA_LEN_LICH'
        """, {**du_lieu, **tuyen, "ma_chuyen": ma_chuyen})

    return {}, 200


def xu_ly_form(hanh_dong, ma_chuyen=None):
    hom_nay = hom_nay_vn()
    dang_luu = request.method == "POST"
    form = request.form.to_dict() if dang_luu else {"ngay_chay": hom_nay.isoformat()}
    loi, danh_muc, chuyen = {}, {}, None
    ma_http = 200
    if dang_luu:
        du_lieu, loi = kiem_tra_form(form, hanh_dong, hom_nay)
        if loi:
            ma_http = 400

    try:
        with closing(get_connection()) as conn:
            if dang_luu and not loi:
                conn.start_transaction()

            with closing(conn.cursor(dictionary=True, buffered=True)) as cursor:
                if ma_chuyen is not None:
                    chuyen = doc_chuyen(cursor, ma_chuyen)
                    if not dang_luu:
                        form = chuyen
                danh_muc = doc_danh_muc(cursor)

                if dang_luu and not loi:
                    loi, ma_http = luu_chuyen(cursor, du_lieu, hanh_dong, ma_chuyen, form, chuyen)
                    if not loi:
                        conn.commit()
                        return redirect(url_for("chuyen_xe.danh_sach"), code=303)
                    conn.rollback()
    except Error as exc:
        if exc.errno in (errorcode.ER_LOCK_DEADLOCK, errorcode.ER_LOCK_WAIT_TIMEOUT):
            loi["chung"] = "Dữ liệu đang được cập nhật. Vui lòng lưu lại."
            ma_http = 409
        else:
            current_app.logger.exception("Không xử lý được biểu mẫu chuyến xe")
            loi["chung"] = "Không lưu hoặc tải được dữ liệu. Kiểm tra kết nối và các bảng MySQL."
            ma_http = 503

    return render_template(
        "chuyenxe/form.html", form=form, loi=loi, danh_muc=danh_muc,
        hom_nay=hom_nay.isoformat(), hanh_dong=hanh_dong, chuyen=chuyen,
    ), ma_http


@bp.route("/them", methods=["GET", "POST"])
def them():
    return xu_ly_form("them")


@bp.route("/<int:ma_chuyen>/sua", methods=["GET", "POST"])
def sua(ma_chuyen):
    return xu_ly_form("sua", ma_chuyen)


@bp.route("/<int:ma_chuyen>/hoan-thanh", methods=["GET", "POST"])
def hoan_thanh(ma_chuyen):
    return xu_ly_form("hoan_thanh", ma_chuyen)


@bp.post("/<int:ma_chuyen>/huy")
def huy(ma_chuyen):
    try:
        with closing(get_connection()) as conn:
            with closing(conn.cursor(dictionary=True)) as cursor:
                cursor.execute("""
                    UPDATE chuyen_xe SET trang_thai = 'DA_HUY'
                    WHERE ma_chuyen = %s AND trang_thai = 'DA_LEN_LICH'
                """, (ma_chuyen,))
                if cursor.rowcount == 0:
                    doc_chuyen(cursor, ma_chuyen)
                    abort(409, description="Chuyến đã thay đổi. Tải lại danh sách trước khi thao tác.")
            conn.commit()
    except Error:
        current_app.logger.exception("Không hủy được chuyến xe")
        abort(503, description="Chưa hủy được chuyến xe. Vui lòng thử lại.")

    return redirect(url_for("chuyen_xe.danh_sach"), code=303)
