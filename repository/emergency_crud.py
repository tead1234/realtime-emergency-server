import sqlite3
from datetime import datetime

# 데이터베이스 연결
db_path = "hospital_data.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

## hospitals 테이블 생성
cursor.execute('''
CREATE TABLE IF NOT EXISTS hospitals (
    hospital_id INTEGER PRIMARY KEY AUTOINCREMENT,
    hospital_name TEXT,
    hospital_phone TEXT,
    hospital_address TEXT,
    hospital_lat REAL,
    hospital_lng REAL,
    hospital_type INTEGER,
    capacity INTEGER,
    status_percent DECIMAL,
    update_dt TIMESTAMP 
)
''')

## transport_logs 테이블 생성
cursor.execute('''
CREATE TABLE IF NOT EXISTS transport_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    hospital_id INTEGER,
    patient_id INTEGER,
    start_datetime TIMESTAMP,
    end_datetime TIMESTAMP,
    status INTEGER DEFAULT 0,
    FOREIGN KEY (hospital_id) REFERENCES hospitals (hospital_id)
)
''')
conn.commit()

## 데이터베이스 연결
def connect_to_db(db_path):
    """
    데이터베이스 연결 함수
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    print("Database connected.")
    return conn, cursor

def close_db_connection(conn):
    """
    데이터베이스 종료 함수
    """
    if conn:
        conn.close()
        print("Database connection closed.")


## CRUD 함수 정의
## Create
## 병원 등록
def create_hospital(name, phone, address, lat, lng, type, capacity, status_percent):
    """
    신규 병원 등록 함수
    """
    update_dt = datetime.now().isoformat()
    cursor.execute('''
        INSERT INTO hospitals (hospital_name, hospital_phone, hospital_address, hospital_lat, hospital_lng, hospital_type, capacity, status_percent, update_dt)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (name, phone, address, lat, lng, type, capacity, status_percent, update_dt))
    conn.commit()

## 로그 등록
def create_transport_log(hospital_id, patient_id, start_datetime, end_datetime, status):
    """
    로그 추가 함수 (한개씩)
    """
    # transport_logs에 로그 추가
    cursor.execute('''
        INSERT INTO transport_logs (hospital_id, patient_id, start_datetime, end_datetime, status)
        VALUES (?, ?, ?, ?, ?)
    ''', (hospital_id, patient_id, start_datetime, end_datetime, status))

    conn.commit()


def create_multiple_transport_logs(log_entries):
    """
    로그 추가 함수 (여러개)
    ex)
    log_entries = [
    (1, 101, datetime.now().isoformat(), datetime.now().isoformat(), 0),
    (1, 102, datetime.now().isoformat(), datetime.now().isoformat(), 1)
    ]

    create_multiple_transport_logs(log_entries)
    """
    cursor.executemany('''
        INSERT INTO transport_logs (hospital_id, patient_id, start_datetime, end_datetime, status)
        VALUES (?, ?, ?, ?, ?)
    ''', log_entries)

    conn.commit()


## Read - 데이터 조회
def read_hospitals():
    cursor.execute("SELECT * FROM hospitals")
    return cursor.fetchall()

def read_transport_logs():
    cursor.execute("SELECT * FROM transport_logs")
    return cursor.fetchall()

## Update - 데이터 업데이트
def update_transport_log_start(hospital_id, patient_id):
    """
    환자 이송 시작시, 이송중 1으로 업데이트
    """
    start_datetime = datetime.now().isoformat()
    cursor.execute('''
    UPDATE transport_logs
    SET status = 1,
        start_datetime = ?
    WHERE hospital_id = ? AND patient_id = ?
    ''', (start_datetime, hospital_id, patient_id))
    conn.commit()

def update_transport_log_end(hospital_id, patient_id):
    """
    환자 이송 완료시, 성공 2으로 업데이트
    """
    end_datetime = datetime.now().isoformat()
    cursor.execute('''
    UPDATE transport_logs
    SET status = 2,
        end_datetime = ?
    WHERE hospital_id = ? AND patient_id = ?
    ''', (end_datetime, hospital_id, patient_id))
    conn.commit()


def update_transport_log_deny(hospital_id, patient_id):
    """
    환자 이송 거절시, 거절 3로 업데이트,
    거절률, 업데이트 날짜 업데이트
    """
    # transport_logs 테이블에서 status를 3으로 업데이트
    cursor.execute('''
        UPDATE transport_logs
        SET status = 3
        WHERE hospital_id = ? AND patient_id = ?
    ''', (hospital_id, patient_id))

    current_time = datetime.now().isoformat()

    cursor.execute('''
        SELECT 
            (SELECT COUNT(*) FROM transport_logs WHERE hospital_id = ?) AS total_logs,
            (SELECT COUNT(*) FROM transport_logs WHERE hospital_id = ? AND status = 3) AS denied_logs
    ''', (hospital_id, hospital_id))
    result = cursor.fetchone()
    total_logs, denied_logs = result

    # 거절률 계산
    if total_logs > 0:
        status_percent = round((denied_logs / total_logs) * 100, 2)
    else:
        status_percent = 0.0

    # hospitals 테이블의 status_percent와 update_dt 업데이트
    cursor.execute('''
        UPDATE hospitals
        SET status_percent = ?,
            update_dt = ?
        WHERE hospital_id = ?
    ''', (status_percent, current_time, hospital_id))
    conn.commit()

## Delete - 데이터 삭제
def delete_hospital(hospital_id):
    cursor.execute("DELETE FROM hospitals WHERE hospital_id = ?", (hospital_id,))
    conn.commit()

def delete_transport_log(log_id):
    cursor.execute("DELETE FROM transport_logs WHERE log_id = ?", (log_id,))
    conn.commit()



# # 예제 실행시 주석 제거
# create_hospital(
#     name="서울중앙병원",
#     phone="02-1234-5678",
#     address="서울특별시 중구 세종대로 110",
#     lat=37.5665,
#     lng=126.9780,
#     type=1,  # 예: 1차 병원
#     capacity=100,
#     status_percent=0
# )
#
# # 환자 ID 101번 환자가 서울중앙병원에 호출된 로그 추가
# create_transport_log(
#     hospital_id=1,            # 서울중앙병원 ID
#     patient_id=101,           # 환자 ID
#     start_datetime='',
#     end_datetime='',
#     status=0                  # 상태 0 (요청)
# )
#
# # 이송 시작 상태로 변경
# update_transport_log_start(hospital_id=1, patient_id=101)
#
# # 이송 완료 상태로 변경
# update_transport_log_end(hospital_id=1, patient_id=101)
#
# log_entries = [
#     (1, 101, datetime.now().isoformat(), datetime.now().isoformat(), 0),
#     (1, 102, datetime.now().isoformat(), datetime.now().isoformat(), 1),
#     (2, 103, datetime.now().isoformat(), datetime.now().isoformat(), 2),
#     (3, 104, datetime.now().isoformat(), datetime.now().isoformat(), 0)
# ]
# create_multiple_transport_logs(log_entries)
#
# # 조회 결과 확인
# hospitals_data = read_hospitals()
# transport_logs_data = read_transport_logs()
#
# print(11,hospitals_data)
# print(22,transport_logs_data)
#
# 데이터베이스 연결 종료
# conn.close()
