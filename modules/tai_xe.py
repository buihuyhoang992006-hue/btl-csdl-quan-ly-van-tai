from contextlib import closing
from datetime import date, datetime, timedelta, timezone

from flask import Blueprint, abort, current_app, redirect, render_template, request, url_for
from mysql.connector import Error, errorcode

from db import get_connection


bp = Blueprint("tai_xe", __name__, url_prefix="/tai-xe")
MUI_GIO_VIET_NAM = timezone(timedelta(hours=7))


def hom_nay_vn():
    return datetime.now(MUI_GIO_VIET_NAM).date()


@bp.get("")
def danh_sach():
    ngay_xem = hom_nay_vn()

    try:
        with closing(get_connection()) as connection:
            with closing(connection.cursor(dictionary=True)) as cursor:
                cursor.execute(
                    """
                    SELECT ma_tai_xe, ho_ten, cmt_cccd, ma_bang_lai, loai_bang_lai,
                           dia_chi, ngay_sinh, ngay_bat_dau_lai_xe,
                           TIMESTAMPDIFF(YEAR, ngay_bat_dau_lai_xe, %s) AS tham_nien
                    FROM tai_xe
                    ORDER BY ho_ten, ma_tai_xe
                    """,
                    (ngay_xem,),
                )
                danh_sach_tai_xe = cursor.fetchall()
    except Error:
        current_app.logger.exception("Không tải được danh sách tài xế từ MySQL")
        return render_template(
            "tai_xe/index.html",
            loi="Không tải được danh sách tài xế. Hãy kiểm tra kết nối MySQL và bảng tai_xe.",
        ), 503

    return render_template("tai_xe/index.html", danh_sach_tai_xe=danh_sach_tai_xe)


def kiem_tra_tai_xe(form, hom_nay):
    tai_xe = {}
    loi = {}

    for cot, so_ky_tu in (
        ("ho_ten", 100),
        ("cmt_cccd", 20),
        ("ma_bang_lai", 30),
        ("loai_bang_lai", 20),
        ("dia_chi", 255),
    ):
        gia_tri = form.get(cot, "").strip()
        if cot in ("cmt_cccd", "ma_bang_lai", "loai_bang_lai"):
            gia_tri = "".join(gia_tri.split()).upper()

        if not gia_tri:
            loi[cot] = "Hãy nhập thông tin này."
        elif len(gia_tri) > so_ky_tu:
            loi[cot] = f"Nhập tối đa {so_ky_tu} ký tự."
        elif cot == "cmt_cccd" and (not gia_tri.isascii() or not gia_tri.isdigit() or len(gia_tri) not in (9, 12)):
            loi[cot] = "Số CMT/CCCD chỉ được gồm 9 hoặc 12 chữ số."
        else:
            tai_xe[cot] = gia_tri

    for cot in ("ngay_sinh", "ngay_bat_dau_lai_xe"):
        try:
            gia_tri = date.fromisoformat(form.get(cot, ""))
        except ValueError:
            loi[cot] = "Hãy nhập ngày hợp lệ."
            continue

        if gia_tri > hom_nay:
            loi[cot] = "Hãy chọn ngày từ hôm nay trở về trước."
        else:
            tai_xe[cot] = gia_tri

    ngay_sinh = tai_xe.get("ngay_sinh")
    ngay_bat_dau = tai_xe.get("ngay_bat_dau_lai_xe")
    if ngay_sinh and ngay_bat_dau and ngay_bat_dau <= ngay_sinh:
        loi["ngay_bat_dau_lai_xe"] = "Ngày bắt đầu lái xe phải sau ngày sinh."

    return tai_xe, loi


def loi_khi_luu_tai_xe(exc):
    if exc.errno == errorcode.ER_DUP_ENTRY:
        thong_diep = str(exc)
        if "cmt_cccd" in thong_diep:
            return {"cmt_cccd": "Số CMT/CCCD này đã tồn tại trong hệ thống."}, 409
        if "ma_bang_lai" in thong_diep:
            return {"ma_bang_lai": "Mã bằng lái này đã tồn tại trong hệ thống."}, 409
        return {"chung": "Thông tin định danh (CMT/CCCD hoặc mã bằng lái) bị trùng."}, 409

    current_app.logger.exception("Không lưu được tài xế vào MySQL")
    return {"chung": "Chưa lưu được thông tin tài xế. Hãy thử lại."}, 503


