# 📖 [T05] 서브쿼리 튜닝 & 뷰 머징(NO_MERGE) 쿼리 변환 마스터 보강노트

- **테마:** `T05 Scalar Subquery / Query Transformation`
- **기준 마스터 문서:** `AGENTS.md`, `SQLP_실기_2회독_통합패턴맵_v2_3_최종확정.md`
- **문서 목적:** 실전 시험 직전 서브쿼리(`UNNEST`, `PUSH_SUBQ`), 스칼라 변환, 뷰 머징(`NO_MERGE`) 관련 문제를 1초 만에 풀어내기 위한 핵심 체크노트

---

# 🚨 [실전 직전 3분] 서브쿼리 & 뷰 머징 5대 함정 탈출 체크리스트

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ ⚠️ [함정 1] NO_UNNEST와 NL_SJ를 한 서브쿼리에 동시에 쓰는 실수                        │
│ 👉 탈출법: 풀어서 조인할 때는 /*+ UNNEST NL_SJ */, 필터로 남길 때는 /*+ NO_UNNEST */!  │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ ⚠️ [함정 2] 여러 테이블 조인 시 서브쿼리 필터를 뒤늦게 실행해 헛조인 폭발시키는 실수 │
│ 👉 탈출법: 조인 중간에 서브쿼리 필터를 먼저 실행시키려면 /*+ NO_UNNEST PUSH_SUBQ */!  │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ ⚠️ [함정 3] 스칼라 서브쿼리를 'INNER JOIN'으로 바꿔 매칭 안 되는 데이터를 날리는 실수 │
│ 👉 탈출법: 스칼라 서브쿼리는 NULL을 반환하는 특성이 있으므로 무조건 [LEFT OUTER JOIN]! │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ ⚠️ [함정 4] 1개 테이블 집계를 위해 스칼라 서브쿼리나 인라인 뷰를 2개로 쪼개는 실수   │
│ 👉 탈출법: [CASE WHEN]을 사용하여 1개의 인라인 뷰에서 SUM과 COUNT를 동시에 1회 집계!  │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ ⚠️ [함정 5] COUNT(CASE WHEN ... ELSE 0 END)로 적어 전체 행 수가 나와버리는 실수     │
│ 👉 탈출법: COUNT는 0도 1건으로 셉니다! COUNT 쓸 땐 ELSE 생략, ELSE 0 쓸 땐 SUM 사용! │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

# 🛡️ 1. 서브쿼리 제어 3대 힌트 세트 공식

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ 1. 서브쿼리를 조인(Semi-Join)으로 풀어서 처리할 때:                                         │
│    👉 메인 힌트: /*+ LEADING(메인 서브Q 타1 타2) USE_NL(서브Q) NL_SJ(서브Q) */               │
│    👉 서브Q 힌트: /*+ UNNEST */ (또는 서브Q 내 /*+ UNNEST NL_SJ */)                       │
│                                                                                        │
│ 2. 서브쿼리를 절대 풀지 않고 메인 쿼리 뒤에서 FILTER로 남길 때:                              │
│    👉 서브Q 힌트: /*+ NO_UNNEST */                                                      │
│                                                                                        │
│ 3. 조인이 많은 쿼리에서 서브쿼리 FILTER를 조인 중간(첫 테이블 직후)에 먼저 적용하고 싶을 때:  │
│    👉 서브Q 힌트: /*+ NO_UNNEST PUSH_SUBQ */                                           │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

# 📊 2. 스칼라 서브쿼리 ➡️ `LEFT OUTER JOIN` + `CASE WHEN 1회 집계` 변환 공식

### 💡 3대 변환 원칙
1. **스칼라의 본질은 `LEFT OUTER JOIN`:**
   - 상대 테이블에 매칭 데이터가 없어도 메인 집합이 탈락하지 않도록 반드시 **`LEFT OUTER JOIN`**을 사용한다.
