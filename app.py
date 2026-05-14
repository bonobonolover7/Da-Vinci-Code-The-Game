import streamlit as st
import random
import time

# ==========================================
# 1. 게임 로직 클래스 (기능 담당)
# ==========================================
class DavinciCodeLogic:
    @staticmethod
    def init_game():
        """게임 초기 데이터 생성 및 세션 저장"""
        # 필수 변수들이 하나라도 없으면 초기화 실행
        needed_keys = ['deck', 'players', 'player_names', 'turn_idx', 'log', 'target_idx']
        if not all(key in st.session_state for key in needed_keys):
            # 타일 생성: 숫자 0-11 (B/W) + 조커(-)
            deck = []
            for color in ['B', 'W']:
                for i in range(12):
                    deck.append({'color': color, 'value': str(i), 'is_joker': False, 'revealed': False})
                deck.append({'color': color, 'value': '-', 'is_joker': True, 'revealed': False})
            
            random.shuffle(deck)
            st.session_state.deck = deck
            
            # 플레이어 설정 (유저 1, 봇 3)
            st.session_state.player_names = ['P1 (User)', 'P2 (Bot)', 'P3 (Bot)', 'P4 (Bot)']
            st.session_state.players = {name: [] for name in st.session_state.player_names}
            st.session_state.turn_idx = 0
            st.session_state.game_over = False
            st.session_state.log = ["🎮 게임이 시작되었습니다!"]
            st.session_state.target_idx = 0 # 유저가 지목할 타일 인덱스

            # 초기 4장씩 분배
            for name in st.session_state.player_names:
                for _ in range(4):
                    st.session_state.players[name].append(st.session_state.deck.pop())
                DavinciCodeLogic.sort_tiles(name)

    @staticmethod
    def sort_tiles(player_name):
        """다빈치 코드 정렬 규칙: 숫자순 -> 검은색 우선 -> 조커는 선택(여기선 뒤로)"""
        hand = st.session_state.players[player_name]
        nums = [t for t in hand if not t['is_joker']]
        jokers = [t for t in hand if t['is_joker']]
        # 숫자는 정수로 변환하여 정렬, 색상은 B(0), W(1) 가중치
        nums.sort(key=lambda x: (int(x['value']), 0 if x['color'] == 'B' else 1))
        st.session_state.players[player_name] = nums + jokers

    @staticmethod
    def handle_guess(attacker, defender, idx, val):
        """추리 성공/실패 판정"""
        target_hand = st.session_state.players[defender]
        
        # 인덱스 범위 초과 방지
        if idx >= len(target_hand):
            return False

        target_tile = target_hand[idx]
        if target_tile['value'] == val:
            target_tile['revealed'] = True
            st.session_state.log.insert(0, f"🎯 {attacker} 적중! {defender}의 {idx+1}번은 '{val}'였습니다.")
            
            # 승리 조건 확인 (상대의 모든 타일이 공개되었는지)
            all_revealed = all(t['revealed'] for t in target_hand)
            if all_revealed:
                st.session_state.log.insert(0, f"💀 {defender} 탈락!")
            return True
        else:
            st.session_state.log.insert(0, f"❌ {attacker} 실패! {defender}의 타일은 '{val}'이 아니었습니다.")
            return False

# ==========================================
# 2. UI 및 그래픽 설정
# ==========================================
st.set_page_config(page_title="Da Vinci Code 4P", layout="wide")

# CSS: 타일 그래픽 및 애니메이션
st.markdown("""
    <style>
    .tile-container { display: flex; gap: 10px; justify-content: center; margin: 15px 0; perspective: 1000px; }
    .tile-box {
        width: 50px; height: 80px;
        border-radius: 8px;
        display: flex; align-items: center; justify-content: center;
        font-size: 22px; font-weight: bold;
        transition: transform 0.3s;
        box-shadow: 3px 3px 10px rgba(0,0,0,0.3);
        border: 2px solid #555;
    }
    .B { background: linear-gradient(145deg, #333, #000); color: white; }
    .W { background: linear-gradient(145deg, #fff, #eee); color: black; }
    .revealed { border: 3px solid #ff4b4b !important; transform: scale(1.05); }
    .target-highlight { outline: 4px solid #00ffcc; outline-offset: 4px; border-radius: 8px; }
    .turn-area { background-color: rgba(76, 175, 80, 0.1); border-radius: 20px; padding: 15px; border: 2px solid #4CAF50; }
    </style>
""", unsafe_allow_html=True)