def hien_thi_form(form, loi, hom_nay, *, ma_tai_xe=None, trang_thai=200):
    return render_template(
        "tai_xe/form.html",
        form=form,
        loi=loi,
        hom_nay=hom_nay,
        ma_tai_xe=ma_tai_xe,
    ), trang_thai


@bp.route("/them", methods=["GET", "POST"])
def them():
    hom_nay = hom_nay_vn()
    if request.method != "POST":
        return hien_thi_form({}, {}, hom_nay)

    form = request.form
    tai_xe, loi = kiem_tra_tai_xe(form, hom_nay)
    trang_thai = 400

    if not loi:
        try:
            with closing(get_connection()) as connection:
                with closing(connection.cursor()) as cursor:
                    cursor.execute(
                        """
                        INSERT INTO tai_xe (
                            ho_ten, cmt_cccd, ma_bang_lai, loai_bang_lai,
                            dia_chi, ngay_sinh, ngay_bat_dau_lai_xe
                        ) VALUES (
                            %(ho_ten)s, %(cmt_cccd)s, %(ma_bang_lai)s, %(loai_bang_lai)s,
                            %(dia_chi)s, %(ngay_sinh)s, %(ngay_bat_dau_lai_xe)s
                        )
                        """,
                        tai_xe,
                    )
                connection.commit()
        except Error as exc:
            loi, trang_thai = loi_khi_luu_tai_xe(exc)
        else:
            return redirect(url_for("tai_xe.danh_sach"), code=303)

    return hien_thi_form(form, loi, hom_nay, trang_thai=trang_thai)


def doc_tai_xe(cursor, ma_tai_xe, *, khoa=False):
    cau_lenh = """
        SELECT ma_tai_xe, ho_ten, cmt_cccd, ma_bang_lai, loai_bang_lai,
               dia_chi, ngay_sinh, ngay_bat_dau_lai_xe
        FROM tai_xe
        WHERE ma_tai_xe = %s
    """
    if khoa:
        cau_lenh += " FOR UPDATE"
    cursor.execute(cau_lenh, (ma_tai_xe,))
    tai_xe = cursor.fetchone()
    if tai_xe is None:
        abort(404, description="Không tìm thấy tài xế.")
    return tai_xe


@bp.get("/<int:ma_tai_xe>/sua")
def sua(ma_tai_xe):
    hom_nay = hom_nay_vn()
    try:
        with closing(get_connection()) as connection:
            with closing(connection.cursor(dictionary=True, buffered=True)) as cursor:
                form = doc_tai_xe(cursor, ma_tai_xe)
    except Error:
        current_app.logger.exception("Không tải được thông tin tài xế từ MySQL")
        return render_template("tai_xe/index.html", loi="Không tải được thông tin tài xế."), 503

    return hien_thi_form(form, {}, hom_nay, ma_tai_xe=ma_tai_xe)


@bp.post("/<int:ma_tai_xe>/sua")
def luu_sua(ma_tai_xe):
    hom_nay = hom_nay_vn()
    form = request.form
    tai_xe, loi = kiem_tra_tai_xe(form, hom_nay)
    trang_thai = 400

    if not loi:
        try:
            with closing(get_connection()) as connection:
                with closing(connection.cursor()) as cursor:
                    tai_xe["ma_tai_xe"] = ma_tai_xe
                    cursor.execute(
                        """
                        UPDATE tai_xe
                        SET ho_ten = %(ho_ten)s,
                            cmt_cccd = %(cmt_cccd)s,
                            ma_bang_lai = %(ma_bang_lai)s,
                            loai_bang_lai = %(loai_bang_lai)s,
                            dia_chi = %(dia_chi)s,
                            ngay_sinh = %(ngay_sinh)s,
                            ngay_bat_dau_lai_xe = %(ngay_bat_dau_lai_xe)s
                        WHERE ma_tai_xe = %(ma_tai_xe)s
                        """,
                        tai_xe,
                    )
                    if cursor.rowcount == 0:
                        cursor.execute("SELECT ma_tai_xe FROM tai_xe WHERE ma_tai_xe = %s", (ma_tai_xe,))
                        if cursor.fetchone() is None:
                            abort(404, description="Không tìm thấy tài xế.")
                connection.commit()
        except Error as exc:
            loi, trang_thai = loi_khi_luu_tai_xe(exc)
        else:
            return redirect(url_for("tai_xe.danh_sach"), code=303)

    return hien_thi_form(form, loi, hom_nay, ma_tai_xe=ma_tai_xe, trang_thai=trang_thai)


