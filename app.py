import streamlit as st
import random
import time

# ==========================================
# 1. 게임 로직 및 초정밀 '메모리' AI
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
            st.session_state.wrong_guesses = [] # 🔥 [중요] 오답 메모리 저장소
            st.session_state.turn_idx = 0
            st.session_state.log = ["🎮 시스템: 환영합니다!"]
            st.session_state.status_msg = "게임을 시작합니다!"
            st.session_state.status_type = "info"

            for name in st.session_state.player_names:
                for _ in range(6):
                    st.session_state.players[name].append(st.session_state.deck.pop())
                st.session_state.players[name].sort(key=lambda x: (int(x['value']), 0 if x['color'] == 'B' else 1))

    @staticmethod
    def ai_ultra_think(bot_name):
        """본인 패 + 공개 패 + 모든 플레이어의 오답 기록을 종합 분석"""
        # 1. 확정된 정보 (내 패 + 공개된 타일들)
        known_pool = []
        for name, hand in st.session_state.players.items():
            for t in hand:
                if name == bot_name or t['revealed']:
                    known_pool.append(f"{t['color']}{t['value']}")

        targets = [n for n in st.session_state.player_names if n != bot_name]
        living_targets = [n for n in targets if any(not t['revealed'] for t in st.session_state.players[n])]
        if not living_targets: return None
        
        best_moves = []
        for t_p in living_targets:
            hand = st.session_state.players[t_p]
            for idx, tile in enumerate(hand):
                if tile['revealed']: continue
                
                # 범위 계산
                min_v, max_v = -1, 12
                for i in range(idx - 1, -1, -1):
                    if hand[i]['revealed']: min_v = int(hand[i]['value']); break
                for i in range(idx + 1, len(hand)):
                    if hand[i]['revealed']: max_v = int(hand[i]['value']); break
                
                # 🔥 종합 분석 시작
                candidates = []
                for v in range(min_v + 1, max_v):
                    val_str = str(v)
                    # 조건 A: 내 눈에 안 보이고 바닥에도 없는 숫자인가?
                    if f"{tile['color']}{val_str}" in known_pool: continue
                    
                    # 조건 B: 누군가 이 타일을 이 숫자로 찍어서 틀린 적이 있는가? (오답 메모리 체크)
                    already_guessed_wrong = False
                    for (prev_target, prev_idx, prev_val) in st.session_state.wrong_guesses:
                        if prev_target == t_p and prev_idx == idx and prev_val == val_str:
                            already_guessed_wrong = True
                            break
                    
                    if not already_guessed_wrong:
                        candidates.append(val_str)

                if candidates:
                    best_moves.append({
                        'target': t_p, 'idx': idx, 
                        'guess': random.choice(candidates), 
                        'count': len(candidates),
                        'candidates': candidates
                    })
        
        if not best_moves: return None
        # 가장 확률 높은(후보가 적은) 공격 대상을 선택
        best_moves.sort(key=lambda x: x['count'])
        return best_moves[0]

    @staticmethod
    def handle_guess(attacker, defender, idx, val):
        target_tile = st.session_state.players[defender][idx]
        if target_tile['value'] == val:
            target_tile['revealed'] = True
            msg = f"🟢 정답! {attacker} → {defender} [{idx+1}번: {val}]"
            st.session_state.status_msg = msg
            st.session_state.status_type = "success"
            st.session_state.log.insert(0, msg)
            return True
        else:
            # 🔥 오답을 메모리에 기록
            st.session_state.wrong_guesses.append((defender, idx, val))
            msg = f"🔴 오답! {attacker}의 추리 실패."
            st.session_state.status_msg = msg
            st.session_state.status_type = "error"
            st.session_state.log.insert(0, f"🔴 오답! {attacker} → {defender} [{idx+1}번을 {val}로 추측]")
            
            # 페널티: 본인 패 공개
            hidden_indices = [i for i, t in enumerate(st.session_state.players[attacker]) if not t['revealed']]
            if hidden_indices:
                p_idx = random.choice(hidden_indices)
                st.session_state.players[attacker][p_idx]['revealed'] = True
                st.session_state.log.insert(0, f"⚠️ 페널티: {attacker}의 {p_idx+1}번({st.session_state.players[attacker][p_idx]['value']}) 공개")
            return False

