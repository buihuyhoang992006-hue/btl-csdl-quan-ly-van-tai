from contextlib import closing
from datetime import datetime, timedelta, timezone

from flask import Flask, render_template
from mysql.connector import Error

from db import get_connection

# TV1 - Quan ly xe
from modules.xe import bp as xe_bp

# TV2 - Quan ly tuyen va bao cao doanh thu
from modules.tuyen_xe import bp as tuyen_xe_bp
from modules.bao_cao import bp as doanh_thu_bp

# TV4 - Quan ly chuyen xe
from modules.chuyenxe import bp as chuyen_xe_bp
from modules.tai_xe import bp as tai_xe_bp
from modules.luong import bp as luong_bp

# TV5 - Bao duong xe
from modules.bao_duong import (
    bp as bao_duong_bp,
    lay_bao_cao,
    co_bang_chuyen_xe
)


# ==========================================
# 1. KHOI TAO FLASK
# ==========================================

app = Flask(__name__)


# ==========================================
# 2. DANG KY BLUEPRINT
# ==========================================

app.register_blueprint(xe_bp)
app.register_blueprint(tuyen_xe_bp)
app.register_blueprint(doanh_thu_bp)
app.register_blueprint(chuyen_xe_bp)
app.register_blueprint(bao_duong_bp)
app.register_blueprint(tai_xe_bp)
app.register_blueprint(luong_bp)


# ==========================================
# 3. TRANG CHU - DASHBOARD
# ==========================================

@app.route("/")
def trang_chu():

    # Lay ngay hien tai theo gio Viet Nam
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

                # 3.1. Dem tong so xe
                cursor.execute("""
                    SELECT COUNT(*) AS tong_xe
                    FROM xe
                """)

                thong_ke["tong_xe"] = (
                    cursor.fetchone()["tong_xe"]
                )

                # 3.2. Kiem tra bang chuyen_xe
                if co_bang_chuyen_xe(cursor):

                    # 3.3. Dem chuyen trong ngay
                    cursor.execute("""
                        SELECT COUNT(*) AS so_chuyen
                        FROM chuyen_xe
                        WHERE ngay_chay = %s
                          AND trang_thai <> 'DA_HUY'
                    """, (hom_nay,))

                    thong_ke["chuyen_hom_nay"] = (
                        cursor.fetchone()["so_chuyen"]
                    )

                    # 3.4. Tinh so xe qua han bao duong
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
        app.logger.exception(
            "Khong lay duoc du lieu Dashboard"
        )

        thong_bao.append(
            "Không tải được đầy đủ số liệu MySQL. "
            "Hãy kiểm tra các bảng dữ liệu."
        )

    return render_template(
        "index.html",
        thong_ke=thong_ke,
        thong_bao=thong_bao,
        hom_nay=hom_nay
    )


# ==========================================
# 4. CHAY UNG DUNG
# ==========================================

if __name__ == "__main__":
    app.run(debug=True)