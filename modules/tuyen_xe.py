
from contextlib import closing
from decimal import Decimal, InvalidOperation

from flask import Blueprint, abort, current_app, redirect, render_template, request, url_for
from mysql.connector import Error, errorcode

from db import get_connection


bp = Blueprint("tuyen_xe", __name__, url_prefix="/tuyen-xe")


@bp.get("")
def danh_sach():
    try:
        with closing(get_connection()) as connection:
            with closing(connection.cursor(dictionary=True)) as cursor:
                cursor.execute("""
                    SELECT ma_tuyen, diem_dau, diem_cuoi,
                           do_dai_km, do_phuc_tap
                    FROM tuyen_xe
                    ORDER BY ma_tuyen
                """)
                danh_sach_tuyen = cursor.fetchall()

    except Error:
        current_app.logger.exception("Không tải được danh sách tuyến xe từ MySQL")
        return render_template(
            "tuyen_xe/index.html",
            loi="Không tải được danh sách tuyến xe. Hãy kiểm tra kết nối MySQL."
        ), 503

    return render_template(
        "tuyen_xe/index.html",
        danh_sach_tuyen=danh_sach_tuyen
    )


def kiem_tra_tuyen(form):
    tuyen = {}
    loi = {}

    for cot in ("diem_dau", "diem_cuoi"):
        gia_tri = form.get(cot, "").strip()

        if not gia_tri:
            loi[cot] = "Hãy nhập thông tin này."
        elif len(gia_tri) > 100:
            loi[cot] = "Nhập tối đa 100 ký tự."
        else:
            tuyen[cot] = gia_tri

    try:
        do_dai = Decimal(form.get("do_dai_km", "").strip())

        if not do_dai.is_finite() or not (0 < do_dai <= Decimal("999999.99")):
            loi["do_dai_km"] = "Độ dài tuyến phải lớn hơn 0 và không vượt quá 999999.99 km."
        elif do_dai != do_dai.quantize(Decimal("0.01")):
            loi["do_dai_km"] = "Độ dài tuyến chỉ được có tối đa 2 chữ số thập phân."
        else:
            tuyen["do_dai_km"] = do_dai

    except (InvalidOperation, ValueError):
        loi["do_dai_km"] = "Hãy nhập độ dài tuyến hợp lệ."

    try:
        do_phuc_tap = int(form.get("do_phuc_tap", ""))

        if do_phuc_tap not in (1, 2, 3):
            loi["do_phuc_tap"] = "Mức độ phức tạp chỉ được là 1, 2 hoặc 3."
        else:
            tuyen["do_phuc_tap"] = do_phuc_tap

    except ValueError:
        loi["do_phuc_tap"] = "Hãy nhập mức độ phức tạp hợp lệ."

    return tuyen, loi


def hien_thi_form(form, loi, ma_tuyen=None, trang_thai=200):
    return render_template(
        "tuyen_xe/form.html",
        form=form,
        loi=loi,
        ma_tuyen=ma_tuyen
    ), trang_thai


@bp.route("/them", methods=["GET", "POST"])
def them():
    if request.method != "POST":
        return hien_thi_form({}, {})

    form = request.form
    tuyen, loi = kiem_tra_tuyen(form)

    if not loi:
        try:
            with closing(get_connection()) as connection:
                with closing(connection.cursor()) as cursor:
                    cursor.execute("""
                        INSERT INTO tuyen_xe (
                            diem_dau, diem_cuoi, do_dai_km, do_phuc_tap
                        )
                        VALUES (
                            %(diem_dau)s, %(diem_cuoi)s,
                            %(do_dai_km)s, %(do_phuc_tap)s
                        )
                    """, tuyen)

                connection.commit()

        except Error:
            current_app.logger.exception("Không thêm được tuyến xe vào MySQL")
            loi["chung"] = "Chưa thêm được tuyến xe. Hãy thử lại."
            return hien_thi_form(form, loi, trang_thai=503)

        return redirect(url_for("tuyen_xe.danh_sach"), code=303)

    return hien_thi_form(form, loi, trang_thai=400)


def doc_tuyen(cursor, ma_tuyen, khoa=False):
    cau_lenh = """
        SELECT ma_tuyen, diem_dau, diem_cuoi, do_dai_km, do_phuc_tap
        FROM tuyen_xe
        WHERE ma_tuyen = %s
    """

    if khoa:
        cau_lenh += " FOR UPDATE"

    cursor.execute(cau_lenh, (ma_tuyen,))
    tuyen = cursor.fetchone()

    if tuyen is None:
        abort(404, description="Không tìm thấy tuyến xe.")

    return tuyen


