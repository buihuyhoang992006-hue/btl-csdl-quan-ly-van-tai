
from contextlib import closing
from datetime import datetime, timedelta, timezone

from flask import Flask, render_template
from mysql.connector import Error

from db import get_connection
from modules.xe import bp as xe_bp
from modules.chuyenxe import bp as chuyen_xe_bp

from modules.bao_duong import (
    bp as bao_duong_bp,
    lay_bao_cao,
    co_bang_chuyen_xe
)


# KHOI TAO FLASK
app = Flask(__name__)

# DANG KY BLUEPRINT
app.register_blueprint(xe_bp)
app.register_blueprint(chuyen_xe_bp)
app.register_blueprint(bao_duong_bp)


# TRANG CHU - DASHBOARD
@app.route("/")
def trang_chu():

    hom_nay = datetime.now(
        timezone(timedelta(hours=7))
    ).date()

    thong_ke = {
        "tong_xe": None,
        "chuyen_hom_nay": None,
        "xe_qua_han": None
    }

    thong_bao = []

    try:
        with closing(get_connection()) as conn:
            with closing(
                conn.cursor(dictionary=True)
            ) as cursor:

                # Dem tong so xe
                cursor.execute("""
                    SELECT COUNT(*) AS tong_xe
                    FROM xe
                """)

                thong_ke["tong_xe"] = (
                    cursor.fetchone()["tong_xe"]
                )

                if co_bang_chuyen_xe(cursor):

                    # Dem chuyen trong ngay
                    cursor.execute("""
                        SELECT COUNT(*) AS so_chuyen
                        FROM chuyen_xe
                        WHERE ngay_chay = %s
                          AND trang_thai <> 'DA_HUY'
                    """, (hom_nay,))

                    thong_ke["chuyen_hom_nay"] = (
                        cursor.fetchone()["so_chuyen"]
                    )

                    # Dung chung cong thuc bao duong
                    danh_sach = lay_bao_cao(
                        cursor, hom_nay
                    )

                    thong_ke["xe_qua_han"] = sum(
                        1
                        for xe in danh_sach
                        if xe["ngay_den_han"] < hom_nay
                    )

                else:
                    thong_bao.append(
                        "Chưa có bảng chuyen_xe. "
                        "Chưa thể thống kê chuyến xe "
                        "và hạn bảo dưỡng."
                    )

    except Error:
        app.logger.exception("Loi Dashboard")
        thong_bao.append(
            "Không tải được đầy đủ số liệu MySQL."
        )

    return render_template(
        "index.html",
        thong_ke=thong_ke,
        thong_bao=thong_bao,
        hom_nay=hom_nay
    )


if __name__ == "__main__":
    app.run(debug=True)
