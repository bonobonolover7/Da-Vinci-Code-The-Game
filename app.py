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
            st.session_state.player_names = ['나 (User)', '알파봇 1', '알파봇 2', '알파봇 3']
            st.session_state.players = {name: [] for name in st.session_state.player_names}
            st.session_state.turn_idx = 0
            st.session_state.log = ["🎮 시스템: AI가 당신의 수순을 완벽하게 읽고 있습니다."]
            st.session_state.status_msg = "게임을 시작합니다!"
            st.session_state.status_type = "info"

            for name in st.session_state.player_names:
                for _ in range(6):
                    st.session_state.players[name].append(st.session_state.deck.pop())
                st.session_state.players[name].sort(key=lambda x: (int(x['value']), 0 if x['color'] == 'B' else 1))

    @staticmethod
    def ai_ultra_think(bot_name):
        # 봇이 아는 정보 (자기 패 + 이미 까진 패)
        known_pool = []
        for name, hand in st.session_state.players.items():
            for t in hand:
                if name == bot_name or t['revealed']:
                    known_pool.append(f"{t['color']}{t['value']}")

        targets = [n for n in st.session_state.player_names if n != bot_name]
        living_targets = [n for n in targets if any(not t['revealed'] for t in st.session_state.players[n])]
        
        if not living_targets: return None, None, None, ""

        best_move = None
        min_candidates_count = 100

        for t_p in living_targets:
            hand = st.session_state.players[t_p]
            for idx, tile in enumerate(hand):
                if tile['revealed']: continue
                
                # 범위 계산 (정렬 기반)
                min_v, max_v = -1, 12
                for i in range(idx - 1, -1, -1):
                    if hand[i]['revealed']: min_v = int(hand[i]['value']); break
                for i in range(idx + 1, len(hand)):
                    if hand[i]['revealed']: max_v = int(hand[i]['value']); break
                
                # 가능한 숫자들 필터링
                candidates = [str(v) for v in range(min_v + 1, max_v) 
                              if f"{tile['color']}{v}" not in known_pool]
                
                if candidates:
                    # 후보가 적을수록(즉, 확신이 높을수록) 우선순위 상승
                    if len(candidates) < min_candidates_count:
                        min_candidates_count = len(candidates)
                        best_move = (t_p, idx, random.choice(candidates), f"확률 {100//len(candidates)}%")
                    if len(candidates) == 1: break # 100% 정답 발견 시 중단
            if min_candidates_count == 1: break

        return best_move if best_move else (None, None, None, "")

    @staticmethod
    def handle_guess(attacker, defender, idx, val):
        target_tile = st.session_state.players[defender][idx]
        if target_tile['value'] == val:
            target_tile['revealed'] = True
            msg = f"🟢 정답입니다! {attacker}가 {defender}의 {idx+1}번 타일을 맞췄습니다."
            st.session_state.status_msg = msg
            st.session_state.status_type = "success"
            st.session_state.log.insert(0, msg)
            return True
        else:
            msg = f"🔴 틀렸습니다! {attacker}가 {defender}의 {idx+1}번을 {val}(으)로 추리했습니다."
            st.session_state.status_msg = msg
            st.session_state.status_type = "error"
            st.session_state.log.insert(0, msg)
            return False

# ==========================================
# 2. UI 렌더링
# ==========================================
st.set_page_config(page_title="Davinci Code Pro", layout="wide")
DavinciCodeLogic.init_game()

st.markdown("""
    <style>
    .tile-container { display: flex; gap: 8px; justify-content: center; padding: 10px; }
    .tile {
        width: 45px; height: 70px; border-radius: 6px;
        display: flex; align-items: center; justify-content: center;
        font-size: 22px; font-weight: bold; border: 2px solid #333;
    }
    .B { background: #222; color: white; }
    .W { background: #fff; color: #222; }
    .revealed { border: 3px solid #FF4B4B !important; color: #FF4B4B !important; background: #ffebeb; }
    .turn-box { border: 2px solid #00FFAA; background: rgba(0, 255, 170, 0.05); border-radius: 10px; padding: 10px; }
    </style>
""", unsafe_allow_html=True)

if st.session_state.status_type == "success": st.success(st.session_state.status_msg)
elif st.session_state.status_type == "error": st.error(st.session_state.status_msg)
else: st.info(st.session_state.status_msg)

# 보드 출력
for name in st.session_state.player_names:
    is_me = (name == '나 (User)')
    is_curr = (name == st.session_state.player_names[st.session_state.turn_idx])
    
    if is_curr: st.markdown('<div class="turn-box">', unsafe_allow_html=True)
    c1, c2 = st.columns([1, 5])
    c1.markdown(f"#### {'⭐' if is_curr else ''} {name}")
    
    with c2:
        cols = st.columns(12)
        for i, t in enumerate(st.session_state.players[name]):
            rev = "revealed" if t['revealed'] else ""
            val = t['value'] if (t['revealed'] or is_me) else "?"
            cols[i].markdown(f'<div class="tile {t["color"]} {rev}">{val}</div>', unsafe_allow_html=True)
    if is_curr: st.markdown('</div>', unsafe_allow_html=True)

st.divider()

# ==========================================
# 3. 컨트롤 섹션 (오류 수정됨)
# ==========================================
curr_player = st.session_state.player_names[st.session_state.turn_idx]

if curr_player == '나 (User)':
    st.subheader("🎯 내 차례")
    col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
    with col1:
        target_p = st.selectbox("공격 대상", [n for n in st.session_state.player_names if n != '나 (User)'])
    with col2:
        available_indices = [i for i, t in enumerate(st.session_state.players[target_p]) if not t['revealed']]
        t_idx = st.selectbox("타일 위치", available_indices, format_func=lambda x: f"{x+1}번 타일") if available_indices else None
    with col3:
        guess_v = st.text_input("숫자")
    with col4:
        st.write("")
        if st.button("추리 제출", use_container_width=True) and t_idx is not None:
            if guess_v.isdigit():
                hit = DavinciCodeLogic.handle_guess('나 (User)', target_p, t_idx, guess_v)
                if not hit: st.session_state.turn_idx = (st.session_state.turn_idx + 1) % 4
                st.rerun()
else:
    st.subheader(f"🤖 {curr_player} 차례")
    if st.button(f"{curr_player} 행동 실행", use_container_width=True):
        res = DavinciCodeLogic.ai_ultra_think(curr_player)
        if res[0]:
            target_p, t_idx, g_val, reason = res
            # 오류 지점 수정: curr_name 대신 curr_player 사용
            st.session_state.log.insert(0, f"🧠 {curr_player} 분석: {target_p}의 {t_idx+1}번은 {g_val} ({reason})")
            hit = DavinciCodeLogic.handle_guess(curr_player, target_p, t_idx, g_val)
            if not hit: st.session_state.turn_idx = (st.session_state.turn_idx + 1) % 4
            st.rerun()

with st.sidebar:
    st.title("🛡️ 로그")
    for l in st.session_state.log[:15]: st.caption(l)
    if st.button("🔄 리셋"):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()
