
# SQL 수행구조 및 I/O 분석

## 1. SQL 수행구조
### 실행 계획 ⇒ 예상 정보
- **[보완]** 옵티마이저 결정(Access Path / Join Order / Join Method)·Cardinality·Cost 확인.  
  Estimated Rows와 Actual Rows의 괴리는 **통계·히스토그램·바인드 스니핑** 점검 포인트.

### 실제 처리 건수 ⇒ 트레이스 정보
- **[보완]** SQL Trace / TKPROF / ASH로 실제 Rows·Fetch 횟수·대기 이벤트 비교.  
  “예상 vs 실제” 차이가 크면 **통계 보정·SQL 재작성·플랜 고정(SQL Plan Baseline)** 검토.

---

## 2. I/O 기본 단위
- 오라클: **Block**
- SQL Server: **Page(기본 8KB)**
- **[보완]** 논리 I/O(버퍼캐시)와 물리 I/O(디스크)를 구분.

---

## 3. 옵티마이저
- **규칙 기반 옵티마이저(RBO)**: Single row by ROWID 액세스
- **비용 기반 옵티마이저(CBO)**: 통계정보 기반 SQL 실행 계획 결정
- **JOIN 기본**: NL, HASH, SORT MERGE
- **[보완]** RBO는 역사적 참고. CBO는 테이블·인덱스 통계(NDV, 히스토그램) 기반.  
  조인 선택은 **데이터량·분포·메모리·I/O 패턴(Random/Sequential)**에 좌우.

---

## 4. I/O 효율화 원리
- 중복 액세스 제거
- 정확한 통계정보 유지
- 힌트를 통한 최적 액세스 경로 유도
- **[보완]** 필터 조건을 **드라이빙 집합**에서 최대한 적용, 불필요 Full Scan 억제,  
  멀티블록 리드 활용으로 순차 I/O 비중 확대.

---

## 5. Connection 관리
- **Connection Pooling** 필수
- Connection 요청 부하: **Thread < Process**
- **전용 서버 방식**: 요청마다 서버 프로세스 생성
- **공유 서버 방식**: Dispatcher 프로세스 경유
- **[보완]** 대규모 동시접속 시 **공유 서버 + 풀링 조합**,  
  세션/커서 캐시 파라미터 조정으로 하드파싱 억제.

---

## 6. DB 저장 구조
- 데이터 읽기·쓰기 단위: **블록 / 페이지**
- 데이터 파일 공간 할당 단위: **익스텐트(Extent)**
- 익스텐트는 물리적으로 인접할 필요 없음
- SQL Server: 페이지 단위, 여러 오브젝트 공유 가능
- **[보완]** 세그먼트(테이블·인덱스)는 다수 익스텐트로 구성,  
  Extent 크기·배치가 Full Scan I/O Call 수에 영향.

---

## 7. Write Ahead Logging
- **Dirty Buffer**를 디스크 기록 전, 로그(Redo)에 선기록
- **[보완]** Redo 선기록 후 DBWR가 데이터파일 반영.  
  커밋 시 `log file sync` 대기 발생 가능.

---

## 8. 메모리 구조
- **DB 버퍼 캐시**: 데이터 블록 캐시
- `/*+ APPEND */`: Direct Path Write
- **클러스터링 팩터**가 높을수록 Buffer Pinning 효과
- **[보완]** APPEND는 Direct Path Write로 버퍼캐시 우회(HWM 뒤로 적재).  
  PGA는 Sort/Hash 영역. CF가 나쁘면 인덱스 Range Scan 시 랜덤 접근 증가.

---

## 9. I/O 튜닝 핵심 원리
- **Sequential Access 비율 ↑**
- **Random Access 비율 ↓**
- **[보완]** 인덱스 설계, 파티셔닝, 프루닝, 멀티블록 리드 최적화로 달성.

---

## 10. 데이터베이스 I/O
- 테이블 블록 스캔 ⇒ Random I/O
- 인덱스 블록 스캔 ⇒ Sequential I/O
- MultiBlock I/O ⇒ Extent 내 블록 일괄 읽기
- Single/MultiBlock I/O ⇒ 테이블 크기 무관
- Index Unique Scan ⇒ Row 단위 I/O
- **[보완]** Multiblock Read Count 조정, Direct Path Read(병렬/대용량) 시 캐시 우회.

---

## 11. 버퍼캐시 히트율
- 공식:  
  ((논리 읽기 - 물리 읽기) / 논리 읽기) × 100
- **[보완]** 히트율 단독 판단은 한계. **대기 이벤트, 응답시간**과 함께 분석.

---

## 12. AWR Report
- **db file sequential read** ⇒ 인덱스 생성/사용 이벤트, 부하 낮음
- **log file sync** ⇒ Online Redo log file 개수 많음
- **[보완]** Top SQL, Top Events, Instance Efficiency, Segments by I/O, ASH 병행 점검.  
  Redo 로그 크기·배치·저장소 성능도 확인.

---

## 13. 통계정보 수집
- 변경 거의 없으면 매일 수집 불필요
- **[보완]** Skew가 크면 히스토그램 생성. 파티션 통계, 증분 통계 고려.

---

## 14. 블록 I/O
- Random I/O ⇒ Table Access by ROWID
- Direct Path I/O ⇒ 병렬 쿼리 Full Scan
- 인덱스 ⇒ 테이블 액세스 ⇒ Single Block I/O
- 테이블 Full Scan ⇒ Multi Block I/O
- **[보완]** Direct Path는 Temp/Redo 영향과 병행 고려.

---

## 15. DB I/O 상세
- 동일 블록 반복 액세스 ⇒ 버퍼 캐시 히트율 ↑
- Multi Block I/O ⇒ I/O Call 시 여러 블록 적재
- 작은 Extent Full Scan ⇒ I/O Call 횟수 ↑
- 하나의 레코드 ⇒ 해당 블록 전체 읽음
- Sequential I/O ⇒ 테이블 또는 인덱스 스캔
- Random I/O ⇒ 인덱스 + 테이블 스캔 병행
- **[보완]** Extent 관리(Uniform/Large)로 Full Scan 효율 개선.

---

## 16. SQL 분석도구
- **Response Time = CPU Time + Wait Time**

### SQL Server
set showplan_text on;
set statistics profile on;
set statistics io on;
set statistics time on;

### Oracle
set autotrace on explain;
set autotrace on statistics;
set autotrace on trace only;
alter session set sql_trace = true;

### TKPROF
- SQL 수행시간, 블록 읽기, Parse/Execute/Fetch 횟수 확인

### 주의사항
- DDL 수행 시: library cache lock, library cache pin 발생 가능
- **[보완]** ASH 리포트로 특정 시간대 병목 파악.  
  DDL은 공유 풀 오브젝트 재컴파일·Invalidation 유발 가능.
