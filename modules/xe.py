from contextlib import closing
from datetime import date, datetime, timedelta, timezone

from flask import Blueprint, abort, current_app, redirect, render_template, request, url_for
from mysql.connector import Error, errorcode

from db import get_connection


bp = Blueprint("xe", __name__, url_prefix="/xe")
MUI_GIO_VIET_NAM = timezone(timedelta(hours=7))


@bp.get("")
def danh_sach():
    ngay_xem = datetime.now(MUI_GIO_VIET_NAM).date()

    try:
        with closing(get_connection()) as connection:
            with closing(connection.cursor(dictionary=True)) as cursor:
                cursor.execute(
                    """
                    SELECT ma_xe, bien_so, mau_xe, hang_san_xuat, model, doi_xe,
                           ngay_dua_vao_su_dung, so_ghe, ngay_bao_duong_cuoi,
                           so_ghe - 2 AS so_khach_toi_da,
                           TIMESTAMPDIFF(YEAR, ngay_dua_vao_su_dung, %s)
                               AS so_nam_su_dung
                    FROM xe
                    ORDER BY bien_so
                    """,
                    (ngay_xem,),
                )
                danh_sach_xe = cursor.fetchall()
    except Error:
        current_app.logger.exception("Không tải được danh sách xe từ MySQL")
        return render_template(
            "xe/index.html",
            loi="Không tải được danh sách xe. Hãy kiểm tra kết nối MySQL và bảng xe.",
        ), 503

    return render_template("xe/index.html", danh_sach_xe=danh_sach_xe)


def kiem_tra_xe(form, hom_nay, *, ngay_bao_duong_da_luu=None):
    xe = {}
    loi = {}

    for cot, so_ky_tu in (
        ("bien_so", 20),
        ("mau_xe", 80),
        ("hang_san_xuat", 80),
        ("model", 80),
    ):
        gia_tri = form.get(cot, "").strip()
        if cot == "bien_so":
            gia_tri = "".join(gia_tri.split()).upper()
        if not gia_tri:
            loi[cot] = "Hãy nhập thông tin này."
        elif len(gia_tri) > so_ky_tu:
            loi[cot] = f"Nhập tối đa {so_ky_tu} ký tự."
        else:
            xe[cot] = gia_tri

    for cot, toi_thieu in (("doi_xe", 1), ("so_ghe", 3)):
        try:
            gia_tri = int(form.get(cot, ""))
        except ValueError:
            loi[cot] = "Hãy nhập một số nguyên."
            continue
        if toi_thieu <= gia_tri <= 65535:
            xe[cot] = gia_tri
        else:
            loi[cot] = f"Nhập số từ {toi_thieu} đến 65535."

    cot_ngay = ["ngay_dua_vao_su_dung"]
    if ngay_bao_duong_da_luu is None:
        cot_ngay.append("ngay_bao_duong_cuoi")

    for cot in cot_ngay:
        try:
            gia_tri = date.fromisoformat(form.get(cot, ""))
        except ValueError:
            loi[cot] = "Hãy nhập ngày hợp lệ."
            continue
        if gia_tri > hom_nay:
            loi[cot] = "Hãy chọn ngày từ hôm nay trở về trước."
        else:
            xe[cot] = gia_tri

    ngay_su_dung = xe.get("ngay_dua_vao_su_dung")
    nam_san_xuat = xe.get("doi_xe")
    if ngay_su_dung is not None and nam_san_xuat is not None and nam_san_xuat > ngay_su_dung.year:
        loi["doi_xe"] = "Năm sản xuất không được sau năm đưa xe vào sử dụng."

    ngay_bao_duong = ngay_bao_duong_da_luu or xe.get("ngay_bao_duong_cuoi")
    if ngay_su_dung and ngay_bao_duong and ngay_bao_duong < ngay_su_dung:
        if ngay_bao_duong_da_luu is None:
            loi["ngay_bao_duong_cuoi"] = "Hãy chọn ngày từ ngày đưa xe vào sử dụng trở đi."
        else:
            loi["ngay_dua_vao_su_dung"] = "Ngày đưa vào sử dụng phải bằng hoặc trước ngày bảo dưỡng cuối."

    return xe, loi


