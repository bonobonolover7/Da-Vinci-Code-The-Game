import streamlit as st
import random
import time

# ==========================================
# 1. 게임 로직 및 상태 관리
# ==========================================
class DavinciCodeLogic:
    @staticmethod
    def init_game():
        needed_keys = ['deck', 'players', 'player_names', 'turn_idx', 'log', 'status_msg', 'status_type', 'drawn_tile']
        if not all(key in st.session_state for key in needed_keys):
            deck = []
            for color in ['B', 'W']:
                for i in range(12):
                    deck.append({'color': color, 'value': str(i), 'is_joker': False, 'revealed': False})
                deck.append({'color': color, 'value': '-', 'is_joker': True, 'revealed': False})
            
            random.shuffle(deck)
            st.session_state.deck = deck
            st.session_state.player_names = ['나 (User)', '봇 1', '봇 2', '봇 3']
            st.session_state.players = {name: [] for name in st.session_state.player_names}
            st.session_state.turn_idx = 0
            st.session_state.log = []
            st.session_state.status_msg = "게임을 시작합니다! 먼저 타일을 하나 뽑으세요."
            st.session_state.status_type = "info" # info, success, error
            st.session_state.drawn_tile = None # 이번 턴에 새로 뽑은 타일
            st.session_state.must_reveal = False # 틀려서 내 타일을 공개해야 하는 상태

            # 초기 3장씩 분배 (4인 플레이 기준)
            for name in st.session_state.player_names:
                for _ in range(3):
                    st.session_state.players[name].append(st.session_state.deck.pop())
                DavinciCodeLogic.sort_tiles(name)

    @staticmethod
    def sort_tiles(name):
        hand = st.session_state.players[name]
        nums = [t for t in hand if not t['is_joker']]
        jokers = [t for t in hand if t['is_joker']]
        nums.sort(key=lambda x: (int(x['value']), 0 if x['color'] == 'B' else 1))
        # 조커는 일단 가장 큰 수 뒤에 배치 (실제 게임에선 위치 선택 가능하지만 로직 단순화)
        st.session_state.players[name] = nums + jokers

# ==========================================
# 2. UI 스타일 및 렌더링
# ==========================================
st.set_page_config(page_title="Da Vinci Code Pro", layout="wide")

