
from contextlib import closing
from datetime import date, datetime, timedelta, timezone

from flask import (
    Blueprint, abort, current_app, redirect,
    render_template, request, url_for
)
from mysql.connector import Error
from db import get_connection


# 1. KHAI BAO BLUEPRINT
bp = Blueprint(
    "bao_duong",
    __name__,
    url_prefix="/bao-cao/bao-duong"
)


# 2. LAY NGAY HIEN TAI THEO GIO VIET NAM
def hom_nay_vn():
    return datetime.now(
        timezone(timedelta(hours=7))
    ).date()


# 3. KIEM TRA BANG CHUYEN XE
def co_bang_chuyen_xe(cursor):
    cursor.execute("""
        SELECT COUNT(*) AS so_bang
        FROM information_schema.tables
        WHERE table_schema = DATABASE()
          AND table_name = 'chuyen_xe'
    """)
    return cursor.fetchone()["so_bang"] > 0


# 4. SQL TINH HAN BAO DUONG
SQL_BAO_DUONG = """
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
       AND c.ngay_chay <= %s

    GROUP BY
        x.ma_xe,
        x.bien_so,
        x.ngay_bao_duong_cuoi
) AS k

ORDER BY ngay_den_han, k.bien_so
"""


# 5. HAM LAY BAO CAO
def lay_bao_cao(cursor, ngay_xem):
    cursor.execute(SQL_BAO_DUONG, (ngay_xem,))
    return cursor.fetchall()


# 6. TRANG DANH SACH BAO DUONG
@bp.get("")
def danh_sach():
    ngay_xem = hom_nay_vn()

    qua_han = []
    den_han = []
    con_han = []
    xe_cho_du_lieu = []
    thong_bao = None
    loi = None

    try:
        with closing(get_connection()) as conn:
            with closing(
                conn.cursor(dictionary=True)
            ) as cursor:

                if co_bang_chuyen_xe(cursor):

                    danh_sach_xe = lay_bao_cao(
                        cursor, ngay_xem
                    )

                    for xe in danh_sach_xe:

                        if xe["ngay_den_han"] < ngay_xem:
                            qua_han.append(xe)

                        elif xe["ngay_den_han"] == ngay_xem:
                            den_han.append(xe)

                        else:
                            con_han.append(xe)

                else:
                    thong_bao = (
                        "Chưa có bảng chuyen_xe. "
                        "Chưa thể tính hạn bảo dưỡng, "
                        "nhưng vẫn có thể cập nhật ngày "
                        "bảo dưỡng của từng xe."
                    )

                    cursor.execute("""
                        SELECT
                            ma_xe,
                            bien_so,
                            ngay_bao_duong_cuoi
                        FROM xe
                        ORDER BY bien_so
                    """)

                    xe_cho_du_lieu = cursor.fetchall()

    except Error:
        current_app.logger.exception(
            "Loi truy van bao duong"
        )
        loi = "Không tải được dữ liệu bảo dưỡng từ MySQL."

    return render_template(
        "bao_duong/index.html",
        qua_han=qua_han,
        den_han=den_han,
        con_han=con_han,
        xe_cho_du_lieu=xe_cho_du_lieu,
        thong_bao=thong_bao,
        loi=loi,
        ngay_xem=ngay_xem
    ), (503 if loi else 200)


# 7. CAP NHAT NGAY BAO DUONG
@bp.route(
    "/<int:ma_xe>/cap-nhat",
    methods=["GET", "POST"]
)
def cap_nhat(ma_xe):
    hom_nay = hom_nay_vn()
    loi = None
    ngay_nhap = request.form.get(
        "ngay_bao_duong_moi", ""
    )

    try:
        with closing(get_connection()) as conn:

            if request.method == "POST":
                conn.start_transaction()

            with closing(
                conn.cursor(dictionary=True, buffered=True)
            ) as cursor:

                sql = """
                    SELECT
                        ma_xe,
                        bien_so,
                        ngay_bao_duong_cuoi
                    FROM xe
                    WHERE ma_xe = %s
                """

                if request.method == "POST":
                    sql += " FOR UPDATE"

                cursor.execute(sql, (ma_xe,))
                xe = cursor.fetchone()

                if xe is None:
                    abort(404, "Không tìm thấy xe.")

                if request.method == "POST":

                    try:
                        ngay_moi = date.fromisoformat(
                            ngay_nhap
                        )
                    except ValueError:
                        loi = "Ngày nhập không hợp lệ."
                    else:
                        if ngay_moi < xe["ngay_bao_duong_cuoi"]:
                            loi = (
                                "Ngày mới không được trước "
                                "ngày bảo dưỡng cuối."
                            )
                        elif ngay_moi > hom_nay:
                            loi = (
                                "Ngày bảo dưỡng không được "
                                "sau hôm nay."
                            )

                    if loi is None:
                        cursor.execute("""
                            UPDATE xe
                            SET ngay_bao_duong_cuoi = %s
                            WHERE ma_xe = %s
                        """, (ngay_moi, ma_xe))

                        conn.commit()

                        return redirect(
                            url_for(
                                "bao_duong.danh_sach",
                                saved=1
                            ),
                            code=303
                        )

                    conn.rollback()

                    return render_template(
                        "bao_duong/cap_nhat.html",
                        xe=xe,
                        hom_nay=hom_nay,
                        ngay_nhap=ngay_nhap,
                        loi=loi
                    ), 400

    except Error:
        current_app.logger.exception(
            "Loi cap nhat bao duong"
        )
        return render_template(
            "bao_duong/cap_nhat.html",
            xe=None,
            hom_nay=hom_nay,
            ngay_nhap=ngay_nhap,
            loi="Không thể truy cập MySQL."
        ), 503

    return render_template(
        "bao_duong/cap_nhat.html",
        xe=xe,
        hom_nay=hom_nay,
        ngay_nhap=ngay_nhap,
        loi=loi
    )