def hien_thi_form(form, loi, hom_nay, *, ma_xe=None, trang_thai=200):
    return render_template(
        "xe/form.html", form=form, loi=loi, hom_nay=hom_nay, ma_xe=ma_xe
    ), trang_thai


def loi_khi_luu_xe(exc):
    if exc.errno == errorcode.ER_DUP_ENTRY:
        return {"bien_so": "Biển số này đã có trong danh sách xe."}, 409

    current_app.logger.exception("Không lưu được xe vào MySQL")
    return {"chung": "Chưa lưu được xe. Hãy thử lại."}, 503


@bp.route("/them", methods=["GET", "POST"])
def them():
    hom_nay = datetime.now(MUI_GIO_VIET_NAM).date()
    if request.method != "POST":
        return hien_thi_form({}, {}, hom_nay)

    form = request.form
    xe, loi = kiem_tra_xe(form, hom_nay)
    trang_thai = 400

    if not loi:
        try:
            with closing(get_connection()) as connection:
                with closing(connection.cursor()) as cursor:
                    cursor.execute(
                        """
                        INSERT INTO xe (
                            bien_so, mau_xe, hang_san_xuat, model, doi_xe,
                            ngay_dua_vao_su_dung, so_ghe, ngay_bao_duong_cuoi
                        ) VALUES (
                            %(bien_so)s, %(mau_xe)s, %(hang_san_xuat)s, %(model)s,
                            %(doi_xe)s, %(ngay_dua_vao_su_dung)s, %(so_ghe)s,
                            %(ngay_bao_duong_cuoi)s
                        )
                        """,
                        xe,
                    )
                connection.commit()
        except Error as exc:
            loi, trang_thai = loi_khi_luu_xe(exc)
        else:
            return redirect(url_for("xe.danh_sach"), code=303)

    return hien_thi_form(form, loi, hom_nay, trang_thai=trang_thai)


def doc_xe(cursor, ma_xe, *, khoa=False):
    cau_lenh = """
        SELECT bien_so, mau_xe, hang_san_xuat, model, doi_xe,
               ngay_dua_vao_su_dung, so_ghe, ngay_bao_duong_cuoi
        FROM xe
        WHERE ma_xe = %s
    """
    if khoa:
        cau_lenh += " FOR UPDATE"
    cursor.execute(cau_lenh, (ma_xe,))
    xe = cursor.fetchone()
    if xe is None:
        abort(404, description="Không tìm thấy xe.")
    return xe


@bp.get("/<int:ma_xe>/sua")
def sua(ma_xe):
    hom_nay = datetime.now(MUI_GIO_VIET_NAM).date()
    try:
        with closing(get_connection()) as connection:
            with closing(connection.cursor(dictionary=True, buffered=True)) as cursor:
                form = doc_xe(cursor, ma_xe)
    except Error:
        current_app.logger.exception("Không tải được thông tin xe từ MySQL")
        return render_template("xe/index.html", loi="Không tải được thông tin xe."), 503

    return hien_thi_form(form, {}, hom_nay, ma_xe=ma_xe)


def tim_chuyen_truoc_ngay_su_dung(cursor, ma_xe, ngay_su_dung):
    try:
        cursor.execute(
            """
            SELECT ma_chuyen, ngay_chay
            FROM chuyen_xe
            WHERE ma_xe = %s AND ngay_chay < %s
              AND trang_thai IN ('DA_LEN_LICH', 'HOAN_THANH')
            ORDER BY ngay_chay, ma_chuyen
            LIMIT 1
            FOR UPDATE
            """,
            (ma_xe, ngay_su_dung),
        )
    except Error as exc:
        if exc.errno == errorcode.ER_NO_SUCH_TABLE:
            return None
        raise
    return cursor.fetchone()


