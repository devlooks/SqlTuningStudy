# 📖 [T06] 선택적 검색조건 & OR Expansion 쿼리 변환 마스터 보강노트

- **테마:** `T06 Optional Predicate / OR Expansion`
- **기준 마스터 문서:** `AGENTS.md`, `SQLP_실기_2회독_통합패턴맵_v2_3_최종확정.md`
- **문서 목적:** 실전 시험 직전 동적 조건(`NVL/DECODE`, `UNION ALL`), OR 조건 인덱스 분기(`USE_CONCAT`, `LNNVL`), IN-List Top-N 스톱키 관련 문제를 1초 만에 풀어내기 위한 핵심 체크노트

---

# 🚨 [실전 직전 3분] 동적조건 & OR Expansion 5대 함정 탈출 체크리스트

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ ⚠️ [함정 1] WHERE (:b IS NULL OR COL = :b) 작성 후 단일 인덱스 스캔을 기대하는 실수     │
│ 👉 탈출법: OR 조건은 단일 LIO로 인덱스를 못 탑니다! [UNION ALL]로 분기하거나 동적 SQL! │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ ⚠️ [함정 2] OR 조건 ➡️ UNION ALL 분기 시 중복 데이터(Double Counting)를 방치하는 실수  │
│ 👉 탈출법: 후행 브랜치에 [LNNVL(선행조건)]을 반드시 추가하여 상호배타성을 100% 확보!    │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ ⚠️ [함정 3] 다중 NVL 검색조건(고객/부서/전체)을 1개의 쿼리로 뭉개서 FTS를 유발하는 실수│
│ 👉 탈출법: 입력 우선순위(고객 50% ➜ 부서 40% ➜ 전체 10%)에 따라 3단계 UNION ALL 분기!  │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ ⚠️ [함정 4] IN-List + Top-N 조회 시 바깥에만 ROWNUM <= 10을 걸어 전체 정렬시키는 실수  │
│ 👉 탈출법: INLIST ITERATOR는 정렬 생략 불가! 브랜치별 [사전 ROWNUM <= 10 + INDEX_DESC]!│
├────────────────────────────────────────────────────────────────────────────────────────┤
│ ⚠️ [함정 5] USE_CONCAT 힌트만 믿고 인덱스 컬럼 구성과 NULL 허용 여부를 검증 안 하는 실수 │
│ 👉 탈출법: 옵티마이저가 비용 기반으로 거부할 수 있으므로, 확실한 UNION ALL 재작성이 정답! │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

# 🛡️ 1. 선택적 검색조건 4대 패턴과 최적 해법

| 패턴 유형 | AS-IS 구현 형태 | 문제점 | 최적 TO-BE 해법 |
|---|---|---|---|
| **1. 단일 컬럼 NVL** | `WHERE COL = NVL(:b, COL)` | NULL 입력 시 `COL IS NOT NULL`로 변환되어 인덱스 스캔 불가 또는 FTS 발생 | `UNION ALL` 분기 (`:b IS NOT NULL` vs `:b IS NULL`) 또는 `OR Expansion` |
| **2. 다중 컬럼 NVL** | `WHERE CUST_ID = NVL(:c, CUST_ID) AND DEPT_NO = NVL(:d, DEPT_NO)` | 하나의 실행계획으로 다양한 입력 패턴(고객만, 부서만, 둘다)을 만족할 수 없어 비효율 발생 | 입력 조합의 선택도/빈도에 따라 **우선순위 기반 `UNION ALL` 배타적 분기** |
| **3. 컬럼 간 OR 조건** | `WHERE (A_CD = :a OR B_CD = :b)` | 단일 인덱스로 양쪽 컬럼을 동시에 Range Scan 불가 ➜ FTS 유도됨 | **`UNION ALL` + `LNNVL` 함수**를 통한 중복 제거 분기 |
| **4. IN-List + Top-N** | `WHERE STAT_CD IN ('A', 'B') ORDER BY REG_DT DESC (ROWNUM <= 10)` | 각 인-리스트 브랜치 내부에서 정렬되므로 최종 결과 정렬 생략 불가 (`SORT ORDER BY`) | **각 조건별 `ROWNUM <= 10` 인라인 뷰 사전 추출** 후 최종 결합 Top-10 |

---

# 📊 2. `LNNVL` 함수를 활용한 상호배타적 `UNION ALL` 분기 공식

