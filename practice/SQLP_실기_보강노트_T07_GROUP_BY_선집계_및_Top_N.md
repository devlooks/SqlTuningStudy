# 📖 [T07] GROUP BY 선집계 & 그룹별 Top-N 튜닝 마스터 보강노트

- **테마:** `T07 GROUP BY / Sort / Top-N`
- **기준 마스터 문서:** `AGENTS.md`, `SQLP_실기_2회독_통합패턴맵_v2_3_최종확정.md`
- **문서 목적:** 실전 시험 직전 1:N 조인 증폭 해소를 위한 다측 선집계(`NO_MERGE` + `USE_HASH`), 그룹별 Top-1 최신 데이터 추출(`PUSH_PRED` + `USE_NL`), 분석함수(`ROW_NUMBER`)의 인덱스 정렬 생략(`WINDOW NOSORT`)을 1초 만에 풀어내기 위한 핵심 체크노트

---

# 🚨 [실전 직전 3분] GROUP BY & Top-N 5대 함정 탈출 체크리스트

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ ⚠️ [함정 1] 1:N 관계 조인 후 바깥에서 GROUP BY 하여 수천만 건 조인 증폭을 유발하는 실수 │
│ 👉 탈출법: N측 테이블(다측)을 인라인 뷰에서 먼저 [선집계(GROUP BY)] 한 뒤 1:1 조인 결합! │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ ⚠️ [함정 2] GROUP BY 선집계 인라인 뷰(V)와 결합할 때 습관적으로 USE_NL을 지정하는 실수  │
│ 👉 탈출법: 선집계 완료된 인라인 뷰 집합에는 [인덱스가 없으므로] 무조건 [USE_HASH(V)]!   │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ ⚠️ [함정 3] 사원/고객별 최신 1건 추출 시 ROW_NUMBER 인라인 뷰 전체를 소트시키는 실수    │
│ 👉 탈출법: [PUSH_PRED + USE_NL]을 적용하여 Outer 건별로 인덱스 1건만 읽고 즉시 Stop!  │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ ⚠️ [함정 4] ROW_NUMBER() OVER (PARTITION BY A ORDER BY B DESC)용 인덱스 선두 오판     │
│ 👉 탈출법: 인덱스는 반드시 [PARTITION BY 컬럼(A) 선두 + ORDER BY 컬럼(B) 후미] 구성!   │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ ⚠️ [함정 5] 선집계 뷰 변환 시 마스터에 매칭 없는 데이터 유실(INNER JOIN) 실수          │
│ 👉 탈출법: 원본 쿼리가 마스터를 보존해야 한다면 선집계 뷰 결합 시 [LEFT OUTER JOIN] 필수!│
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

# 🛡️ 1. 다측(N) 선집계 인라인 뷰 변환 3대 원칙

### 💡 1:N 조인 후 GROUP BY vs 사전 선집계 비교
* **AS-IS (조인 후 집계):** 1(마스터 10만) $\times$ N(상세 1,000만) $\rightarrow$ **1,000만 건 조인 증폭** $\rightarrow$ `HASH GROUP BY` (1,000만 건 정렬/해시 부하)
* **TO-BE (사전 선집계 후 조인):** N(상세 1,000만) $\rightarrow$ **사전 `GROUP BY` (10만 건 축소)** $\rightarrow$ 마스터 10만 건과 1:1 `USE_HASH` 결합 (중간 집합 99% 급감!)

```sql
-- [표준 모범 패턴] 다측 선집계 인라인 뷰 + USE_HASH
SELECT /*+ LEADING(C V) USE_HASH(V) */
       C.CUST_ID,
       C.CUST_NM,
       NVL(V.ORD_CNT, 0)   AS ORD_CNT,
       NVL(V.TOTAL_AMT, 0) AS TOTAL_AMT
  FROM TB_CUST C
  LEFT OUTER JOIN (
       SELECT /*+ NO_MERGE */
              CUST_ID,
              COUNT(ORD_NO) AS ORD_CNT,
              SUM(ORD_AMT)  AS TOTAL_AMT
         FROM TB_ORD
        WHERE ORD_DT BETWEEN '20260101' AND '20260630'
        GROUP BY CUST_ID
       ) V
    ON C.CUST_ID = V.CUST_ID
 WHERE C.GRADE_CD = 'VIP';
```

---

# ⚡ 2. 그룹별 최신 1건 (Top-1) 고속 추출 2대 해법

### 💡 해법 1: `PUSH_PRED` + `USE_NL` 상관 인라인 뷰 기법
* **적용 조건:** Outer(사원/고객) 건수가 소량(수천 건 이하)이고, Inner에 `(EMP_ID, APPR_DT DESC)` 결합 인덱스가 있을 때
* **동작 원리:** 인라인 뷰 내부로 Outer의 `EMP_ID` 조건이 침투(`PUSH_PRED`)하여, 사원당 최신 1건만 인덱스로 읽고 Stopkey 종료.

```sql
-- [인덱스] IX_TB_APPR_01: (EMP_ID, APPR_DT DESC, APPR_NO)
SELECT /*+ LEADING(E V) USE_NL(V) */
       E.EMP_ID,
       E.EMP_NM,
       V.APPR_NO,
       V.APPR_DT,
       V.APPR_AMT
  FROM TB_EMP E,
       LATERAL ( -- 또는 PUSH_PRED 적용 상관 서브쿼리
       SELECT /*+ NO_MERGE PUSH_PRED */
              A.APPR_NO, A.APPR_DT, A.APPR_AMT
         FROM TB_APPR A
        WHERE A.EMP_ID = E.EMP_ID
        ORDER BY A.APPR_DT DESC
        FETCH FIRST 1 ROWS ONLY
       ) V
 WHERE E.DEPT_CD = 'D01';
```

### 💡 해법 2: `ROW_NUMBER` + `WINDOW NOSORT` 인덱스 활용 기법
* **적용 조건:** 전체 사원에 대해 일괄 배치 추출할 때
* **인덱스 설계:** `(EMP_ID, APPR_DT DESC)`로 인덱스를 생성하면 `ROW_NUMBER() OVER (PARTITION BY EMP_ID ORDER BY APPR_DT DESC)` 수행 시 정렬 연산이 100% 생략(`WINDOW NOSORT`)됩니다.

---

# 💬 3. 실전 질의응답(Q&A) 마스터 카드

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ 💬 Q1. 선집계 인라인 뷰에 왜 반드시 /*+ NO_MERGE */를 주어야 하나요?                    │
│ 👉 A1. 옵티마이저가 Complex View Merging을 수행하여 인라인 뷰의 GROUP BY를 풀어서       │
│        메인 쿼리와 합쳐버리면, 다시 1:N 조인 증폭이 발생하므로 독립 집계를 강제합니다.    │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 💬 Q2. PUSH_PRED 힌트 적용 시 왜 USE_HASH가 아닌 USE_NL을 써야 하나요?                 │
│ 👉 A2. PUSH_PRED는 Outer 테이블의 각 행에서 값을 하나씩 건네받아 Inner 뷰를 반복 실행      │
│        (Starts N회)하므로, Loop 기반의 Nested Loops 조인(USE_NL)과만 결합할 수 있습니다.│
└────────────────────────────────────────────────────────────────────────────────────────┘
```