@bp.post("/<int:ma_xe>/sua")
def luu_sua(ma_xe):
    hom_nay = datetime.now(MUI_GIO_VIET_NAM).date()
    form = request.form.to_dict()
    form.pop("ngay_bao_duong_cuoi", None)

    try:
        with closing(get_connection()) as connection:
            connection.start_transaction()
            with closing(connection.cursor(dictionary=True, buffered=True)) as cursor:
                xe_cu = doc_xe(cursor, ma_xe, khoa=True)
                ngay_bao_duong = xe_cu["ngay_bao_duong_cuoi"]
                form["ngay_bao_duong_cuoi"] = ngay_bao_duong
                xe, loi = kiem_tra_xe(form, hom_nay, ngay_bao_duong_da_luu=ngay_bao_duong)
                if loi:
                    connection.rollback()
                    return hien_thi_form(form, loi, hom_nay, ma_xe=ma_xe, trang_thai=400)

                ngay_su_dung = xe["ngay_dua_vao_su_dung"]
                if ngay_su_dung > xe_cu["ngay_dua_vao_su_dung"]:
                    chuyen = tim_chuyen_truoc_ngay_su_dung(cursor, ma_xe, ngay_su_dung)
                    if chuyen:
                        loi["ngay_dua_vao_su_dung"] = (
                            f"Chuyến {chuyen['ma_chuyen']} có ngày chạy {chuyen['ngay_chay']:%d/%m/%Y}. "
                            "Hãy chọn ngày đưa xe vào sử dụng từ ngày đó trở về trước."
                        )
                        connection.rollback()
                        return hien_thi_form(form, loi, hom_nay, ma_xe=ma_xe, trang_thai=409)

                if xe["so_ghe"] != xe_cu["so_ghe"]:
                    cursor.execute(
                        """
                        SELECT ma_chuyen, so_khach
                        FROM chuyen_xe
                        WHERE ma_xe = %s AND trang_thai = 'DA_LEN_LICH' AND so_khach > %s
                        ORDER BY so_khach DESC, ma_chuyen
                        LIMIT 1
                        FOR UPDATE
                        """,
                        (ma_xe, xe["so_ghe"] - 2),
                    )
                    chuyen = cursor.fetchone()
                    if chuyen:
                        loi["so_ghe"] = (
                            f"Chuyến {chuyen['ma_chuyen']} đã lên lịch cho {chuyen['so_khach']} khách. "
                            f"Xe cần ít nhất {chuyen['so_khach'] + 2} ghế."
                        )
                        connection.rollback()
                        return hien_thi_form(form, loi, hom_nay, ma_xe=ma_xe, trang_thai=409)

                xe["ma_xe"] = ma_xe
                cursor.execute(
                    """
                    UPDATE xe
                    SET bien_so = %(bien_so)s, mau_xe = %(mau_xe)s,
                        hang_san_xuat = %(hang_san_xuat)s, model = %(model)s,
                        doi_xe = %(doi_xe)s, ngay_dua_vao_su_dung = %(ngay_dua_vao_su_dung)s,
                        so_ghe = %(so_ghe)s
                    WHERE ma_xe = %(ma_xe)s
                    """,
                    xe,
                )
            connection.commit()
    except Error as exc:
        loi, trang_thai = loi_khi_luu_xe(exc)
        return hien_thi_form(form, loi, hom_nay, ma_xe=ma_xe, trang_thai=trang_thai)

    return redirect(url_for("xe.danh_sach"), code=303)