def tim_chuyen_tham_chieu(cursor, ma_tai_xe, *, khoa=False):
    cau_lenh = """
        SELECT ma_chuyen
        FROM chuyen_xe
        WHERE ma_lai_xe = %s OR ma_phu_xe = %s
        ORDER BY ma_chuyen
        LIMIT 1
    """
    if khoa:
        cau_lenh += " FOR UPDATE"

    try:
        cursor.execute(cau_lenh, (ma_tai_xe, ma_tai_xe))
    except Error as exc:
        if exc.errno == errorcode.ER_NO_SUCH_TABLE:
            return None
        raise

    return cursor.fetchone()


@bp.route("/<int:ma_tai_xe>/xoa", methods=["GET", "POST"])
def xoa(ma_tai_xe):
    xac_nhan = request.method == "POST"

    try:
        with closing(get_connection()) as connection:
            if xac_nhan:
                connection.start_transaction()

            with closing(connection.cursor(dictionary=True, buffered=True)) as cursor:
                tai_xe = doc_tai_xe(cursor, ma_tai_xe, khoa=xac_nhan)
                chuyen = tim_chuyen_tham_chieu(cursor, ma_tai_xe, khoa=xac_nhan)
                if not xac_nhan or chuyen:
                    if xac_nhan:
                        connection.rollback()
                    trang_thai = 409 if xac_nhan else 200
                    return render_template(
                        "tai_xe/xoa.html", tai_xe=tai_xe, ma_tai_xe=ma_tai_xe, chuyen=chuyen
                    ), trang_thai

                cursor.execute("DELETE FROM tai_xe WHERE ma_tai_xe = %s", (ma_tai_xe,))

            connection.commit()
    except Error as exc:
        if exc.errno in (errorcode.ER_ROW_IS_REFERENCED, errorcode.ER_ROW_IS_REFERENCED_2):
            loi = "Tài xế đang được phân công trong chuyến xe nên không thể xóa."
            trang_thai = 409
        else:
            current_app.logger.exception("Không thực hiện được yêu cầu xóa tài xế từ MySQL")
            loi = "Chưa thể thực hiện yêu cầu xóa tài xế. Hãy thử lại."
            trang_thai = 503
        return render_template("tai_xe/xoa.html", loi=loi), trang_thai

    return redirect(url_for("tai_xe.danh_sach"), code=303)


@bp.get("/<int:ma_tai_xe>/lich-su")
def lich_su(ma_tai_xe):
    tai_xe = None
    try:
        with closing(get_connection()) as connection:
            with closing(connection.cursor(dictionary=True, buffered=True)) as cursor:
                tai_xe = doc_tai_xe(cursor, ma_tai_xe)
                cursor.execute(
                    """
                    SELECT c.ma_chuyen, c.ngay_chay, c.trang_thai,
                           CASE
                               WHEN c.ma_lai_xe = %s THEN 'Lái xe'
                               ELSE 'Phụ xe'
                           END AS vai_tro,
                           x.bien_so,
                           t.diem_dau, t.diem_cuoi
                    FROM chuyen_xe AS c
                    JOIN xe AS x ON x.ma_xe = c.ma_xe
                    JOIN tuyen_xe AS t ON t.ma_tuyen = c.ma_tuyen
                    WHERE c.ma_lai_xe = %s OR c.ma_phu_xe = %s
                    ORDER BY c.ngay_chay DESC, c.ma_chuyen DESC
                    """,
                    (ma_tai_xe, ma_tai_xe, ma_tai_xe),
                )
                danh_sach_chuyen = cursor.fetchall()
    except Error as exc:
        if exc.errno == errorcode.ER_NO_SUCH_TABLE and tai_xe is not None:
            loi = "Cần tạo bảng chuyen_xe theo SQL chung để xem lịch sử phân công."
        else:
            current_app.logger.exception("Không tải được lịch sử phân công tài xế từ MySQL")
            loi = "Không tải được lịch sử phân công. Hãy kiểm tra kết nối MySQL và cấu trúc bảng."
        return render_template("tai_xe/lich_su.html", tai_xe=tai_xe, loi=loi), 503

    return render_template("tai_xe/lich_su.html", tai_xe=tai_xe, danh_sach_chuyen=danh_sach_chuyen)