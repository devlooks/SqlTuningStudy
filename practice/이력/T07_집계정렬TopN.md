# 🗂️ T07 GROUP BY / Sort / Top-N — 이력

- **최종 갱신:** 2026-09-18
- **사다리 위치:** 3/11 · **상태:** 🔵 진행 중 (현재 테마)
- **교안:** `SQLP_실기_테마교안.md` §2 T07 · **숙련도:** `SQLP_실기_테마별_숙련도.md` §4·§5·§9
- **세션 전문:** `이력/_세션전문.md` (시간순 원본)

> 이 파일에는 **T07 문항의 풀이 결과만** 적는다. 세션 전체 서술은 `_세션전문.md` 에 append 한다.
> 구 `판단 기준 #번호`는 폐기되었다. **교안 §1.6 매핑표**로 조회한다.

---

## 1. 풀이 이력

| 일자 | 세션 | Pattern ID | 난이도 | 판정 | 요약 |
|:---:|---|---|:---:|---|---|
| 2026-09-06 | B01 T07 | O01, P01 | 중급 | **독립해결 (60/100 -> 최종수정 100)** | [1교시: 계좌 거래내역] '='조건 선두 배치 및 정렬 컬럼 순서 완벽 도출. ASC 생성 인덱스에 순방향 INDEX 힌트 사용으로 스캔 방향 충돌 진단(부분오답 60점). 튜터의 'INDEX_DESC' 피드백을 즉시 수용 및 교정하여 최종 Mastered. |
| 2026-09-10 | 1교시 집계 위치 판별 (원본2 + 변형2) | G01, G03, R06 | 중~고 | 4문항 평균 66.3 / **독립해결 0** | 병목 Id **4/4**, ④비중 **4/4**, ③낭비율 코칭 후 2/2. B/C 판별 **3/4**. 그러나 **판정→SQL 이관 1/4 · 힌트 물리 검증 1/4 · 결과집합 3문장 0/4** — RC1(판정→SQL 이관 실패)·RC2(힌트 물리 검증 부재) 신규 특정. 진단 능력과 처방 능력의 분리가 실증된 세션 |

---

## 2. 출제 완료 · 미풀이 문항

> 출제는 끝났으나 아직 풀지 않은 문항이다. 풀고 나면 **§2 테마별 이력**과 **§3 세션 전문**으로 옮기고 이 절에서 지운다.


### SQLP 실기 2회독 — 1교시 3차 드릴 P·Q (SQL 작성 전용)


- **출제일:** 2026-09-18 (09-10 세션 이월분 재출제) · **테마:** T07 GROUP BY / 선집계 / Top-N
- **형식:** 처방 전용 — `[1] 병목 판정은 제공`, `[2] 개선 SQL만 작성`. 진단이 아니라 **처방** 훈련
- **설계 의도(사용자 제시분에는 미노출):**
  - **P:** 선집계 정답 + **AVG 결합법칙 함정** (`K22` 검증)
  - **Q:** 후집계 정답 + **허브 테이블 LEADING 카티션 함정** (`K15` 검증)
- ⚠️ 처방 전용 형식이므로 **진급 게이트 판정 대상이 아니다**(AGENTS §2.1).

#### 필수 제출물 3파트 (양 문항 공통)

1. **B/C 판별** — ① 팩트 테이블 ② B = 팩트 액세스 노드 A-Rows ③ C = 조인·필터를 모두 통과한 뒤 집계 직전 행 수 ④ **조인의 정체(붙이기 / 필터)** ⑤ 결론(선집계 / 후집계)
2. **개선 SQL** — 힌트 세트 포함 완성본 + 필요 시 인덱스 DDL
3. **힌트 사전검증 4항 + 결과집합 3문장**
   - 사전검증 ① LEADING 인접성(각 테이블이 앞에 나온 테이블 중 하나와 WHERE 조인 조건을 갖는가)
   - 사전검증 ② 힌트 짝 정합성(`PUSH_PRED`는 NL 전용, `USE_HASH`와 동시 사용 시 무효)
   - 사전검증 ③ 인덱스 실존 / 신규 설계 시 선두 컬럼 = 조인키
   - 사전검증 ④ 손익분기(NL 반복횟수 × 회당 블록수 **vs** 상대 FULL 블록수, 숫자로)
   - 결과집합 3문장 = 행 수 / NULL / 중복

---

#### 드릴 P

##### 테이블·통계

