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
    status_cnt INTEGER,
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
    status INTEGER,
    FOREIGN KEY (hospital_id) REFERENCES hospitals (hospital_id)
)
''')
conn.commit()

## CRUD 함수 정의
## Create
## 병원 등록
def create_hospital(name, phone, address, lat, lng, type, capacity, status_cnt):
    update_dt = datetime.now().isoformat()
    cursor.execute('''
        INSERT INTO hospitals (hospital_name, hospital_phone, hospital_address, hospital_lat, hospital_lng, hospital_type, capacity, status_cnt, update_dt)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (name, phone, address, lat, lng, type, capacity, status_cnt, update_dt))
    conn.commit()

## 로그 등록
def create_transport_log(hospital_id, patient_id, start_datetime, end_datetime, status):
    # transport_logs에 로그 추가
    cursor.execute('''
        INSERT INTO transport_logs (hospital_id, patient_id, start_datetime, end_datetime, status)
        VALUES (?, ?, ?, ?, ?)
    ''', (hospital_id, patient_id, start_datetime, end_datetime, status))

    # 만약 status가 2라면, hospitals 테이블에서 해당 hospital_id의 status_cnt를 증가시킴
    if status == 2:
        current_time = datetime.now().isoformat()
        cursor.execute('''
        UPDATE hospitals
        SET status_cnt = status_cnt + 1,
            update_dt = ?
        WHERE hospital_id = ?
        ''', (current_time, hospital_id))

    conn.commit()


## Read - 데이터 조회
def read_hospitals():
    cursor.execute("SELECT * FROM hospitals")
    return cursor.fetchall()

def read_transport_logs():
    cursor.execute("SELECT * FROM transport_logs")
    return cursor.fetchall()

## Update - 데이터 업데이트
## 1. 환자 이송 시작시, 이송중 3으로 업데이트
def update_transport_log_start(hospital_id, patient_id):
    start_datetime = datetime.now().isoformat()
    cursor.execute('''
    UPDATE transport_logs
    SET status = 3,
        start_datetime = ?
    WHERE hospital_id = ? AND patient_id = ?
    ''', (start_datetime, hospital_id, patient_id))
    conn.commit()

## 2. 환자 이송 완료시, 성공 1으로 업데이트
def update_transport_log_end(hospital_id, patient_id):
    end_datetime = datetime.now().isoformat()
    cursor.execute('''
    UPDATE transport_logs
    SET status = 1,
        end_datetime = ?
    WHERE hospital_id = ? AND patient_id = ?
    ''', (end_datetime, hospital_id, patient_id))
    conn.commit()


## 3. 환자 이송 거절시, 거절 2로 업데이트
def update_transport_log_deny(hospital_id, patient_id):
    cursor.execute('''
    UPDATE transport_logs
    SET status = 2
    WHERE hospital_id = ? AND patient_id = ?
    ''', (hospital_id, patient_id))

    current_time = datetime.now().isoformat()
    cursor.execute('''
    UPDATE hospitals
    SET status_cnt = status_cnt + 1,
        update_dt = ?
    WHERE hospital_id = ?
    ''', (current_time, hospital_id))
    conn.commit()

# def update_hospital(hospital_id, name=None, capacity=None, status_cnt=None):
#     fields = []
#     values = []
#     if name:
#         fields.append("hospital_name = ?")
#         values.append(name)
#     if capacity:
#         fields.append("capacity = ?")
#         values.append(capacity)
#     if status_cnt:
#         fields.append("status_cnt = ?")
#         values.append(status_cnt)
#     values.append(hospital_id)
#     cursor.execute(f"UPDATE hospitals SET {', '.join(fields)} WHERE hospital_id = ?", values)
#     conn.commit()


## Delete - 데이터 삭제
def delete_hospital(hospital_id):
    cursor.execute("DELETE FROM hospitals WHERE hospital_id = ?", (hospital_id,))
    conn.commit()

def delete_transport_log(log_id):
    cursor.execute("DELETE FROM transport_logs WHERE log_id = ?", (log_id,))
    conn.commit()

# 예제 실행
create_hospital(
    name="서울중앙병원",
    phone="02-1234-5678",
    address="서울특별시 중구 세종대로 110",
    lat=37.5665,
    lng=126.9780,
    type=1,  # 예: 1차 병원
    capacity=100,
    status_cnt=0
)

# 환자 ID 101번 환자가 서울중앙병원에 호출된 로그 추가
create_transport_log(
    hospital_id=1,            # 서울중앙병원 ID
    patient_id=101,           # 환자 ID
    start_datetime='',
    end_datetime='',
    status=0                  # 상태 0 (요청)
)

# 이송 시작 상태로 변경
update_transport_log_start(hospital_id=1, patient_id=101)

# 이송 완료 상태로 변경
update_transport_log_end(hospital_id=1, patient_id=101)

# 조회 결과 확인
hospitals_data = read_hospitals()
transport_logs_data = read_transport_logs()

print(11,hospitals_data)
print(22,transport_logs_data)



# 데이터베이스 연결 종료
conn.close()
