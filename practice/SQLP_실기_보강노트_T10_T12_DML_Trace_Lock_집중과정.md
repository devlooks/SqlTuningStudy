# SQLP 실기 보강노트: T10~T12 3단계(초·중·고) 집중 마스터 가이드

- **적용 대상:** T10 (DML/Batch/DDL), T11 (Runtime/Trace/DB Call), T12 (Lock/Transaction/Concurrency)
- **운영 기간:** 2026-08-28(금) ~ 2026-08-30(일) (3일간 집중 진행)
- **과정 목적:** 생소하고 난이도가 높은 테마별 **필수 물리적 개념 완벽 숙지** 및 **실전 튜닝 숙달(Mastery)** 달성
- **운영 규칙:** 초·중·고 3단계 레벨화는 **T10~T12 테마에 한정하여 유효**하게 적용함

---

## 📅 1. 3일간 진행 일정 및 테마 배정

| 일자 | 대상 테마 | 단계별 구성 (초 ➡️ 중 ➡️ 고) | 핵심 정복 목표 |
|:---:|---|---|---|
| **08/28 (금)** | **T10. DML / Batch / DDL** | • **[초급]** 대량 DELETE의 한계 & CTAS 5단계 재구성<br>• **[중급]** 파티션 교체(EXCHANGE) & 사전 인덱스<br>• **[고급]** Direct-Path + UNUSABLE & 대량 MERGE | 대량 데이터 삭제/적재/갱신 시 Undo/Redo/인덱스 부하를 제거하는 구조적 해법 마스터 |
| **08/29 (토)** | **T11. Runtime / Trace / DB Call** | • **[초급]** Parse/Execute/Fetch 메커니즘 & Array Fetch<br>• **[중급]** TKPROF 지표 분석 & Row-by-Row ➡️ Set MERGE<br>• **[고급]** 과도한 Logical I/O & Database Call 복합 튜닝 | SQL 수행 단계별 통계 분석 및 건별 루프를 단일 원샷 집합 처리로 전환하는 능력 확립 |
| **08/30 (일)** | **T12. Lock / Transaction / 동시성** | • **[초급]** TX Row Lock vs TM Table Lock (외래키 인덱스)<br>• **[중급]** Blocker 추적, Commit 주기, SELECT FOR UPDATE<br>• **[고급]** 동시 DML 경합 해소 & 트랜잭션 분할 설계 | 락 대기 및 동시성 저하 원인을 식별하고 고성능 트랜잭션 구조로 재설계하는 역량 완성 |

---

## 📦 2. [T10] DML / Batch / DDL 핵심 개념 및 단계별 가이드

### 📌 [초급] 대량 DELETE 한계 & CTAS 5단계 표준 절차
1. **대량 DELETE의 3대 물리적 병목:**
   - **Undo/Redo 폭증:** 지워지는 모든 행의 전후 데이터를 Undo 세그먼트와 Redo 로그에 기록하므로 I/O 및 공간 고갈 발생.
   - **인덱스 유지 비용:** 테이블의 행 삭제 시 해당 테이블에 걸린 모든 인덱스 Leaf 노드에서 건건이 삭제 마킹(Delete Flag)을 수행하여 엄청난 Random I/O 유발.
   - **HWM(High Water Mark) 유지:** DELETE는 공간을 반환하지 않으므로 테이블 세그먼트의 HWM이 그대로 유지되어 이후 Full Scan 성능 영구 저하.
2. **CTAS 5단계 표준 DDL 절차:**
   - **Step 1:** 보존할 데이터(예: 5%)만 추출하여 NOLOGGING + PARALLEL로 임시 테이블 생성 (CREATE TABLE ... AS SELECT ...)
   - **Step 2:** 신규 임시 테이블에 PK 제약조건 및 필수 인덱스 일괄 생성 (NOLOGGING + PARALLEL)
   - **Step 3:** 원본 테이블 백업 또는 즉시 삭제 (DROP TABLE TB_ORIGIN PURGE;)
   - **Step 4:** 임시 테이블을 원본 테이블명으로 변경 (RENAME TB_TEMP TO TB_ORIGIN;)
   - **Step 5:** 테이블 및 인덱스를 LOGGING 및 NOPARALLEL로 정상화 복구

### 📌 [중급] EXCHANGE PARTITION & 스테이징 사전 인덱스
- **원리:** 데이터 복사 없이 딕셔너리의 세그먼트 메타데이터 포인터만 맞바꾸는 최고속 교체 기법.
- **핵심 급소 (사전 인덱스):** INCLUDING INDEXES 옵션 사용 시, 파티션 테이블에 로컬 인덱스가 존재한다면 **임시(스테이징) 테이블에도 동일한 컬럼 순서의 일반 인덱스가 사전에 생성되어 있어야만** 파티션 교체 후 로컬 인덱스가 UNUSABLE로 깨지지 않고 유지됨.