### 💡 `LNNVL(condition)` 함수의 물리적 동작 원리
* `LNNVL(조건)`은 해당 조건이 **`FALSE`이거나 `UNKNOWN(NULL)`일 때만 `TRUE`**를 반환합니다.
* 즉, **"앞선 브랜치에서 이미 처리된 데이터를 후속 브랜치에서 완벽히 제외"**하여 `UNION ALL` 수행 시 `UNION`의 정렬/중복제거 부하 없이 동일한 결과를 100% 보장합니다.

```sql
-- [표준 모범 패턴] 컬럼별 OR 조건을 상호배타적 UNION ALL로 변환
SELECT /*+ INDEX(A IX_TB_DOC_01) */
       DOC_NO, REG_DT, CUST_ID, DEPT_CD
  FROM TB_DOC A
 WHERE CUST_ID = :CUST_ID  -- 1. 고객번호 인덱스 활용 (우선 추출)
UNION ALL
SELECT /*+ INDEX(A IX_TB_DOC_02) */
       DOC_NO, REG_DT, CUST_ID, DEPT_CD
  FROM TB_DOC A
 WHERE DEPT_CD = :DEPT_CD
   AND LNNVL(CUST_ID = :CUST_ID); -- 2. 앞선 1번 브랜치에서 조회된 고객 데이터 완벽 제외!
```

---

# ⚡ 3. IN-List + Top-N 쿼리 정렬 부하 제거 (브랜치 사전 Stopkey)

### 💡 왜 IN-List는 `SORT ORDER BY`를 생략할 수 없는가?
* `INLIST ITERATOR`는 `STAT_CD = 'A'`를 인덱스로 역순 정렬 스캔하고, 이어서 `STAT_CD = 'B'`를 인덱스로 역순 정렬 스캔합니다.
* 하지만 'A' 그룹 내부와 'B' 그룹 내부는 각각 정렬되어 있어도, **두 그룹을 합친 전체 데이터는 `REG_DT` 순서로 정렬되어 있지 않기 때문에** 최종 `SORT ORDER BY` 연산이 불가피하게 발생합니다.

### 🏆 [표준 정답] 브랜치별 사전 Top-N 추출 공식
```sql
SELECT *
  FROM (
        SELECT /*+ INDEX_DESC(A IX_TB_ORD_01) */
               ORD_NO, ORD_DT, STAT_CD, ORD_AMT
          FROM TB_ORD A
         WHERE STAT_CD = 'A'
           AND ROWNUM <= 10 -- 브랜치 1: 최대 10건만 읽고 즉시 Stop!
        UNION ALL
        SELECT /*+ INDEX_DESC(A IX_TB_ORD_01) */
               ORD_NO, ORD_DT, STAT_CD, ORD_AMT
          FROM TB_ORD A
         WHERE STAT_CD = 'B'
           AND ROWNUM <= 10 -- 브랜치 2: 최대 10건만 읽고 즉시 Stop!
       )
 ORDER BY ORD_DT DESC
 FETCH FIRST 10 ROWS ONLY; -- (또는 WHERE ROWNUM <= 10)
```
* **성능 효과:** 수백만 건 전체를 정렬하는 대참사를 막고, 단 20건만 읽어서 10건을 추출하므로 I/O가 99.9% 절감됩니다.

---

# 💬 4. 실전 질의응답(Q&A) 마스터 카드

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ 💬 Q1. USE_CONCAT 힌트와 직접 UNION ALL 작성 중 시험에서 무엇이 우선인가요?             │
│ 👉 A1. SQLP 실기에서는 옵티마이저 파라미터나 환경에 구애받지 않고 100% 확실한 실행계획을     │
│        보장하는 [직접 UNION ALL + LNNVL 배타적 분기 재작성]이 가장 높은 점수를 받습니다. │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 💬 Q2. LNNVL을 쓰지 않고 AND (CUST_ID <> :b OR CUST_ID IS NULL)로 쓰면 안 되나요?      │
│ 👉 A2. 논리적으로 동일하지만, LNNVL(CUST_ID = :b)이 훨씬 간결하고 NULL 비교 연산자의    │
│        3치 논리(3-Valued Logic) 오류를 원천 차단하는 오라클 표준 권장 함수입니다.         │
└────────────────────────────────────────────────────────────────────────────────────────┘
```