2. **`CASE WHEN` 1회 집계 (중복 스캔 100% 제거):**
   - 동일 테이블에 대해 정상금액(`SUM`)과 반품/실패건수(`COUNT`)를 각각 쪼개지 말고, **단 1개의 인라인 뷰에서 `CASE WHEN`으로 동시에 집계**한다.
   - **금액 합계:** `SUM(CASE WHEN 조건 THEN 금액컬럼 END)`
   - **건수 카운트:** `COUNT(CASE WHEN 조건 THEN 1 END)` 또는 `SUM(CASE WHEN 조건 THEN 1 ELSE 0 END)`
3. **대량 결합은 무조건 `USE_HASH`:**
   - `GROUP BY`가 완료된 인라인 뷰(`V`) 메모리 집합에는 **B-Tree 인덱스가 없으므로** 대량 조인 시 `USE_NL`을 쓰면 부하가 터진다. 무조건 **`USE_HASH(V)`**를 지정한다.

---

# 🏛️ 3. 뷰 머징(View Merging) & `NO_MERGE` 총망라 가이드

### (1) [오라클 공식 규정] 뷰 머징 원천 불가 8대 제약사항 (Non-Mergeable Views)
아래 항목이 인라인 뷰 내에 포함되어 있으면, 힌트와 무관하게 **오라클이 알아서 머징을 포기하고 독립적인 `VIEW` 오퍼레이션으로 실행**합니다:

| 번호 | 제약 요소 | 상세 설명 및 예시 |
|:---:|---|---|
| **1** | **`ROWNUM` 의사컬럼** | `WHERE ROWNUM <= 10` 등 Top-N 페이징 처리가 들어간 뷰 |
| **2** | **집합 연산자 (Set Operators)** | `UNION`, `UNION ALL`, `INTERSECT`, `MINUS`가 사용된 뷰 |
| **3** | **계층형 쿼리 (Hierarchical Query)** | `START WITH`, `CONNECT BY` 절이 포함된 계층형 뷰 |
| **4** | **`GROUP BY` 없는 집계 함수** | `SELECT SUM(AMT), AVG(QTY) FROM ...` 처럼 전체 단 1행만 반환하는 스칼라 집계 뷰 |
| **5** | **분석/윈도우 함수 (Analytic Functions)** | `ROW_NUMBER()`, `RANK()`, `SUM() OVER (...)` 등이 포함된 뷰 |
| **6** | **`MODEL` 절** | 오라클 다차원 모델링 `MODEL` 구문이 사용된 뷰 |
| **7** | **시퀀스 및 비결정적 함수** | 뷰의 SELECT 목록에 `SEQ.NEXTVAL` 또는 비결정적 함수 포함 시 |
| **8** | **XMLTable / Flashback 절** | `XMLTABLE(...)` 구문 또는 `AS OF TIMESTAMP/SCN` 과거 시점 조회가 포함된 뷰 |

### (2) [튜너의 무기] 튜너가 직접 `/*+ NO_MERGE */`를 거는 5대 실무 목적
1. **[선집계 강제]** `GROUP BY`로 수천만 건을 수만 건으로 먼저 축소한 뒤 메인과 결합할 때 (Complex View Merging 방지).
2. **[선중복제거]** `DISTINCT`로 대량 집합의 중복을 먼저 깎아낸 뒤 조인할 때.
3. **[조인순서 통제]** 5~6개 복잡한 테이블 조인 시 인라인 뷰를 '독립 블록'으로 묶어 `LEADING` 순서를 통제할 때.
4. **[조인증폭 방지]** 1:N:M 관계에서 중간 카디널리티 폭발(데카르트곱)을 막고 싶을 때.
5. **[함수호출 지연]** 무거운 PL/SQL 사용자 정의 함수 호출을 최종 10건 필터링 뒤로 미루어 호출 횟수를 극소화할 때.

---