@bp.get("/<int:ma_tuyen>/sua")
def sua(ma_tuyen):
    try:
        with closing(get_connection()) as connection:
            with closing(connection.cursor(dictionary=True)) as cursor:
                form = doc_tuyen(cursor, ma_tuyen)

    except Error:
        current_app.logger.exception("Không tải được thông tin tuyến xe")
        return render_template(
            "tuyen_xe/index.html",
            loi="Không tải được thông tin tuyến xe."
        ), 503

    return hien_thi_form(form, {}, ma_tuyen=ma_tuyen)


@bp.post("/<int:ma_tuyen>/sua")
def luu_sua(ma_tuyen):
    form = request.form
    tuyen, loi = kiem_tra_tuyen(form)

    if loi:
        return hien_thi_form(form, loi, ma_tuyen=ma_tuyen, trang_thai=400)

    try:
        with closing(get_connection()) as connection:
            with closing(connection.cursor()) as cursor:
                cursor.execute("""
                    UPDATE tuyen_xe
                    SET diem_dau = %(diem_dau)s,
                        diem_cuoi = %(diem_cuoi)s,
                        do_dai_km = %(do_dai_km)s,
                        do_phuc_tap = %(do_phuc_tap)s
                    WHERE ma_tuyen = %(ma_tuyen)s
                """, {**tuyen, "ma_tuyen": ma_tuyen})

                if cursor.rowcount == 0:
                    cursor.execute(
                        "SELECT ma_tuyen FROM tuyen_xe WHERE ma_tuyen = %s",
                        (ma_tuyen,)
                    )
                    if cursor.fetchone() is None:
                        abort(404, description="Không tìm thấy tuyến xe.")

            connection.commit()

    except Error:
        current_app.logger.exception("Không cập nhật được tuyến xe")
        loi["chung"] = "Chưa cập nhật được tuyến xe. Hãy thử lại."
        return hien_thi_form(form, loi, ma_tuyen=ma_tuyen, trang_thai=503)

    return redirect(url_for("tuyen_xe.danh_sach"), code=303)


def tim_chuyen_tham_chieu(cursor, ma_tuyen):
    try:
        cursor.execute("""
            SELECT ma_chuyen
            FROM chuyen_xe
            WHERE ma_tuyen = %s
            ORDER BY ma_chuyen
            LIMIT 1
        """, (ma_tuyen,))

    except Error as exc:
        if exc.errno == errorcode.ER_NO_SUCH_TABLE:
            return None
        raise

    return cursor.fetchone()


@bp.route("/<int:ma_tuyen>/xoa", methods=["GET", "POST"])
def xoa(ma_tuyen):
    xac_nhan = request.method == "POST"

    try:
        with closing(get_connection()) as connection:
            if xac_nhan:
                connection.start_transaction()

            with closing(connection.cursor(dictionary=True)) as cursor:
                tuyen = doc_tuyen(cursor, ma_tuyen, khoa=xac_nhan)
                chuyen = tim_chuyen_tham_chieu(cursor, ma_tuyen)

                if not xac_nhan or chuyen:
                    if xac_nhan:
                        connection.rollback()

                    return render_template(
                        "tuyen_xe/xoa.html",
                        tuyen=tuyen,
                        ma_tuyen=ma_tuyen,
                        chuyen=chuyen
                    ), 409 if xac_nhan else 200

                cursor.execute(
                    "DELETE FROM tuyen_xe WHERE ma_tuyen = %s",
                    (ma_tuyen,)
                )

            connection.commit()

    except Error as exc:
        if exc.errno in (
            errorcode.ER_ROW_IS_REFERENCED,
            errorcode.ER_ROW_IS_REFERENCED_2
        ):
            loi = "Tuyến xe đang được chuyến xe tham chiếu nên không thể xóa."
            trang_thai = 409
        else:
            current_app.logger.exception("Không xóa được tuyến xe")
            loi = "Chưa thể thực hiện yêu cầu xóa tuyến xe. Hãy thử lại."
            trang_thai = 503

        return render_template("tuyen_xe/xoa.html", loi=loi), trang_thai

    return redirect(url_for("tuyen_xe.danh_sach"), code=303)