| 테이블 | 건수 | 비고 |
|---|---:|---|
| TB_SALE_DTL | 200,000,000 | PK (SALE_NO, DTL_SEQ) / `TB_SALE_DTL_X01 (SALE_DT)` / SALE_DT 순 적재(클러스터링 양호) / FULL 시 약 2,500,000 블록 |
| TB_CUST | 20,000,000 | PK (CUST_NO) / GRADE_CD 5종 / **FULL 시 약 250,000 블록** |

- `TB_SALE_DTL.SALE_AMT`, `UNIT_PRICE`, `STORE_CD`, `CUST_NO` 는 **NOT NULL**
- 2026-01 판매상세 = 12,000,000건, 해당 기간 (STORE_CD, CUST_NO) 조합 = **500,000**
- 점포 3,000개, 최종 결과 12,400행

##### AS-IS SQL

```sql
SELECT d.STORE_CD,
       c.GRADE_CD,
       SUM(d.SALE_AMT)   AS TOT_AMT,
       COUNT(*)          AS SALE_CNT,
       AVG(d.UNIT_PRICE) AS AVG_PRICE
  FROM TB_SALE_DTL d,
       TB_CUST     c
 WHERE d.SALE_DT >= DATE '2026-01-01'
   AND d.SALE_DT <  DATE '2026-02-01'
   AND c.CUST_NO  = d.CUST_NO
 GROUP BY d.STORE_CD, c.GRADE_CD;
```

##### AS-IS 실행계획

```
-----------------------------------------------------------------------------------------------------------------
| Id | Operation                              | Name            |     Starts | E-Rows |     A-Rows |    Buffers |
-----------------------------------------------------------------------------------------------------------------
|  0 | SELECT STATEMENT                       |                 |          1 |        |     12,400 | 48,182,140 |
|  1 |  HASH GROUP BY                         |                 |          1 | 11,908 |     12,400 | 48,182,140 |
|  2 |   NESTED LOOPS                         |                 |          1 | 11,842K| 12,000,000 | 48,182,140 |
|  3 |    TABLE ACCESS BY INDEX ROWID BATCHED | TB_SALE_DTL     |          1 | 11,842K| 12,000,000 |    182,140 |
|  4 |     INDEX RANGE SCAN                   | TB_SALE_DTL_X01 |          1 | 11,842K| 12,000,000 |     32,140 |
|  5 |    TABLE ACCESS BY INDEX ROWID         | TB_CUST         | 12,000,000 |      1 | 12,000,000 | 48,000,000 |
|  6 |     INDEX UNIQUE SCAN                  | TB_CUST_PK      | 12,000,000 |      1 | 12,000,000 | 36,000,000 |
-----------------------------------------------------------------------------------------------------------------

Predicate Information (identified by operation id):
   4 - access("D"."SALE_DT">=TO_DATE('2026-01-01') AND "D"."SALE_DT"<TO_DATE('2026-02-01'))
   6 - access("C"."CUST_NO"="D"."CUST_NO")
```

##### [1] 병목 판정 (제공)

- **병목 Id: 5 (+6)** — TB_CUST 반복 액세스
- **③ 낭비율:** 12,000,000 ÷ 12,400 = **968배** (행 낭비형)
- **④ 비중:** (12,000,000 + 36,000,000) ÷ 48,182,140 = **99.6%**

##### [2] 요구 — 개선 SQL (60점) + 필수 제출물 3파트

- 제약: 인덱스 신규 생성 1개까지 허용(불필요하면 생성하지 않아도 됨). 결과집합은 AS-IS와 완전히 동일해야 한다.

---

#### 드릴 Q

##### 테이블·통계

| 테이블 | 건수 | 비고 |
|---|---:|---|
| TB_CLAIM_DTL | 300,000,000 | PK (CLAIM_NO, DTL_SEQ) / CLAIM_AMT NOT NULL / FULL 시 4,300,000 블록 / 청구당 평균 7.5행 |
| TB_CLAIM | 40,000,000 | PK (CLAIM_NO) / `TB_CLAIM_X01 (CLAIM_DT)` / 컬럼 CLAIM_DT, HOSP_CD, MEMB_NO |
| TB_HOSP | 30,000 | PK (HOSP_CD) / REGION_CD / FULL 700 블록 / REGION_CD='11' = 4,000건 |
| TB_MEMB | 8,000,000 | PK (MEMB_NO) / PROD_CD / FULL 160,000 블록 / PROD_CD='P0731' = 1,600,000명 |

- 2026-01-01 ~ 2026-03-31 청구 = 480,000건, 그중 서울(11) 병원 = 62,000건, 그중 P0731 가입자 = **12,400건**
- TB_CLAIM_DTL 은 모든 청구에 대해 1건 이상 존재