### 📌 [고급] 대량 INSERT(UNUSABLE) & 대량 UPDATE(MERGE)
- **Direct-Path INSERT:** 인덱스를 UNUSABLE 처리 ➡️ INSERT /*+ APPEND PARALLEL */ ➡️ ALTER INDEX ... REBUILD PARALLEL 순으로 대량 적재.
- **대량 UPDATE:** 상관 서브쿼리 UPDATE 80만 회 반복 ➡️ MERGE INTO ... USING (선집계 뷰) ... ON (...) + USE_HASH로 단 1회 조인 갱신.

---

## ⚡ 3. [T11] Runtime / Trace / DB Call 핵심 개념 및 단계별 가이드

### 📌 [초급] Parse/Execute/Fetch & Array Processing
1. **SQL 수행 3단계:**
   - **Parse:** 문법 검사, 의미 분석, 권한 확인, Shared Pool 캐싱 확인 및 최적화 실행계획 생성.
   - **Execute:** 커서 오픈, 바인드 변수 바인딩, 데이터 추출 준비 (SELECT는 실행계획 셋업, DML은 실제 데이터 변경).
   - **Fetch:** SELECT 쿼리에서 실제 결과 로우(Row)를 서버 버퍼캐시에서 읽어 애플리케이션으로 전송.
2. **Fetch Count 산출 공식:**
   \text{Fetch Count} = \text{TRUNC}\left(\frac{\text{총 반환 행수}}{\text{Array Size}}\right) + 1
   *(※ 정확히 나누어떨어져도 마지막에 더 이상 읽을 데이터가 없음을 확인하는 EOF Fetch Call 1회가 반드시 추가됨)*
3. **Array Size 설정의 Trade-off:**
   - Array Size를 키우면 Network Round-Trip(DB Call) 및 Block Pinning I/O가 대폭 감소하지만, 클라이언트/서버 메모리(PGA) 사용량이 증가하므로 통상 100~500 수준이 최적.

### 📌 [중급] TKPROF 지표 분석 & Row-by-Row ➡️ Set MERGE
- **Consistent Gets (query) vs DB Block Gets (current):**
  - query: SELECT 조회 시 CR 블록을 읽을 때 발생.
  - current: INSERT/UPDATE/DELETE 시 최신 블록을 직접 읽고 변경할 때 발생.
- **Set Processing 전환:**
  - 루프 내 건건이 SELECT ➡️ UPDATE / INSERT 분기 ➡️ 단일 MERGE INTO ... USING (선집계 뷰) ON (...) WHEN MATCHED ... WHEN NOT MATCHED ... 구문으로 통합하여 Call 횟수를 수만 회에서 **단 1회**로 축소.

---

## 🔒 4. [T12] Lock / Transaction / Concurrency 핵심 개념 및 단계별 가이드

### 📌 [초급] TX Row Lock vs TM Table Lock
- **TX Lock (Row-Level):** 동일한 행을 서로 다른 두 세션이 동시에 UPDATE/DELETE하려 할 때 발생 (배타적 락).
- **TM Lock (Table-Level):** 자식 테이블의 **외래키(FK) 컬럼에 인덱스가 없는 상태**에서 부모 테이블의 행을 삭제/수정할 때, 자식 테이블 전체에 Share Lock (TM)이 걸려 자식 테이블의 모든 DML이 전면 블로킹됨.

### 📌 [중급] Blocker 추적 & Commit 주기 및 SELECT FOR UPDATE
- **Blocker 식별:** 대기 중인 Waiter 세션만 볼 것이 아니라, 락을 쥐고 있는 Blocker 세션의 트랜잭션 시작 시점과 SQL을 찾아야 함.
- **Commit 주기:** 루프 건건이 Commit은 Redo Log Sync I/O 폭증과 Snapshot Too Old (ORA-01555)를 유발하고, 너무 늦은 Commit은 락 유지시간을 증가시키므로 적정 배치 단위(예: 5,000~10,000건) 분할 커밋이 원칙.
- **동시성 제어:** SELECT ... FOR UPDATE NOWAIT 또는 SKIP LOCKED를 활용한 큐잉 시스템 튜닝.

---

## 🎯 5. 합격을 위한 실전 체크리스트 (T10~T12 공통)

1. DML 문법에서 **MERGE의 USING 절에 반드시 필요한 집계/선필터 인라인 뷰가 올바른 Alias와 힌트**를 갖추었는가?
2. EXCHANGE PARTITION 작성 시 **INCLUDING INDEXES와 스테이징 테이블 사전 인덱스**를 누락하지 않았는가?
3. TKPROF 표에서 **query(Consistent)와 current(DB block) 수치를 구분**하여 I/O 원인을 진단하였는가?
4. 건별 반복 루프의 폐해를 **Database Call 수치와 Context Switching** 관점에서 명확히 지적하였는가?
