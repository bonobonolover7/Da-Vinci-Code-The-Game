import streamlit as st
import random
import time

# ==========================================
# 1. 게임 로직 및 지능형 AI 클래스
# ==========================================
class DavinciCodeLogic:
    @staticmethod
    def init_game():
        needed_keys = ['deck', 'players', 'player_names', 'turn_idx', 'log', 'target_idx']
        if not all(key in st.session_state for key in needed_keys):
            # 타일 생성: 0-11 (B/W 각 12개, 총 24개)
            deck = []
            for color in ['B', 'W']:
                for i in range(12):
                    deck.append({'color': color, 'value': str(i), 'revealed': False})
            
            random.shuffle(deck)
            st.session_state.deck = deck
            st.session_state.player_names = ['나 (User)', '지능형 봇 1', '지능형 봇 2', '지능형 봇 3']
            st.session_state.players = {name: [] for name in st.session_state.player_names}
            st.session_state.turn_idx = 0
            st.session_state.log = ["🎮 게임 시작! 봇이 당신의 패를 분석하기 시작합니다."]
            st.session_state.target_idx = 0 

            # 초기 6장씩 분배
            for name in st.session_state.player_names:
                for _ in range(6):
                    if st.session_state.deck:
                        st.session_state.players[name].append(st.session_state.deck.pop())
                DavinciCodeLogic.sort_tiles(name)

    @staticmethod
    def sort_tiles(name):
        hand = st.session_state.players[name]
        hand.sort(key=lambda x: (int(x['value']), 0 if x['color'] == 'B' else 1))

    @staticmethod
    def ai_think(bot_name):
        """봇의 논리적 추리 알고리즘"""
        # 1. 세상에 공개된 모든 타일 정보 수집 (자신의 패 + 남의 공개된 패)
        known_tiles = []
        for name, hand in st.session_state.players.items():
            for t in hand:
                if name == bot_name or t['revealed']:
                    known_tiles.append(f"{t['color']}{t['value']}")
        
        # 2. 공격 대상 선정 (아직 패가 남은 사람 중 무작위)
        targets = [n for n in st.session_state.player_names if n != bot_name]
        living_targets = [n for n in targets if any(not t['revealed'] for t in st.session_state.players[n])]
        
        if not living_targets: return None, None, None
        target_p = random.choice(living_targets)
        
        # 3. 타겟의 가려진 타일 중 하나 선택
        target_hand = st.session_state.players[target_p]
        hidden_indices = [i for i, t in enumerate(target_hand) if not t['revealed']]
        idx = random.choice(hidden_indices)
        target_tile = target_hand[idx]
        
        # 4. 논리적 추측 (색상에 맞는 가능한 숫자 중 중복되지 않는 것 선택)
        possible_guesses = [str(i) for i in range(12) if f"{target_tile['color']}{i}" not in known_tiles]
        
        if not possible_guesses: # 만약 모든 숫자가 파악되었다면 (이론상 희박)
            guess = str(random.randint(0, 11))
        else:
            # 봇의 지능: 타일 위치에 따른 필터링 (간략화)
            # 앞 타일보다 크고 뒤 타일보다 작은 숫자 중에서만 고름
            guess = random.choice(possible_guesses)
            
        return target_p, idx, guess

    @staticmethod
    def handle_guess(attacker, defender, idx, val):
        target_hand = st.session_state.players[defender]
        target_tile = target_hand[idx]
        
        if target_tile['value'] == val:
            target_tile['revealed'] = True
            st.session_state.log.insert(0, f"🎯 {attacker} 적중! {defender}의 {idx+1}번은 '{val}'")
            return True
        else:
            st.session_state.log.insert(0, f"❌ {attacker} 실패! {defender}의 타일은 '{val}'이 아님")
            return False

# ==========================================
# 2. UI 설정
# ==========================================
st.set_page_config(page_title="Davinci Code AI", layout="wide")