# 게임 초기화 실행
DavinciCodeLogic.init_game()

# ==========================================
# 3. 메인 화면 렌더링
# ==========================================
with st.sidebar:
    st.title("🧩 Game Status")
    if 'player_names' in st.session_state:
        curr_player = st.session_state.player_names[st.session_state.turn_idx]
        st.success(f"현재 턴: **{curr_player}**")
    
    st.divider()
    st.subheader("📜 로그")
    for msg in st.session_state.log[:8]:
        st.caption(msg)
    
    if st.button("🔄 게임 리셋"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

st.title("🎲 Da Vinci Code : 4-Player Battle")

# 플레이어별 타일 그리기 함수
def render_player_board(name):
    is_user = (name == 'P1 (User)')
    is_current = (name == st.session_state.player_names[st.session_state.turn_idx])
    
    # 현재 턴인 플레이어 강조
    area_class = "turn-area" if is_current else ""
    st.markdown(f'<div class="{area_class}">', unsafe_allow_html=True)
    
    cols = st.columns([1, 5])
    cols[0].markdown(f"### {name}")
    
    tile_html = '<div class="tile-container">'
    for i, t in enumerate(st.session_state.players[name]):
        # UI 강조 로직
        rev_class = "revealed" if t['revealed'] else ""
        # 상대방 타일 지목 시 하이라이트
        target_class = "target-highlight" if (not is_user and name == st.session_state.get('target_p') and st.session_state.target_idx == i) else ""
        
        display_val = t['value'] if (t['revealed'] or is_user) else "?"
        tile_html += f'<div class="tile-box {t["color"]} {rev_class} {target_class}">{display_val}</div>'
    
    tile_html += '</div>'
    cols[1].markdown(tile_html, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# 4명의 보드 출력
for name in st.session_state.player_names:
    render_player_board(name)
    st.write("")

st.divider()

# ==========================================
# 4. 게임 컨트롤 (유저용)
# ==========================================
if 'player_names' in st.session_state:
    if curr_player == 'P1 (User)':
        st.subheader("🎯 당신의 차례입니다! 상대의 타일을 추리하세요.")
        c1, c2, c3 = st.columns([2, 2, 1])
        
        with c1:
            opponents = [n for n in st.session_state.player_names if n != 'P1 (User)']
            target_p = st.selectbox("공격 대상 선택", opponents, key="target_p")
        with c2:
            max_idx = len(st.session_state.players[target_p])
            t_idx = st.number_input(f"{target_p}의 타일 번호 (1~{max_idx})", 1, max_idx, step=1) - 1
            st.session_state.target_idx = t_idx # 하이라이트 연동용
        with c3:
            st.write(" ") # 높이 맞춤
            guess_v = st.text_input("예상 숫자 (또는 -)", key="guess_input")

        if st.button("🔥 추리 제출", use_container_width=True, type="primary"):
            if guess_v:
                hit = DavinciCodeLogic.handle_guess('P1 (User)', target_p, t_idx, guess_v)
                if not hit:
                    # 실패 시 턴 넘기기
                    st.session_state.turn_idx = (st.session_state.turn_idx + 1) % 4
                st.rerun()
            else:
                st.warning("숫자를 입력해주세요!")
    else:
        # 봇의 턴
        st.subheader(f"🤖 {curr_player}가 전략을 세우는 중...")
        if st.button("봇의 행동 진행하기 ➡️", use_container_width=True):
            with st.spinner("봇이 추리 중..."):
                time.sleep(0.8)
                attacker = curr_player
                # 살아있는 상대 중 무작위 선택 (간단한 AI)
                target_p = random.choice([n for n in st.session_state.player_names if n != attacker])
                t_idx = random.randint(0, len(st.session_state.players[target_p])-1)
                g_val = str(random.randint(0, 11))
                
                hit = DavinciCodeLogic.handle_guess(attacker, target_p, t_idx, g_val)
                if not hit:
                    st.session_state.turn_idx = (st.session_state.turn_idx + 1) % 4
                st.rerun()
