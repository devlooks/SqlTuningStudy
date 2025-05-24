- ordered : 순서대로
- leading : 조인 순서 지정
- no_swap_join_inputs : BuildInput 지정
- swap_join_inputs : Probe Input 지정
- 힌트 지정시, index 지정 확인하기

부분 처리 
  1. 소트 생략
  2. lpad(avg(거래금액), 10) || lpad(avg(거래금액), 10) || lpad(avg(거래금액), 10)
     -> to_number(substr(금액, 1, 10)) , to_number(substr(금액, 11, 21)) , to_number(substr(금액, 21, 30))
  3. no_merge push_pred 사용 (group by 쿼리로 조건 push)
     - main Query ex) no_merge(t) push_pred(t)
     - sub Query ex) no_merge push_pred

조인 처리
- 모두 출력 -> 부분 처리 X
- 비 파티션
  - 파티션 Pruning X, nl 조인 X
  - 결과 집합 10%이하 -> 인덱스 이용 -> 테이블 정보 (속성 100/50 만건) -> hash 사용 X
- 데이터 종류 -> 선택도 계산
- 등록 상품 20000건 -> 모두 읽기 -> full Scan (filter 조건 X)
- 고르게 주문 -> hash 조인 권장(뷰, 메인 테이블간)
- rownum 사용시 적은 량 조인 -> nl 조인 권장
- index_ffs : 조건절 컬럼 + 조회 컬럼 -> 인덱스에 포함, (정렬X)
- no_nl_batching : Batch I/O 사용 X (full - 데이터 정렬 보장X)-> 순서 엉킴 제어


인덱스 생성 명령어
- create index t_x1 on t_name(c1, c2);

Outer 조인시 조인 조건 
- Inner Table (+) 표시 = Outer Table

일시 -> 일자로 변경
- trunc(sysdate)
- 쿼리에 Between 있을시, 부등호로 변경 -> 스캔 범위 의미가 있는지 확인
- 변경일자 = to_char(sysdate, 'yyyymmdd')

점이력
```
(a, b) = (select a, b from
                    (select a, b from t as h
                      where h.a = mainT.a
                      order by 일자 desc, 순번 desc)
          where rownum <= 1)
order by mainT.a 
```

선분 이력
```
and 부등호 조건(시작 <= sysdate)
and 부등호 조건(종료 >= sysdate)
```

직전 이력 
```
and 최종변경일시 > 유효시작일시
and 최종변경일시 <= 유효종료일시 - 1/(60*60*24) -> 직전 일의
```

쿼리변환
- no_unnest push_subq : 스칼라 쿼리 부분 처리
- no_merge push_pred : 서브쿼리 부분 처리

테이블 연관 -> arc 관계
- 서로 배타적 관계 -> 배타 관계 테이블을 Outer 처리 (+) 조인
- index 중복 스캔 X 경우 -> Union all 로 분기
- index 중복 스캔 O 경우 -> decode 로 분기 조인, decode 분기 출력

