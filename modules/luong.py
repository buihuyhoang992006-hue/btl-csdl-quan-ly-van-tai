from contextlib import closing
from datetime import datetime, timedelta, timezone

from flask import Blueprint, current_app, render_template, request
from mysql.connector import Error, errorcode

from db import get_connection


bp = Blueprint("luong", __name__, url_prefix="/bao-cao")
MUI_GIO_VIET_NAM = timezone(timedelta(hours=7))


def hom_nay_vn():
    return datetime.now(MUI_GIO_VIET_NAM).date()


SQL_BAO_CAO_LUONG = """
    SELECT
        tx.ma_tai_xe,
        tx.ho_ten,
        COALESCE(lx.so_chuyen_lai, 0) AS so_chuyen_lai,
        COALESCE(px.so_chuyen_phu, 0) AS so_chuyen_phu,
        COALESCE(lx.luong_lai, 0) + COALESCE(px.luong_phu, 0) AS tong_luong
    FROM tai_xe tx
    LEFT JOIN (
        SELECT
            ma_lai_xe,
            COUNT(*) AS so_chuyen_lai,
            SUM(
                200000 * CASE do_phuc_tap_chot
                    WHEN 1 THEN 1.00
                    WHEN 2 THEN 1.25
                    WHEN 3 THEN 1.50
                    ELSE 0
                END
            ) AS luong_lai
        FROM chuyen_xe
        WHERE trang_thai = 'HOAN_THANH'
          AND ngay_chay >= %s
          AND ngay_chay < DATE_ADD(%s, INTERVAL 1 MONTH)
          AND ngay_chay <= %s
        GROUP BY ma_lai_xe
    ) lx ON tx.ma_tai_xe = lx.ma_lai_xe
    LEFT JOIN (
        SELECT
            ma_phu_xe,
            COUNT(*) AS so_chuyen_phu,
            SUM(
                100000 * CASE do_phuc_tap_chot
                    WHEN 1 THEN 1.00
                    WHEN 2 THEN 1.25
                    WHEN 3 THEN 1.50
                    ELSE 0
                END
            ) AS luong_phu
        FROM chuyen_xe
        WHERE trang_thai = 'HOAN_THANH'
          AND ngay_chay >= %s
          AND ngay_chay < DATE_ADD(%s, INTERVAL 1 MONTH)
          AND ngay_chay <= %s
        GROUP BY ma_phu_xe
    ) px ON tx.ma_tai_xe = px.ma_phu_xe
    ORDER BY tx.ho_ten, tx.ma_tai_xe
"""


@bp.get("/luong")
def bao_cao_luong():
    hom_nay = hom_nay_vn()
    thang_hien_tai = hom_nay.strftime("%Y-%m")
    thang_chon = request.args.get("thang", thang_hien_tai).strip()

    loi = None
    danh_sach_luong = []

    try:
        ngay_dau_thang = datetime.strptime(thang_chon, "%Y-%m").date().replace(day=1)
        if ngay_dau_thang > hom_nay.replace(day=1):
            loi = "Chỉ được chọn tháng hiện tại hoặc các tháng đã qua."
    except ValueError:
        loi = "Tháng lựa chọn không hợp lệ."

    if loi is None:
        try:
            with closing(get_connection()) as conn:
                with closing(conn.cursor(dictionary=True)) as cursor:
                    cursor.execute(
                        SQL_BAO_CAO_LUONG,
                        (
                            ngay_dau_thang,
                            ngay_dau_thang,
                            hom_nay,
                            ngay_dau_thang,
                            ngay_dau_thang,
                            hom_nay,
                        ),
                    )
                    danh_sach_luong = cursor.fetchall()
        except Error as exc:
            if exc.errno == errorcode.ER_NO_SUCH_TABLE:
                loi = "Chưa có đủ bảng chuyen_xe hoặc tai_xe trong CSDL."
            else:
                current_app.logger.exception("Lỗi truy vấn báo cáo lương")
                loi = "Không thể truy xuất dữ liệu lương tài xế từ MySQL."

    return render_template(
        "luong/index.html",
        danh_sach_luong=danh_sach_luong,
        thang_chon=thang_chon,
        thang_hien_tai=thang_hien_tai,
        hom_nay=hom_nay,
        loi=loi,
    )