##### AS-IS SQL

```sql
SELECT cl.CLAIM_NO, cl.CLAIM_DT, h.HOSP_NM, m.MEMB_NO,
       d.TOT_AMT, d.DTL_CNT
  FROM (SELECT CLAIM_NO,
               SUM(CLAIM_AMT) AS TOT_AMT,
               COUNT(*)       AS DTL_CNT
          FROM TB_CLAIM_DTL
         GROUP BY CLAIM_NO) d,
       TB_CLAIM cl,
       TB_HOSP  h,
       TB_MEMB  m
 WHERE cl.CLAIM_DT >= DATE '2026-01-01'
   AND cl.CLAIM_DT <  DATE '2026-04-01'
   AND h.HOSP_CD   = cl.HOSP_CD
   AND h.REGION_CD = '11'
   AND m.MEMB_NO   = cl.MEMB_NO
   AND m.PROD_CD   = 'P0731'
   AND d.CLAIM_NO  = cl.CLAIM_NO;
```

##### AS-IS 실행계획

```
-----------------------------------------------------------------------------------------------------------------
| Id | Operation                              | Name            | Starts | E-Rows |      A-Rows |    Buffers |
-----------------------------------------------------------------------------------------------------------------
|  0 | SELECT STATEMENT                       |                 |      1 |        |      12,400 |  4,487,105 |
|  1 |  HASH JOIN                             |                 |      1 | 11,902 |      12,400 |  4,487,105 |
|  2 |   HASH JOIN                            |                 |      1 | 12,400 |      12,400 |    187,105 |
|  3 |    HASH JOIN                           |                 |      1 | 62,000 |      62,000 |     27,105 |
|  4 |     TABLE ACCESS FULL                  | TB_HOSP         |      1 |  4,000 |       4,000 |        700 |
|  5 |     TABLE ACCESS BY INDEX ROWID BATCHED| TB_CLAIM        |      1 |   480K |     480,000 |     26,405 |
|  6 |      INDEX RANGE SCAN                  | TB_CLAIM_X01    |      1 |   480K |     480,000 |      1,405 |
|  7 |    TABLE ACCESS FULL                   | TB_MEMB         |      1 | 1,600K |   1,600,000 |    160,000 |
|  8 |   VIEW                                 |                 |      1 | 40,000K|  40,000,000 |  4,300,000 |
|  9 |    HASH GROUP BY                       |                 |      1 | 40,000K|  40,000,000 |  4,300,000 |
| 10 |     TABLE ACCESS FULL                  | TB_CLAIM_DTL    |      1 |   300M | 300,000,000 |  4,300,000 |
-----------------------------------------------------------------------------------------------------------------

Predicate Information (identified by operation id):
   1 - access("D"."CLAIM_NO"="CL"."CLAIM_NO")
   2 - access("M"."MEMB_NO"="CL"."MEMB_NO")
   3 - access("H"."HOSP_CD"="CL"."HOSP_CD")
   4 - filter("H"."REGION_CD"='11')
   6 - access("CL"."CLAIM_DT">=TO_DATE('2026-01-01') AND "CL"."CLAIM_DT"<TO_DATE('2026-04-01'))
   7 - filter("M"."PROD_CD"='P0731')
```

##### [1] 병목 판정 (제공)

- **병목 Id: 8 (+9, 10)** — 인라인 뷰 `d`
- **③ 낭비율:** 40,000,000 ÷ 12,400 = **3,226배** (Id 10 기준이면 24,194배)
- **④ 비중:** 4,300,000 ÷ 4,487,105 = **95.8%**

##### [2] 요구 — 개선 SQL (60점) + 필수 제출물 3파트

- 제약: 인덱스 신규 생성 1개까지 허용. 결과집합은 AS-IS와 완전히 동일해야 한다.
- 힌트 세트는 **LEADING 을 반드시 포함**하여 조인 순서를 명시할 것.

---

#### 채점 배점 (문항당 100점)

| 항목 | 배점 |
|---|---:|
| B/C 판별 + 조인의 정체 판정 | 20 |
| 개선 SQL 구조 (선집계/후집계 정확 반영) | 30 |
| 힌트 세트 물리적 성립 | 20 |
| 인덱스 설계 (선두 컬럼) | 10 |
| 힌트 사전검증 4항 | 10 |
| 결과집합 3문장 | 10 |

---

