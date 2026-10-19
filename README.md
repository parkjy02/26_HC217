# 26_HC217


## 💡1. 프로젝트 개요

### 1-1. 프로젝트 소개

- **프로젝트 명** : GNSS-LiDAR 기반 실내외 다층 이동 물류 운송 로봇
- **프로젝트 정의** : LiDAR 및 GNSS 기반 자율주행, 비전 기반 엘리베이터 조작, 매니퓰레이터와 자동 적재함을 통합하여 실내외 다층 환경에서 자율적인 물류 운송을 수행하는 모바일 매니퓰레이터 시스템

### 1-2. 개발 배경 및 필요성

기존 자율주행 물류 로봇은 주로 실내 또는 단일 층을 중심으로 운용되어 건물 간 이동이나 층간 이동이 필요한 환경에서는 활용이 제한적입니다. 특히 다층 이동을 지원하는 로봇은 엘리베이터 관제 서버나 통신 API 연동에 의존하는 경우가 많아 별도의 인프라 구축 비용이 발생하며, 기존 건물에 적용하기 어렵다는 한계가 있습니다.

이러한 문제를 해결하기 위해 별도의 엘리베이터 통신 인프라 없이도 로봇이 직접 버튼을 인식하고 조작할 수 있는 독립형 다층 이동 기술이 필요합니다. 또한 실내와 실외를 연계한 자율주행 기술을 통해 단일 건물 내부에 국한된 물류 운송 범위를 확장할 필요가 있습니다.

이에 본 프로젝트에서는 LiDAR SLAM과 GNSS 기반 자율주행 기술을 결합하고, Depth Camera와 매니퓰레이터를 활용한 엘리베이터 조작 기능을 통합하여 실내외 다층 환경에서 연속적인 물류 운송이 가능한 자율주행 로봇을 개발하고자 하였습니다.

### 1-3. 프로젝트 특장점

- **실내외 연계 자율주행** : LiDAR SLAM 기반 실내 위치 추정과 RTK-GNSS 기반 실외 위치 추정을 활용하여 다양한 주행 환경에 대응
- **인프라 비의존형 층간 이동** : 별도의 엘리베이터 통신 연동 없이 YOLOv8 객체 인식과 매니퓰레이터를 이용하여 엘리베이터 버튼을 직접 조작
- **다층 지도 전환 시스템** : 층별 실내 지도를 독립적으로 관리하고 엘리베이터 이동 후 목표 층의 지도로 전환하여 자율주행 재개
- **비전 기반 정밀 매니퓰레이터 제어** : Depth Camera를 이용한 3차원 좌표 추정과 MoveIt 기반 경로 계획을 통해 목표 버튼 자동 조작
- **물류 운송 기능 확장** : 매니퓰레이터와 자동 적재함을 결합하여 물품 운송뿐 아니라 적재 및 하역 작업까지 수행할 수 있도록 설계
- **안전 및 상태 모니터링** : 모터 피드백 전류 기반 끼임 감지와 로봇 위치 및 운송 상태 모니터링 기능을 통해 운용 안전성과 관리 편의성 확보

### 1-4. 주요 기능

- **LiDAR SLAM 기반 실내 자율주행** : 실내 지도 생성, AMCL 기반 위치 추정, Dijkstra 전역 경로 계획 및 TEB 기반 장애물 회피와 경로 추종
- **RTK-GNSS 기반 실외 자율주행** : GNSS 절대 위치 정보와 IMU Heading 정보를 활용한 실외 경로 추종 및 LiDAR 기반 장애물 감지
- **엘리베이터 자동 탑승 및 층간 이동** : YOLOv8 기반 버튼 인식, Depth Camera 기반 3차원 위치 추정, 매니퓰레이터 버튼 조작 및 층별 지도 전환
- **매니퓰레이터 자동 제어** : URDF 기반 좌표계 변환, MoveIt 역기구학 계산 및 RRTConnect 경로 계획을 활용한 로봇팔 제어
- **자동 적재함 및 안전 제어** : 다이나믹셀 모터를 이용한 적재함 자동 개폐와 피드백 전류 기반 과부하 감지
- **로봇 상태 및 위치 모니터링** : RViz 및 Kakao Maps API를 활용한 위치 시각화와 운송 상태, 적재 여부, 오류 정보 표시
- **ROS 기반 통합 제어** : ROS Topic 및 Service 통신을 활용하여 자율주행, 객체 인식, 매니퓰레이터 제어 및 물류 운송 시퀀스를 통합 관리

### 1-5. 기대 효과 및 활용 분야

- **기대 효과**
  - 엘리베이터 통신 인프라 구축 없이 기존 건물에 적용할 수 있어 시스템 도입 비용과 환경적 제약 감소
  - 실내외 연계 자율주행 및 독립적인 층간 이동을 통해 물류 로봇의 운용 범위 확대
  - 매니퓰레이터와 자동 적재함을 활용하여 단순 운송을 넘어 물품 적재 및 하역을 포함한 물류 작업 자동화 가능
  - 실시간 위치 및 상태 모니터링과 안전 제어 기능을 통해 물류 운송의 효율성과 안정성 향상
  - ROS 기반 모듈형 시스템을 활용하여 다양한 서비스 로봇 및 물류 환경으로 기능 확장 가능

- **활용 분야**
  - 병원 및 의료시설 내 의약품, 검체, 의료 물품의 층간 운송
  - 대학 및 공공기관 내 서류, 택배, 물품의 무인 운송
  - 오피스 및 복합 건물 내 실내외 연계 배송 서비스
  - 거동 불편자 및 노약자를 위한 생활 지원과 비대면 물품 전달 서비스
  - 다층 물류시설 및 스마트빌딩의 자율 물류 운송 시스템