# 💬 4. 실전 질의응답(Q&A) 마스터 카드

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ 💬 Q1. PUSH_SUBQ는 언제 쓰나요?                                                         │
│ 👉 A1. 메인 FROM 절에 여러 테이블 조인이 엮여 있을 때, 서브쿼리 필터를 조인 맨 마지막이     │
│        아닌 [조인 중간(첫 테이블 직후)]으로 밀어 넣어 뒤따르는 후행 조인 Starts를 급감시킴!   │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 💬 Q2. 왜 GROUP BY 인라인 뷰(V)와의 대량 조인은 무조건 USE_HASH인가요?                 │
│ 👉 A2. 집계가 완료된 인라인 뷰 메모리 집합에는 [인덱스가 없기 때문]에 NL 조인을 돌리면         │
│        엄청난 부하가 터집니다. 메모리 해시 맵으로 1:1 매칭하는 HASH JOIN이 최적입니다.          │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 💬 Q3. 옵티마이저가 스칼라 서브쿼리를 알아서 UNNEST 해주지 않나요?                      │
│ 👉 A3. 옵티마이저는 테이블 1개를 2번 쪼갠 서브쿼리를 [CASE WHEN 1회 집계]로 합치지 못하며,│
│        집계가 복잡하면 UNNEST를 포기하거나 NL Outer Join을 타는 등 엉뚱한 결정을 내립니다.    │
│        따라서 튜너가 직접 [LEFT OUTER JOIN + CASE WHEN + USE_HASH]로 통제해야 합니다!         │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 💬 Q4. 인라인 뷰가 풀리지 않게 하려면 힌트를 어떻게 써야 하나요?                       │
│ 👉 A4. FROM 절 인라인 뷰는 독립 뷰이므로 NO_UNNEST가 아닌 [/*+ NO_MERGE */]를 인라인 뷰 내부에│
│        선언하여 완벽한 독립 선집계를 보장합니다!                                       │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 💬 Q5. UNNEST 시 LEADING 힌트에 서브쿼리 테이블을 꼭 2순위로 넣어야 하나요?             │
│ 👉 A5. 네! LEADING에 서브쿼리 테이블(E)을 빼먹으면 옵티마이저가 E를 맨 마지막 4등으로 밀어버려│
│        선행 헛조인 병목이 재발합니다. 반드시 /*+ LEADING(메인 서브Q 타1 타2) */로 강제합니다!  │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 💬 Q6. 조인 연결고리가 없는 부모 테이블끼리 먼저 조인하고 PUSH_SUBQ를 할 수 있나요?      │
│ 👉 A6. 절대 불가! 조인 조건이 없는 독립 부모끼리 조인하면 [카디시안 곱]이 발생하며,          │
│        서브쿼리는 상관 키(계좌번호 등)를 공급해주는 메인 테이블이 먼저 읽혀야만 실행됩니다!     │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 💬 Q7. COUNT(CASE WHEN ... ELSE 0 END)는 왜 치명적인 오류인가요?                        │
│ 👉 A7. COUNT는 [Non-NULL 모든 값]을 세므로, 숫자 0도 1건으로 셉니다! (전체 행 수가 나옴)   │
│        • COUNT 사용 시 ➡️ 반드시 ELSE 생략: COUNT(CASE WHEN 조건 THEN 1 END)           │
│        • ELSE 0 사용 시 ➡️ 반드시 SUM 사용: SUM(CASE WHEN 조건 THEN 1 ELSE 0 END)       │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

# 📝 5. 시험 직전 실전 자가 테스트 문제 & 만점 정답 세트

---

### 📋 [실전 문제 1] 스칼라 서브쿼리 ➡️ `LEFT OUTER JOIN` + `CASE WHEN 1회 집계` + `USE_HASH`

* **상황:** 배송기사 15,000명(`TB_DRIVER`)에 대해 프로필(`TB_DRIVER_PROFILE`)과 1,500만 건 배송이력(`TB_DELIVERY_LOG`)의 완료금액(`SUM`)과 실패건수(`COUNT`)를 각각 스칼라로 조회하여 45,000회 I/O 폭발.

