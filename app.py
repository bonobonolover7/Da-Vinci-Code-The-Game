import streamlit as st
import random
import time

# ==========================================
# 1. 게임 로직 클래스 (4인용 확장)
# ==========================================
class DavinciCodeLogic:
    @staticmethod
    def init_game():
        if 'deck' not in st.session_state:
            # 타일 생성: 0-11 (B/W) + 조커(-)
            deck = []
            for color in ['B', 'W']:
                for i in range(12):
                    deck.append({'color': color, 'value': str(i), 'is_joker': False, 'revealed': False})
                deck.append({'color': color, 'value': '-', 'is_joker': True, 'revealed': False})
            
            random.shuffle(deck)
            st.session_state.deck = deck
            
            # 4명 플레이어 설정
            st.session_state.players = {
                'P1 (User)': [],
                'P2 (Bot)': [],
                'P3 (Bot)': [],
                'P4 (Bot)': []
            }
            st.session_state.player_names = list(st.session_state.players.keys())
            st.session_state.turn_idx = 0
            st.session_state.game_over = False
            st.session_state.log = ["🎮 게임이 시작되었습니다!"]

            # 각자 4장씩 분배
            for name in st.session_state.player_names:
                for _ in range(4):
                    st.session_state.players[name].append(st.session_state.deck.pop())
                DavinciCodeLogic.sort_tiles(name)

    @staticmethod
    def sort_tiles(player_name):
        hand = st.session_state.players[player_name]
        # 조커와 일반 타일 분리 정렬 (조커는 일단 맨 뒤로)
        nums = [t for t in hand if not t['is_joker']]
        jokers = [t for t in hand if t['is_joker']]
        nums.sort(key=lambda x: (int(x['value']), 0 if x['color'] == 'B' else 1))
        st.session_state.players[player_name] = nums + jokers

    @staticmethod
    def handle_guess(attacker, defender, target_idx, guess_val):
        target_tile = st.session_state.players[defender][target_idx]
        if target_tile['value'] == guess_val:
            target_tile['revealed'] = True
            st.session_state.log.insert(0, f"🎯 {attacker}의 적중! {defender}의 {target_idx+1}번 타일은 '{guess_val}'였습니다.")
            # 승리 확인 로직 등은 간소화
            return True
        else:
            st.session_state.log.insert(0, f"❌ {attacker}의 추리 실패! ({defender}의 타일은 {guess_val}이 아님)")
            return False

# ==========================================
# 2. UI 스타일 정의 (고급화 및 텍스트 오류 방지)
# ==========================================
st.set_page_config(page_title="Davinci Code 4P", layout="wide")

st.markdown("""
    <style>
    .tile-box {
        display: inline-block;
        width: 45px;
        height: 70px;
        margin: 5px;
        border-radius: 8px;
        text-align: center;
        line-height: 70px;
        font-size: 20px;
        font-weight: bold;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
        border: 2px solid #ddd;
    }
    .B { background-color: #333; color: white; }
    .W { background-color: #fff; color: black; }
    .revealed { border: 3px solid #ff4b4b !important; }
    .current-turn { background-color: #e8f4ea; border-radius: 15px; padding: 10px; border-left: 5px solid #4CAF50; }
    </style>
""", unsafe_allow_html=True)

# 초기화
DavinciCodeLogic.init_game()

# ==========================================
# 3. 사이드바 및 상태 표시
# ==========================================
with st.sidebar:
    st.title("🧩 Game Status")
    curr_turn_name = st.session_state.player_names[st.session_state.turn_idx]
    st.success(f"현재 차례: **{curr_turn_name}**")
    
    st.divider()
    st.subheader("📜 히스토리")
    for l in st.session_state.log[:5]:
        st.caption(l)
    
    if st.button("🔄 게임 초기화"):
        del st.session_state['deck']
        st.rerun()

# ==========================================
# 4. 메인 게임 보드 (알잘딱 UI)
# ==========================================
st.title("🎲 Da Vinci Code : 4-Player Battle")

# 타일 렌더링 함수
def draw_tiles(player_name, is_user=False):
    cols = st.columns([1, 4])
    with cols[0]:
        st.markdown(f"**{player_name}**")
    with cols[1]:
        html_tiles = ""
        for i, t in enumerate(st.session_state.players[player_name]):
            rev_class = "revealed" if t['revealed'] else ""
            # 유저 패거나 공개된 패는 숫자를 보여줌
            display_val = t['value'] if (t['revealed'] or is_user) else "?"
            html_tiles += f'<div class="tile-box {t["color"]} {rev_class}">{display_val}</div>'
        st.markdown(html_tiles, unsafe_allow_html=True)

# 모든 플레이어 영역 렌더링
for name in st.session_state.player_names:
    with st.container():
        is_it_me = (name == 'P1 (User)')
        if name == curr_turn_name:
            st.markdown(f'<div class="current-turn">', unsafe_allow_html=True)
            draw_tiles(name, is_user=is_it_me)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            draw_tiles(name, is_user=is_it_me)
        st.write("")

st.divider()

# ==========================================
# 5. 액션 제어 (User 전용)
# ==========================================
if curr_turn_name == 'P1 (User)':
    st.subheader("🎯 내 차례: 추리하기")
    c1, c2, c3 = st.columns(3)
    
    with c1:
        target_p = st.selectbox("공격 대상", [n for n in st.session_state.player_names if n != 'P1 (User)'])
    with c2:
        # 공개되지 않은 타일 인덱스만 선택 가능하도록 구현 가능하나 일단 단순화
        target_idx = st.number_input("대상 타일 번호 (1부터)", min_value=1, max_value=len(st.session_state.players[target_p]), step=1) - 1
    with c3:
        guess_val = st.text_input("숫자 예상 (0~11 또는 -)")

    if st.button("🔥 추리 제출", use_container_width=True):
        if guess_val:
            success = DavinciCodeLogic.handle_guess('P1 (User)', target_p, target_idx, guess_val)
            if not success:
                st.session_state.turn_idx = (st.session_state.turn_idx + 1) % 4
            st.rerun()
else:
    # 봇 턴 (시뮬레이션)
    st.subheader("🤖 봇이 생각 중입니다...")
    if st.button("봇 행동 지켜보기"):
        with st.spinner("봇이 추리 중..."):
            time.sleep(1)
            # 단순 봇 로직: 무작위 공격
            attacker = curr_turn_name
            defender = random.choice([n for n in st.session_state.player_names if n != attacker])
            t_idx = random.randint(0, len(st.session_state.players[defender])-1)
            g_val = str(random.randint(0, 11))
            
            DavinciCodeLogic.handle_guess(attacker, defender, t_idx, g_val)
            st.session_state.turn_idx = (st.session_state.turn_idx + 1) % 4
            st.rerun()