def tim_chuyen_tham_chieu(cursor, ma_xe, *, khoa=False):
    cau_lenh = """
        SELECT ma_chuyen
        FROM chuyen_xe
        WHERE ma_xe = %s
        ORDER BY ma_chuyen
        LIMIT 1
    """
    if khoa:
        cau_lenh += " FOR UPDATE"

    try:
        cursor.execute(cau_lenh, (ma_xe,))
    except Error as exc:
        if exc.errno == errorcode.ER_NO_SUCH_TABLE:
            # Hỗ trợ CSDL cục bộ mới được tạo từ xe.sql.
            return None
        raise

    return cursor.fetchone()


@bp.route("/<int:ma_xe>/xoa", methods=["GET", "POST"])
def xoa(ma_xe):
    xac_nhan = request.method == "POST"

    try:
        with closing(get_connection()) as connection:
            if xac_nhan:
                connection.start_transaction()

            with closing(connection.cursor(dictionary=True, buffered=True)) as cursor:
                xe = doc_xe(cursor, ma_xe, khoa=xac_nhan)
                chuyen = tim_chuyen_tham_chieu(cursor, ma_xe, khoa=xac_nhan)
                if not xac_nhan or chuyen:
                    if xac_nhan:
                        connection.rollback()
                    trang_thai = 409 if xac_nhan else 200
                    return render_template(
                        "xe/xoa.html", xe=xe, ma_xe=ma_xe, chuyen=chuyen
                    ), trang_thai

                cursor.execute("DELETE FROM xe WHERE ma_xe = %s", (ma_xe,))

            connection.commit()
    except Error as exc:
        if exc.errno in (errorcode.ER_ROW_IS_REFERENCED, errorcode.ER_ROW_IS_REFERENCED_2):
            loi = "Xe đang được dữ liệu liên quan tham chiếu nên không thể xóa."
            trang_thai = 409
        else:
            current_app.logger.exception("Không thực hiện được yêu cầu xóa xe từ MySQL")
            loi = "Chưa thể thực hiện yêu cầu xóa xe. Hãy thử lại."
            trang_thai = 503
        return render_template("xe/xoa.html", loi=loi), trang_thai

    return redirect(url_for("xe.danh_sach"), code=303)


@bp.get("/<int:ma_xe>/lich-su")
def lich_su(ma_xe):
    xe = None
    try:
        with closing(get_connection()) as connection:
            with closing(connection.cursor(dictionary=True, buffered=True)) as cursor:
                xe = doc_xe(cursor, ma_xe)
                cursor.execute(
                    """
                    SELECT c.ma_chuyen, c.ngay_chay, c.so_khach, c.gia_ve, c.trang_thai,
                           t.diem_dau, t.diem_cuoi,
                           lai_xe.ho_ten AS ten_lai_xe, phu_xe.ho_ten AS ten_phu_xe
                    FROM chuyen_xe AS c
                    JOIN tuyen_xe AS t ON t.ma_tuyen = c.ma_tuyen
                    JOIN tai_xe AS lai_xe ON lai_xe.ma_tai_xe = c.ma_lai_xe
                    JOIN tai_xe AS phu_xe ON phu_xe.ma_tai_xe = c.ma_phu_xe
                    WHERE c.ma_xe = %s
                    ORDER BY c.ngay_chay DESC, c.ma_chuyen DESC
                    """,
                    (ma_xe,),
                )
                danh_sach_chuyen = cursor.fetchall()
    except Error as exc:
        if exc.errno == errorcode.ER_NO_SUCH_TABLE and xe is not None:
            loi = "Cần tạo các bảng chuyến xe, tuyến xe và tài xế theo SQL chung để xem lịch sử."
        else:
            current_app.logger.exception("Không tải được lịch sử chuyến từ MySQL")
            loi = "Không tải được lịch sử chuyến. Hãy kiểm tra kết nối MySQL và cấu trúc bảng."
        return render_template("xe/lich_su.html", xe=xe, loi=loi), 503

    return render_template("xe/lich_su.html", xe=xe, danh_sach_chuyen=danh_sach_chuyen)