#### 💯 [만점 정답 SQL]
```sql
SELECT /*+ LEADING(D P V) USE_NL(P) USE_HASH(V)
           INDEX(D IX_DRIVER_01) INDEX(P PK_TB_DRIVER_PROFILE) */
       D.DRIVER_ID,
       D.DRIVER_NM,
       P.CAR_TYPE_CD,
       NVL(V.DONE_FEE_AMT, 0) AS DONE_FEE_AMT,
       NVL(V.FAIL_CNT, 0)     AS FAIL_CNT
  FROM TB_DRIVER D
  LEFT OUTER JOIN TB_DRIVER_PROFILE P 
    ON P.DRIVER_ID = D.DRIVER_ID
  LEFT OUTER JOIN (
       SELECT /*+ NO_MERGE INDEX(L IX_DELIV_01) */
              L.DRIVER_ID,
              SUM(CASE WHEN L.DELIV_STAT_CD = 'DONE' THEN L.DELIV_FEE ELSE 0 END) AS DONE_FEE_AMT,
              COUNT(CASE WHEN L.DELIV_STAT_CD = 'FAIL' THEN 1 END)                AS FAIL_CNT
         FROM TB_DELIVERY_LOG L
        WHERE L.DELIV_DT >= '20260101'
        GROUP BY L.DRIVER_ID
  ) V
    ON V.DRIVER_ID = D.DRIVER_ID
 WHERE D.AREA_CD = 'SEOUL'
   AND D.JOIN_DT >= '20260101';
```

---

### 📋 [실전 문제 2] 서브쿼리 조기 필터링 (`PUSH_SUBQ` vs `UNNEST NL_SJ`)

* **상황:** 당일 예약자 10,000건(`TB_RESERV`)에 대해 진료과(`TB_DEPT`)와 의사(`TB_DOCTOR`)를 20,000회 헛조인한 뒤, 맨 마지막에 당일 중증 응급로그(`TB_EMERGENCY_LOG`, 단 20건)로 거르는 비효율 해소.

#### 💯 [방식 1: PUSH_SUBQ 정답 (서브쿼리 안에 힌트 추가)]
```sql
SELECT R.RESV_NO, R.PATIENT_ID, D.DEPT_NM, DOC.DOC_NM
  FROM TB_RESERV R, TB_DEPT D, TB_DOCTOR DOC
 WHERE R.DEPT_CD = D.DEPT_CD AND R.DOC_ID = DOC.DOC_ID
   AND R.RESV_STAT_CD = '01' AND R.RESV_DT = '20260817'
   AND EXISTS (
       SELECT /*+ NO_UNNEST PUSH_SUBQ INDEX(E IX_EMRG_01) */ 1
         FROM TB_EMERGENCY_LOG E
        WHERE E.PATIENT_ID = R.PATIENT_ID
          AND E.EMRG_LEVEL = 'L1'
          AND E.LOG_DT >= '20260817'
   );
```

#### 💯 [방식 2: UNNEST NL_SJ 정답 (메인 LEADING 2순위에 E 배치)]
```sql
SELECT /*+ LEADING(R E D DOC) USE_NL(E) NL_SJ(E) USE_NL(D) USE_NL(DOC)
           INDEX(R IX_RESV_01) INDEX(E IX_EMRG_01) 
           INDEX(D PK_TB_DEPT) INDEX(DOC PK_TB_DOCTOR) */
       R.RESV_NO, R.PATIENT_ID, D.DEPT_NM, DOC.DOC_NM
  FROM TB_RESERV R, TB_DEPT D, TB_DOCTOR DOC
 WHERE R.DEPT_CD = D.DEPT_CD AND R.DOC_ID = DOC.DOC_ID
   AND R.RESV_STAT_CD = '01' AND R.RESV_DT = '20260817'
   AND EXISTS (
       SELECT /*+ UNNEST */ 1
         FROM TB_EMERGENCY_LOG E
        WHERE E.PATIENT_ID = R.PATIENT_ID
          AND E.EMRG_LEVEL = 'L1'
          AND E.LOG_DT >= '20260817'
   );
```