### 1-6. 기술 스택

- **운영체제** : Ubuntu 20.04
- **개발언어** : Python, C++, C
- **로봇 개발 프레임워크** : ROS Noetic, MoveIt
- **자율주행 및 위치 추정** : LiDAR SLAM, AMCL, EKF, Dijkstra, TEB, RTK-GNSS
- **컴퓨터 비전 및 객체 인식** : YOLOv8, OpenCV, Intel RealSense Depth Camera
- **매니퓰레이터 제어** : MoveIt, RRTConnect, URDF, TF, Dynamixel SDK
- **임베디드 및 모터 제어** : STM32, OpenCR, OpenRB, BLDC Motor, Dynamixel Motor
- **시뮬레이션 및 시각화** : RViz, Gazebo, Kakao Maps API
- **개발 도구** : Visual Studio Code, Arduino IDE, STM32CubeIDE, CMake, Catkin Workspace
- **통신 및 시스템 연동** : UART, USB, HTTP, ROS Topic/Service, Dynamixel Protocol 2.0
- **형상관리 및 협업** : GitHub, Discord


## 💡2. 팀원 소개
<img width="1127" height="398" alt="image" src="https://github.com/user-attachments/assets/e18098ed-a511-4dd2-85fa-ad892f90e466" />


## 💡3. 시스템 구성도

• 서비스 시나리오

<img width="543" height="716" alt="image" src="https://github.com/user-attachments/assets/6c9cf478-42ac-4908-bbcc-3fcf0915b540" />


• 시스템 구성도

<img width="680" height="338" alt="image" src="https://github.com/user-attachments/assets/a9729265-e719-4ed9-b6ac-971eb2c8ac94" />


• 서비스 흐름도

<img width="702" height="467" alt="image" src="https://github.com/user-attachments/assets/48a8e558-4d03-4637-abf2-542bc66f439e" />


## 💡4. 작품 소개영상

[![한이음 드림업 프로젝트 소개영상](https://img.youtube.com/vi/miliMlOqH7A/hqdefault.jpg)](https://www.youtube.com/watch?v=miliMlOqH7A)


## 💡5. 핵심 소스코드

### 5-1. AMCL 기반 위치추정 알고리즘 개선

- **개선 목적** : 파티클 재분포 방식 개선을 통한 위치추정 안정성 향상
- **파티클 생성** : 현재 추정 위치를 중심으로 가우시안 분포 기반 신규 파티클 생성
- **유효성 검증** : 지도 내 유효 좌표 및 장애물 점유 여부 확인을 통한 자유 공간 파티클 선별
- **리샘플링 적용** : 개선된 파티클 생성 함수를 AMCL 리샘플링 과정에 적용

**핵심 소스코드: 가우시안 분포 기반 파티클 생성**

```cpp
pf_vector_t
AmclNode::gaussianPoseGenerator(void* arg)
{
  map_t* map = (map_t*)arg;
  pf_vector_t p;

  for(;;)
  {
    p.v[0] = temp_x + gaussianRandom(0, 0.5);
    p.v[1] = temp_y + gaussianRandom(0, 0.5);
    p.v[2] = temp_t + gaussianRandom(0, 0.1) * 2 * 3.141592 * 0.05;

    int i,j;
    i = MAP_GXWX(map, p.v[0]);
    j = MAP_GYWY(map, p.v[1]);
    if(MAP_VALID(map,i,j) && (map->cells[MAP_INDEX(map,i,j)].occ_state == -1))
      break;
  }
  return p;
}
```


### 5-2. 비전 기반 로봇팔 제어 및 버튼 조작

- **객체 인식** : YOLOv8과 Depth Camera를 활용한 엘리베이터 버튼 인식 및 3차원 좌표 추정
- **좌표 변환** : TF를 이용한 카메라 좌표계에서 로봇 기준 좌표계로의 변환
- **위치 제어** : MoveIt 기반 목표 위치 이동 및 FK를 활용한 관절 위치 보정
- **접촉 감지** : Dynamixel 모터의 관절 전류 변화를 이용한 버튼 접촉 판정
- **동작 검증** : 버튼 조작 후 ON/OFF 상태 확인 및 실패 시 재시도

**핵심 소스코드 ① : 목표 위치 이동 및 보정**

```python
def move_to_target_then_compensate(self, x, y, z, label="target"):
    if not self.move_to_position_only(x, y, z, label=label):
        return {
            "motion_ok": False,
            "contact_detected": False,
            "returned_to_start": False,
        }
    target_xyz = [x, y, z]
    self.compensate_after_move_once(target_xyz, label=label)
    result = self.execute_pose_push(label=label)
    if isinstance(result, dict):
        return result
    return {
        "motion_ok": bool(result),
        "contact_detected": False,
        "returned_to_start": bool(result),
    }
```

**핵심 소스코드 ② : 모터 전류 기반 접촉 감지**

```python
def check_contact_from_current(self, baseline, label="target"):
    if baseline is None:
        return False, None
    i2, i3 = self.get_current_q2_q3_raw()
    if i2 is None or i3 is None:
        return False, None
    d2 = i2 - baseline["q2"]
    d3 = i3 - baseline["q3"]
    contact = (d3 >= self.contact_q3_delta_th) and (abs(d2) >= self.contact_q2_abs_delta_th)
    info = {"i2": i2, "i3": i3, "d2": d2, "d3": d3}
    rospy.loginfo_throttle(0.2, "Current monitor [%s]: q2=%.1f(d=%.1f) q3=%.1f(d=%.1f) contact=%s",
                           label, i2, d2, i3, d3, str(contact))
    return contact, info
```