# ==========================================
# 2. UI 및 정렬 (HTML 고정)
# ==========================================
st.set_page_config(page_title="Davinci Code: Genius AI", layout="wide")
DavinciCodeLogic.init_game()

st.markdown("""
    <style>
    .player-row { display: flex; align-items: center; padding: 15px; margin-bottom: 8px; border-radius: 12px; background: white; border: 1px solid #ddd; }
    .active-row { border: 2px solid #00FFAA !important; background: #f0fffb !important; }
    .name-tag { width: 130px; font-weight: bold; }
    .tile-list { display: flex; gap: 8px; }
    .tile { width: 42px; height: 62px; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-size: 20px; font-weight: bold; border: 2px solid #444; }
    .B { background: #222; color: white; }
    .W { background: #fff; color: #222; }
    .revealed { border-color: #FF4B4B !important; color: #FF4B4B !important; background: #ffebeb; }
    </style>
""", unsafe_allow_html=True)

if st.session_state.status_type == "success": st.success(st.session_state.status_msg)
elif st.session_state.status_type == "error": st.error(st.session_state.status_msg)
else: st.info(st.session_state.status_msg)

for name in st.session_state.player_names:
    is_me = (name == '나 (User)')
    is_curr = (name == st.session_state.player_names[st.session_state.turn_idx])
    row_class = "player-row active-row" if is_curr else "player-row"
    
    html = f'<div class="{row_class}"><div class="name-tag">{"⭐" if is_curr else ""}{name}</div><div class="tile-list">'
    for i, t in enumerate(st.session_state.players[name]):
        rev = "revealed" if t['revealed'] else ""
        val = t['value'] if (t['revealed'] or is_me) else "?"
        html += f'<div class="tile {t["color"]} {rev}">{val}</div>'
    html += '</div></div>'
    st.markdown(html, unsafe_allow_html=True)

st.divider()

# ==========================================
# 3. 조작 및 턴 제어
# ==========================================
curr_p = st.session_state.player_names[st.session_state.turn_idx]

if curr_p == '나 (User)':
    c1, c2, c3, c4 = st.columns([2, 2, 1, 1])
    with c1:
        target_p = st.selectbox("공격 대상", [n for n in st.session_state.player_names if n != '나 (User)'])
    with c2:
        avail = [i for i, t in enumerate(st.session_state.players[target_p]) if not t['revealed']]
        t_idx = st.selectbox("타일 위치", avail, format_func=lambda x: f"{x+1}번") if avail else None
    with c3:
        guess_v = st.text_input("숫자")
    with c4:
        st.write("")
        if st.button("추리!", use_container_width=True) and t_idx is not None:
            DavinciCodeLogic.handle_guess('나 (User)', target_p, t_idx, guess_v.strip())
            st.session_state.turn_idx = (st.session_state.turn_idx + 1) % 4
            st.rerun()
else:
    st.subheader(f"🤖 {curr_p}가 뇌 풀가동 중...")
    if st.button(f"{curr_p} 행동 진행", use_container_width=True):
        move = DavinciCodeLogic.ai_ultra_think(curr_p)
        if move:
            st.session_state.log.insert(0, f"🧠 {curr_p} 추론: {move['target']}의 {move['idx']+1}번 후보 {move['candidates']} 중 '{move['guess']}' 선택")
            DavinciCodeLogic.handle_guess(curr_p, move['target'], move['idx'], move['guess'])
        st.session_state.turn_idx = (st.session_state.turn_idx + 1) % 4
        st.rerun()

with st.sidebar:
    st.title("📑 메모리 센터")
    st.write("**오답 기록 (봇이 참고함):**")
    for (t, i, v) in st.session_state.wrong_guesses[-10:]:
        st.caption(f"- {t}의 {i+1}번은 {v}가 아님")
    st.divider()
    for l in st.session_state.log[:15]: st.caption(l)
    if st.button("🔄 리셋"):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()
