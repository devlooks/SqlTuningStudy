SQL Server의 Lock
  - 변경 중 레코드 일기 -> 커밋시까지 대기
  - 다른 트랜잭션이 조회중 레코드 읽을때는 기다리지 X
  - 대량 변경 데이터일 경우 -> lock Escalation이 발생

Insert되는 데이터에 대해 DML 동시 수행 되지 않는다.
단, 제약 조건이 없다면, Insert 동시 가능(Unique, PK 등..)

Insert 중인 데이터 -> 변경, 변경 삭제 -> 불가능
  - 쿼리 상으로 Insert 데이터가 포함되지 않는 경우, 해당 조건 컬럼이 Index인 경우  
    -> full Scan -> 해당 Insert 데이터 지나칠떄 블로킹으로 읽지 않음

오라클 데이터 변경 -> 로우 Lock + 테이블 Lock -> DML 중 DDL 수행하지 못하도록 함
  - 테이블 lock 일경우 데이터 조회시 문제 되지 않는다(lock에 따라 호환가능)
  - RX(Row Exclusive) 까지 서로 호환

1개 table 당 -> TM Lock
1개 TX 당 -> TX Lock

Insert시 데이터 컬럼에 제약 조건이 없는 한 교착 상태 발생X

트랜잭션 4가지 특징
  - 원자 -> 트랜잭션 분해 X 최소단위 -> 전부 처리 또는 하나도 처리 X
  - 일관 -> 트랜잭션 성공 -> DB 일관 상태 (결과 모순X)
  - 격리 -> 트랜잭션 중간 결과 -> 다른 트랜잭션 접근 안됨 -> Dirty Read
  - 영속 -> 실행 성공적 완료 -> DB영속적 저장

Read Uncommited -> Dirty Read 가능하다(커밋 X 데이터 읽음)

Dirty Read : 변경 중 데이터 읽기 -> 최종에서 롤백 -> 비일관성 상태
Non-Repeatable Read : 한 트랜잭션 내, 같은 데이터 두번이상 읽음 -> 읽은 값이 달라짐
Phantom Read : 일정 범위 데이터 두번 이상 읽기 -> 새로운 데이터 추가 -> 없던 데이터 생김

Read Uncommited : Dirty Read, Non-Repeatable Read, Phantom Read
Read Commited : Non-Reapeatable Read, Phatom Read
Repeatable Read : Phantom Read
Serializable : 없음

Read Commited 격리성 -> 읽기 직전 공유 Lock 획득 -> 다음 레코드 이동 순간 Lock 해제
Repeatable Read 격리성 -> 읽기 직전 lock 획득 -> 최종 커밋, 롤백 순간 lock 해제
Serializable 격리성 -> 어떤 lock 도 사용 불가능

- with(nolock) -> Dirty Read 허용 힌트 -> 일관성 보장하지 않음 -> 제한적 사용 필요
- DBMS의 기본 격리성 수준 -> Read Committed -> Dirty Read 만 방지
- Serializable -> 개발 세션 레벨에 필요한 경우만 사용
  - 단, 부작용 발생 가능성 높음
    - Sql Server -> 심한 lock 경합 성능 떨어짐
    - Oracle -> DML 수행시 충돌 자주 발생 -> 작업 실패
   
- 격리성 수준 변경 명령어
  - set transaction level read committed
 
갱싱 대상 식별
  - Oracle(MVCC) -> Update 문 시작 시점 -> 발견시 갱신
  - SQL Server -> 레코드 도달 지점 -> 갱신 대상 식별
    - Oracle Update -> 비동기 식으로, 전부 읽은 후 처리 (로우 X, 처리 X)
    - SQL Server -> 동기 쿼리문 종료 떄 까지 대기 후 다음 쿼리 구동
   
동시성 제어
  - 일관성 -> 데이터품질과 연관
  - 동시성 -> 성능
  - 독립 DB -> 동시성 제어 불필요

비관적 동시성 제어, 낙관적 동시성 제어
  - 비관적 -> 데이터 읽는 시점 lock 설정 (for update)
  - 낙관적 -> 변경 여부 확인(쿼리문 또는 plsql 특수 구문으로 확인)

Serializable -> SQL 문장 수준 일관성 보장

WAIT 나 NOWAIT 옵션은 Select 문에서만 가능

select ~ for update wait 3;
  - lock 걸린 레코드 3초 기다림 -> 3초 대기 후 -> select 문 전체 종료

Update 로 인한 건수 변경 -> 결과 달라짐 -> 동시성 보장 X

MVCC 
  - 문장 수준 일관성 부장
  - 트랜잭션 수준 일관성 보장 X (Serializable 이면 가능)

SnapShot too old
  - fetch across commit 형태 프로그램 지양
  - 정렬 불필요 해도 order by 추가로 해소
  - 대량 Update 후 -> Full Scan 쿼리 수행 -> delayed block clean out -> 해소
