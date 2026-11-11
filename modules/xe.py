from contextlib import closing
from datetime import datetime, timedelta, timezone

from flask import Blueprint, current_app, render_template
from mysql.connector import Error

from db import get_connection


bp = Blueprint("xe", __name__, url_prefix="/xe")


@bp.get("")
def danh_sach():
    ngay_xem = datetime.now(timezone(timedelta(hours=7))).date()

    try:
        with closing(get_connection()) as connection:
            with closing(connection.cursor(dictionary=True)) as cursor:
                cursor.execute(
                    """
                    SELECT bien_so, mau_xe, hang_san_xuat, model, doi_xe,
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
