
from contextlib import closing
from datetime import datetime

from flask import Blueprint, render_template, request
from mysql.connector import Error

from db import get_connection


bp = Blueprint("doanh_thu", __name__, url_prefix="/bao-cao")


@bp.route("/doanh-thu", methods=["GET"])
def doanh_thu():
    tu_ngay = request.args.get("tu_ngay", "").strip()
    den_ngay = request.args.get("den_ngay", "").strip()

    danh_sach_doanh_thu = []
    loi = None
    da_loc = False

    if tu_ngay or den_ngay:
        try:
            if not tu_ngay or not den_ngay:
                raise ValueError

            ngay_bat_dau = datetime.strptime(tu_ngay, "%Y-%m-%d").date()
            ngay_ket_thuc = datetime.strptime(den_ngay, "%Y-%m-%d").date()

            if ngay_bat_dau > ngay_ket_thuc:
                loi = "Ngày bắt đầu không được sau ngày kết thúc."
            else:
                sql = """
                    SELECT
                        x.ma_xe,
                        x.bien_so,
                        COUNT(c.ma_chuyen) AS so_chuyen,
                        COALESCE(SUM(c.so_khach), 0) AS tong_khach,
                        COALESCE(SUM(c.so_khach * c.gia_ve), 0) AS doanh_thu
                    FROM xe x
                    LEFT JOIN chuyen_xe c
                        ON x.ma_xe = c.ma_xe
                        AND c.trang_thai = 'HOAN_THANH'
                        AND c.ngay_chay BETWEEN %s AND %s
                    GROUP BY x.ma_xe, x.bien_so
                    ORDER BY x.bien_so
                """

                with closing(get_connection()) as conn:
                    with closing(conn.cursor(dictionary=True)) as cursor:
                        cursor.execute(
                            sql,
                            (ngay_bat_dau, ngay_ket_thuc)
                        )
                        danh_sach_doanh_thu = cursor.fetchall()

                da_loc = True

        except ValueError:
            loi = "Vui lòng nhập ngày hợp lệ và đầy đủ."

        except Error:
            loi = "Không thể truy xuất dữ liệu doanh thu."

    return render_template(
        "bao_cao/doanh_thu.html",
        danh_sach_doanh_thu=danh_sach_doanh_thu,
        tu_ngay=tu_ngay,
        den_ngay=den_ngay,
        loi=loi,
        da_loc=da_loc
    )

from datetime import datetime


@bp.route("/thong-ke-tuyen", methods=["GET"])
def thong_ke_tuyen():
    # Lấy tháng cần thống kê, mặc định là tháng hiện tại
    thang = request.args.get(
        "thang",
        datetime.now().strftime("%Y-%m")
    )

    try:
        ngay_dau = datetime.strptime(thang, "%Y-%m").date()
    except ValueError:
        ngay_dau = datetime.now().date().replace(day=1)
        thang = ngay_dau.strftime("%Y-%m")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    sql = """
        SELECT
            t.ma_tuyen,
            t.diem_dau,
            t.diem_cuoi,
            t.do_dai_km,
            COUNT(c.ma_chuyen) AS so_chuyen,
            COALESCE(SUM(c.so_khach), 0) AS tong_khach
        FROM tuyen_xe t
        LEFT JOIN chuyen_xe c
            ON t.ma_tuyen = c.ma_tuyen
            AND c.trang_thai = 'HOAN_THANH'
            AND c.ngay_chay >= %s
            AND c.ngay_chay < DATE_ADD(%s, INTERVAL 1 MONTH)
        GROUP BY
            t.ma_tuyen,
            t.diem_dau,
            t.diem_cuoi,
            t.do_dai_km
        ORDER BY t.ma_tuyen
    """

    cursor.execute(sql, (ngay_dau, ngay_dau))
    ds_tuyen = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "bao_cao/thong_ke_tuyen.html",
        ds_tuyen=ds_tuyen,
        thang=thang
    )