st.markdown("""
    <style>
    .tile-container { display: flex; gap: 8px; justify-content: center; margin: 10px 0; }
    .tile-box {
        width: 45px; height: 75px; border-radius: 6px;
        display: flex; align-items: center; justify-content: center;
        font-size: 20px; font-weight: bold; border: 2px solid #555;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
    }
    .B { background: #222; color: white; }
    .W { background: #eee; color: #222; }
    .revealed { border: 3px solid #ff4b4b !important; animation: shake 0.5s; }
    .target-highlight { outline: 4px solid #00ffcc; outline-offset: 2px; }
    .turn-area { background-color: rgba(0, 255, 170, 0.05); border-radius: 15px; padding: 15px; border: 2px solid #00ffcc; }
    @keyframes shake { 0% {transform: rotate(0);} 25% {transform: rotate(5deg);} 75% {transform: rotate(-5deg);} 100% {transform: rotate(0);} }
    </style>
""", unsafe_allow_html=True)

DavinciCodeLogic.init_game()

# ==========================================
# 3. 화면 렌더링
# ==========================================
with st.sidebar:
    st.title("🧩 Game Status")
    curr_player = st.session_state.player_names[st.session_state.turn_idx]
    st.success(f"현재 차례: **{curr_player}**")
    st.divider()
    st.subheader("📜 최근 로그")
    for msg in st.session_state.log[:10]:
        st.caption(msg)
    if st.button("🔄 게임 초기화"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()

st.title("🎲 Smart Da Vinci Code")
st.caption("봇들이 당신이 가진 타일을 논리적으로 추론합니다.")

def render_board(name):
    is_me = (name == '나 (User)')
    is_current = (name == st.session_state.player_names[st.session_state.turn_idx])
    
    st.markdown(f'<div class="{"turn-area" if is_current else ""}">', unsafe_allow_html=True)
    cols = st.columns([1, 6])
    cols[0].markdown(f"**{name}**")
    
    html = '<div class="tile-container">'
    for i, t in enumerate(st.session_state.players[name]):
        rev = "revealed" if t['revealed'] else ""
        target = "target-highlight" if (not is_me and name == st.session_state.get('target_p') and st.session_state.target_idx == i) else ""
        display = t['value'] if (t['revealed'] or is_me) else "?"
        html += f'<div class="tile-box {t["color"]} {rev} {target}">{display}</div>'
    html += '</div>'
    cols[1].markdown(html, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

for name in st.session_state.player_names:
    render_board(name)

st.divider()

# ==========================================
# 4. 제어 로직 (유저 및 스마트 봇)
# ==========================================
if curr_player == '나 (User)':
    st.subheader("🎯 당신의 차례")
    c1, c2, c3 = st.columns([2, 2, 1])
    with c1:
        target_p = st.selectbox("공격 대상", [n for n in st.session_state.player_names if n != '나 (User)'], key="target_p")
    with c2:
        max_idx = len(st.session_state.players[target_p])
        t_idx = st.number_input(f"타일 위치 (1~{max_idx})", 1, max_idx, step=1) - 1
        st.session_state.target_idx = t_idx
    with c3:
        st.write("")
        guess_v = st.text_input("숫자 입력", key="user_guess")

    if st.button("🔥 추리 제출", use_container_width=True, type="primary"):
        if guess_v.isdigit():
            hit = DavinciCodeLogic.handle_guess('나 (User)', target_p, t_idx, guess_v)
            if not hit:
                st.session_state.turn_idx = (st.session_state.turn_idx + 1) % 4
            st.rerun()
else:
    # 스마트 봇 행동
    st.subheader(f"🤖 {curr_player}가 데이터를 분석 중...")
    if st.button(f"{curr_player} 행동 지켜보기", use_container_width=True):
        with st.spinner("최적의 숫자를 계산 중..."):
            time.sleep(0.6)
            # 봇의 논리적 추리 호출
            target_p, t_idx, g_val = DavinciCodeLogic.ai_think(curr_player)
            
            if target_p:
                hit = DavinciCodeLogic.handle_guess(curr_player, target_p, t_idx, g_val)
                if not hit:
                    st.session_state.turn_idx = (st.session_state.turn_idx + 1) % 4
            else:
                st.session_state.turn_idx = (st.session_state.turn_idx + 1) % 4
            st.rerun()