### [추가 출제] 2교시 문제 1 — 1:N 증폭 / DISTINCT 제거

- **출제일:** 2026-09-18
- **설계 의도(비공개):** J07·J10·O03 — 1:N 증폭 후 `DISTINCT` 정리 구조를 **세미 조인(EXISTS)** 으로 전환.
  부수 검증: ① 테이블 액세스 소멸(커버링) ② **신규 인덱스 불필요** 판단 ③ `DISTINCT` 동반 제거
- **형식:** 정식 2문항 (`[1]` 40점 + `[2]` 60점)

##### 통계

| 테이블 | 건수 | 비고 |
|---|---:|---|
| TB_CUST | 20,000,000 | PK (CUST_NO) / `TB_CUST_X02 (GRADE_CD)` / GRADE_CD 6종 / CUST_NO·GRADE_CD NOT NULL |
| TB_CUST (VIP+VVIP) | 400,000 | |
| TB_ORD | 300,000,000 | PK (ORD_NO) / `TB_ORD_X01 (CUST_NO, ORD_DT)` / CUST_NO·ORD_DT NOT NULL / CUST_NO 순 적재 아님 |

- VIP/VVIP 고객의 2026년 주문 = 24,000,000건 (1인 평균 60건)
- 2026년 주문이 1건 이상인 VIP/VVIP 고객 = **380,000명** (= 최종 결과)

##### AS-IS SQL

```sql
SELECT DISTINCT c.CUST_NO, c.CUST_NM, c.GRADE_CD
  FROM TB_CUST c,
       TB_ORD  o
 WHERE c.GRADE_CD IN ('VIP','VVIP')
   AND o.CUST_NO = c.CUST_NO
   AND o.ORD_DT >= DATE '2026-01-01';
```

##### AS-IS 실행계획

```
--------------------------------------------------------------------------------------------------------------
| Id | Operation                              | Name        |  Starts | E-Rows |     A-Rows |    Buffers |
--------------------------------------------------------------------------------------------------------------
|  0 | SELECT STATEMENT                       |             |       1 |        |    380,000 | 25,341,400 |
|  1 |  HASH UNIQUE                           |             |       1 |   366K |    380,000 | 25,341,400 |
|  2 |   NESTED LOOPS                         |             |       1 | 23,842K| 24,000,000 | 25,341,400 |
|  3 |    TABLE ACCESS BY INDEX ROWID BATCHED | TB_CUST     |       1 |   398K |    400,000 |     61,400 |
|  4 |     INDEX RANGE SCAN                   | TB_CUST_X02 |       1 |   398K |    400,000 |      1,400 |
|  5 |    TABLE ACCESS BY INDEX ROWID BATCHED | TB_ORD      | 400,000 |     59 | 24,000,000 | 25,280,000 |
|  6 |     INDEX RANGE SCAN                   | TB_ORD_X01  | 400,000 |     59 | 24,000,000 |  1,280,000 |
--------------------------------------------------------------------------------------------------------------

Predicate Information (identified by operation id):
   4 - access("C"."GRADE_CD"='VIP' OR "C"."GRADE_CD"='VVIP')
   6 - access("O"."CUST_NO"="C"."CUST_NO" AND "O"."ORD_DT">=TO_DATE('2026-01-01'))
```

##### 정답 (채점용)

- `[1]` 병목 **Id 5** — 순수 Buffers 24,000,000 (전체의 94.7%). 존재 여부만 필요한데 24,000,000행의 테이블 블록을 랜덤 액세스
- ③ 24,000,000 ÷ 380,000 = **63배** (행 낭비형) / ④ **94.7%**
- 검산 4항: 1,400 + 60,000 + 1,280,000 + 24,000,000 = 25,341,400

```sql
SELECT c.CUST_NO, c.CUST_NM, c.GRADE_CD
  FROM TB_CUST c
 WHERE c.GRADE_CD IN ('VIP','VVIP')
   AND EXISTS (SELECT /*+ NL_SJ INDEX(o TB_ORD_X01) */ 1
                 FROM TB_ORD o
                WHERE o.CUST_NO = c.CUST_NO
                  AND o.ORD_DT >= DATE '2026-01-01');
```

- **신규 인덱스 불필요** — `TB_ORD_X01 (CUST_NO, ORD_DT)` 가 이미 커버링
- TO-BE Buffers ≈ 61,400 + 1,200,000 = **약 1,261,400 → 20배 개선**
- `DISTINCT` 제거 필수 (세미 조인은 좌측을 증폭하지 않음 → `HASH UNIQUE` 소멸)