st.markdown("""
    <style>
    .tile-container { display: flex; gap: 8px; justify-content: center; margin-bottom: 10px; }
    .tile {
        width: 45px; height: 70px; border-radius: 6px;
        display: flex; align-items: center; justify-content: center;
        font-size: 20px; font-weight: bold; border: 2px solid #555;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
    }
    .B { background: #222; color: white; }
    .W { background: #eee; color: #222; }
    .revealed { border: 3px solid #FF4B4B !important; }
    .my-tile { border: 2px dashed #00FFAA; }
    .turn-box { background: rgba(0, 255, 170, 0.05); border: 1px solid #00FFAA; padding: 10px; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

DavinciCodeLogic.init_game()

# 상단 상태 바 (맞음/틀림 피드백)
if st.session_state.status_type == "success":
    st.success(st.session_state.status_msg)
elif st.session_state.status_type == "error":
    st.error(st.session_state.status_msg)
else:
    st.info(st.session_state.status_msg)

# ==========================================
# 3. 게임 보드 출력
# ==========================================
def render_board():
    for name in st.session_state.player_names:
        is_me = (name == '나 (User)')
        is_current = (st.session_state.player_names[st.session_state.turn_idx] == name)
        
        with st.container():
            if is_current: st.markdown('<div class="turn-box">', unsafe_allow_html=True)
            
            col1, col2 = st.columns([1, 5])
            col1.subheader(f"{'⭐ ' if is_current else ''}{name}")
            
            html = '<div class="tile-container">'
            for i, t in enumerate(st.session_state.players[name]):
                rev = "revealed" if t['revealed'] else ""
                # 내 패는 ?로 보이지만 안에 숫자 표시 (실제 다빈치 코드 느낌)
                if is_me:
                    val = t['value']
                    display = f'<div class="tile {t["color"]} {rev} my-tile">{val}</div>'
                else:
                    val = t['value'] if t['revealed'] else "?"
                    display = f'<div class="tile {t["color"]} {rev}">{val}</div>'
                html += display
            html += '</div>'
            col2.markdown(html, unsafe_allow_html=True)
            
            if is_current: st.markdown('</div>', unsafe_allow_html=True)
        st.write("")

render_board()

# ==========================================
# 4. 게임 컨트롤 로직
# ==========================================
st.divider()
curr_name = st.session_state.player_names[st.session_state.turn_idx]

# --- USER TURN ---
if curr_name == '나 (User)':
    # 1. 타일 뽑기 단계
    if st.session_state.drawn_tile is None and not st.session_state.must_reveal:
        if st.button("🎴 타일 하나 뽑기"):
            if st.session_state.deck:
                new_tile = st.session_state.deck.pop()
                st.session_state.players['나 (User)'].append(new_tile)
                st.session_state.drawn_tile = new_tile
                DavinciCodeLogic.sort_tiles('나 (User)')
                st.session_state.status_msg = "타일을 뽑았습니다. 이제 상대방의 숫자를 추리하세요!"
                st.session_state.status_type = "info"
                st.rerun()

    # 2. 추리 실패 시 내 타일 공개 선택 단계
    elif st.session_state.must_reveal:
        st.warning("추리에 실패했습니다! 공개할 내 타일을 선택하세요.")
        my_unrevealed = [i for i, t in enumerate(st.session_state.players['나 (User)']) if not t['revealed']]
        selected_to_reveal = st.radio("공개할 타일 번호:", my_unrevealed, format_func=lambda x: f"{x+1}번 타일 ({st.session_state.players['나 (User)'][x]['value']})", horizontal=True)
        
        if st.button("선택한 타일 공개하고 턴 넘기기"):
            st.session_state.players['나 (User)'][selected_to_reveal]['revealed'] = True
            st.session_state.must_reveal = False
            st.session_state.drawn_tile = None
            st.session_state.turn_idx = (st.session_state.turn_idx + 1) % 4
            st.session_state.status_msg = "봇의 차례입니다."
            st.session_state.status_type = "info"
            st.rerun()

    # 3. 추리 단계
    elif st.session_state.drawn_tile is not None:
        c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
        target_p = c1.selectbox("공격 대상", [n for n in st.session_state.player_names if n != '나 (User)'])
        target_idx = c2.number_input("몇 번째 타일?", 1, len(st.session_state.players[target_p]), step=1) - 1
        guess_val = c3.text_input("예상 숫자/조커(-)")
        
        if c4.button("🔥 추리!!", use_container_width=True):
            target_tile = st.session_state.players[target_p][target_idx]
            if target_tile['value'] == guess_val:
                target_tile['revealed'] = True
                st.session_state.status_msg = "🟢 정답입니다! 한 번 더 추리하거나 턴을 마칠 수 있습니다."
                st.session_state.status_type = "success"
                # 정답 시 drawn_tile을 유지하여 계속 추리 가능하게 함
                st.rerun()
            else:
                st.session_state.status_msg = "🔴 틀렸습니다! 패널티로 내 타일을 하나 공개해야 합니다."
                st.session_state.status_type = "error"
                st.session_state.must_reveal = True
                st.rerun()
        
        if st.button("턴 종료 (추리 중단)"):
            st.session_state.drawn_tile = None
            st.session_state.turn_idx = (st.session_state.turn_idx + 1) % 4
            st.rerun()

# --- BOT TURN (자동 실행) ---
else:
    st.subheader(f"🤖 {curr_name}가 생각 중...")
    time.sleep(1.5) # 봇 행동 지연 (시각적 효과)
    
    # 봇은 무조건 타일을 하나 뽑음
    if st.session_state.deck:
        new_tile = st.session_state.deck.pop()
        st.session_state.players[curr_name].append(new_tile)
        DavinciCodeLogic.sort_tiles(curr_name)
    
    # 무작위 추리
    attacker = curr_name
    defender = random.choice([n for n in st.session_state.player_names if n != attacker])
    unrevealed_indices = [i for i, t in enumerate(st.session_state.players[defender]) if not t['revealed']]
    
    if unrevealed_indices:
        t_idx = random.choice(unrevealed_indices)
        g_val = str(random.randint(0, 11))
        
        if st.session_state.players[defender][t_idx]['value'] == g_val:
            st.session_state.players[defender][t_idx]['revealed'] = True
            st.session_state.status_msg = f"🤖 {attacker}가 {defender}의 {t_idx+1}번 타일을 맞췄습니다!"
            st.session_state.status_type = "error" if defender == '나 (User)' else "info"
        else:
            # 봇 추리 실패 시 봇의 타일 중 하나 랜덤 공개
            bot_unrevealed = [i for i, t in enumerate(st.session_state.players[attacker]) if not t['revealed']]
            if bot_unrevealed:
                st.session_state.players[attacker][random.choice(bot_unrevealed)]['revealed'] = True
            st.session_state.status_msg = f"🤖 {attacker}의 추리가 틀렸습니다."
            st.session_state.status_type = "info"

    # 턴 종료
    st.session_state.turn_idx = (st.session_state.turn_idx + 1) % 4
    st.rerun()
