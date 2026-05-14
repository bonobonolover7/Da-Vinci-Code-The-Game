import streamlit as st
import random
import time

# ==========================================
# 1. 게임 로직 및 초정밀 AI
# ==========================================
class DavinciCodeLogic:
    @staticmethod
    def init_game():
        if 'deck' not in st.session_state:
            deck = []
            for color in ['B', 'W']:
                for i in range(12):
                    deck.append({'color': color, 'value': str(i), 'revealed': False})
            random.shuffle(deck)
            st.session_state.deck = deck
            st.session_state.player_names = ['나 (User)', '봇 1', '봇 2', '봇 3']
            st.session_state.players = {name: [] for name in st.session_state.player_names}
            st.session_state.turn_idx = 0
            st.session_state.log = ["🎮 게임 시작!"]
            st.session_state.status_msg = "게임을 시작합니다!"
            st.session_state.status_type = "info"

            for name in st.session_state.player_names:
                for _ in range(6):
                    st.session_state.players[name].append(st.session_state.deck.pop())
                st.session_state.players[name].sort(key=lambda x: (int(x['value']), 0 if x['color'] == 'B' else 1))

    @staticmethod
    def ai_smart_think(bot_name):
        # 1. 모든 정보 수집
        known_numbers = []
        for name, hand in st.session_state.players.items():
            for t in hand:
                if name == bot_name or t['revealed']:
                    known_numbers.append(f"{t['color']}{t['value']}")

        # 2. 타겟 설정 (아직 안 까진 타일이 있는 사람)
        targets = [n for n in st.session_state.player_names if n != bot_name]
        living_targets = [n for n in targets if any(not t['revealed'] for t in st.session_state.players[n])]
        if not living_targets: return None, None, None, ""
        
        target_p = random.choice(living_targets)
        hand = st.session_state.players[target_p]
        hidden_indices = [i for i, t in enumerate(hand) if not t['revealed']]
        
        # 3. 모든 가려진 타일 검토 (가장 확신 드는 타일 찾기)
        best_idx = hidden_indices[0]
        best_guess = "0"
        best_reason = "찍기"
        
        for idx in hidden_indices:
            target_tile = hand[idx]
            min_v, max_v = -1, 12
            for i in range(idx - 1, -1, -1):
                if hand[i]['revealed']: min_v = int(hand[i]['value']); break
            for i in range(idx + 1, len(hand)):
                if hand[i]['revealed']: max_v = int(hand[i]['value']); break
            
            # 후보군 필터링
            candidates = [str(v) for v in range(min_v + 1, max_v) if f"{target_tile['color']}{v}" not in known_numbers]
            
            if candidates:
                best_idx = idx
                best_guess = random.choice(candidates)
                best_reason = f"확률 {100//len(candidates)}%"
                if len(candidates) == 1: # 100% 확신 시 즉시 결정
                    break

        return target_p, best_idx, best_guess, best_reason

    @staticmethod
    def handle_guess(attacker, defender, idx, val):
        target_tile = st.session_state.players[defender][idx]
        if target_tile['value'] == val:
            target_tile['revealed'] = True
            st.session_state.status_msg = f"🟢 정답입니다! {attacker}가 {defender}의 {idx+1}번을 맞췄습니다."
            st.session_state.status_type = "success"
            st.session_state.log.insert(0, st.session_state.status_msg)
            return True
        else:
            st.session_state.status_msg = f"🔴 틀렸습니다! {attacker}가 {defender}의 {idx+1}번을 {val}(으)로 틀림."
            st.session_state.status_type = "error"
            st.session_state.log.insert(0, st.session_state.status_msg)
            return False

# ==========================================
# 2. UI 설정
# ==========================================
st.set_page_config(page_title="Davinci Code Pro", layout="wide")
DavinciCodeLogic.init_game()

st.markdown("""
    <style>
    .tile-row { display: flex; gap: 10px; align-items: center; padding: 10px; border-bottom: 1px solid #eee; }
    .tile-box {
        width: 40px; height: 65px; border-radius: 5px;
        display: flex; align-items: center; justify-content: center;
        font-size: 18px; font-weight: bold; border: 2px solid #555;
    }
    .B { background: #222; color: white; }
    .W { background: #eee; color: #222; }
    .revealed { border: 3px solid #FF4B4B !important; }
    .turn-area { border: 2px solid #00FFAA; background: rgba(0, 255, 170, 0.05); border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

# 피드백 메시지 바
if st.session_state.status_type == "success": st.success(st.session_state.status_msg)
elif st.session_state.status_type == "error": st.error(st.session_state.status_msg)
else: st.info(st.session_state.status_msg)

# ==========================================
# 3. 게임판 출력 (정렬 고정)
# ==========================================
for name in st.session_state.player_names:
    is_me = (name == '나 (User)')
    is_curr = (name == st.session_state.player_names[st.session_state.turn_idx])
    
    st.markdown(f'<div class="{"turn-area" if is_curr else ""}">', unsafe_allow_html=True)
    c1, c2 = st.columns([1, 5])
    c1.markdown(f"#### {'⭐' if is_curr else ''} {name}")
    
    html = '<div class="tile-row">'
    for i, t in enumerate(st.session_state.players[name]):
        rev = "revealed" if t['revealed'] else ""
        val = t['value'] if (t['revealed'] or is_me) else "?"
        html += f'<div class="tile-box {t["color"]} {rev}">{val}</div>'
    html += '</div>'
    c2.markdown(html, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.divider()

# ==========================================
# 4. 컨트롤 (중복 추리 차단)
# ==========================================
curr_name = st.session_state.player_names[st.session_state.turn_idx]

if curr_name == '나 (User)':
    st.subheader("🎯 내 차례")
    col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
    
    with col1:
        target_p = st.selectbox("공격 대상", [n for n in st.session_state.player_names if n != '나 (User)'])
    with col2:
        # 이미 맞춰진 타일은 제외하고 선택 가능하게 수정
        available_indices = [i for i, t in enumerate(st.session_state.players[target_p]) if not t['revealed']]
        if available_indices:
            t_idx = st.selectbox("타일 번호 선택", available_indices, format_func=lambda x: f"{x+1}번 타일")
        else:
            st.write("모든 타일이 공개됨")
            t_idx = None
    with col3:
        guess_v = st.text_input("숫자(0-11)")
    
    with col4:
        st.write("") # 간격 맞춤
        if st.button("🔥 추리", use_container_width=True) and t_idx is not None:
            if guess_v.isdigit():
                hit = DavinciCodeLogic.handle_guess('나 (User)', target_p, t_idx, guess_v)
                if not hit: st.session_state.turn_idx = (st.session_state.turn_idx + 1) % 4
                st.rerun()

else:
    st.subheader(f"🤖 {curr_name}가 생각 중...")
    if st.button(f"{curr_name} 행동 진행", use_container_width=True):
        time.sleep(0.5)
        target_p, t_idx, g_val, reason = DavinciCodeLogic.ai_smart_think(curr_name)
        if target_p:
            st.session_state.log.insert(0, f"🧠 {curr_name} 분석: {target_p}의 {t_idx+1}번은 {g_val} ({reason})")
            hit = DavinciCodeLogic.handle_guess(curr_name, target_p, t_idx, g_val)
            if not hit: st.session_state.turn_idx = (st.session_state.turn_idx + 1) % 4
            st.rerun()

with st.sidebar:
    st.title("📜 로그")
    for l in st.session_state.log[:20]: st.caption(l)
    if st.button("🔄 리셋"):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()
